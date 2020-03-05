# eva bacas, 3.4.19
# this file defines the NameObj, PubName, and PersonName classes

# import necessary packages
import re
import pickle
from symspellpy.symspellpy import SymSpell, Verbosity
from nltk.metrics import edit_distance

# create list of titles
titles = """Doctor,Dr,Mr,Mrs,Miss,Msgr,Monsignor,Rev,Reverend,Hon,Honorable,Honourable,Prof,Professor,Madame,Madam,Lady,Lord,Sir,Dame,Master,Mistress,Princess,Prince,Duke,Duchess,Baron,Father,Chancellor,Principal,President,Pres,Warden,Dean,Regent,Rector,Provost,Director
"""
titles = titles.rstrip().split(',')

# create title gender dict
title_gender_dict = {}
w_list = ['Mrs','Miss','Madame','Madam','Lady','Dame','Mistress','Princess','Duchess']
for x in titles:
    if x in w_list:
        title_gender_dict[x.lower()] = 'F'
    else:
        title_gender_dict[x.lower()] = 'M'

# import symspell dictionaries
female_name_dict = pickle.load(open('../data/female_name_dict.pkl','rb'))
male_name_dict = pickle.load(open('../data/male_name_dict.pkl','rb'))

# create lists of pub_ends and pub_associates
pub_ends = ['company','co','incorporated','inc','firm','press','group','publishers','publishing',
                    'publications','pub','books','ltd','limited','society','house','associates']
pub_associates = ['sons','son','brother','brothers']

# define functions used by NameObj and child classes
def remove_punct(word, dash = True):
    if dash == True:
        return ''.join([x for x in word if (x.isalnum()) or (x == '-') or (x=='–')])

def fix_initials(initials):
    i_list = initials.split()
    i_list = [remove_punct(x) for x in i_list]
    return ';'.join(i_list)

def get_fuzzy_pub_ends(pub_part):
    """
    Fuzzy matches pub ends.
    Returns pub ends closer than 2 edits away.
    """
    pub_part = ''.join([x for x in list(pub_part) if x.isalpha()]).lower()
    potential_matches = [x for x in pub_ends if (edit_distance(pub_part, x[:len(pub_part)+1]) < 2)]

    return potential_matches

# define NameObj
class NameObj(str):

    def __init__(self, name):
        self.full_name = name
        self.review_id = ''
        self.review_loc = ''
        self.all_variants = ''

    def getNameVariants(self):
        return self.all_variants


# define PubName
class PubName(NameObj):
    """
    Object type for publisher names. Inherits NameObj & string functions.

    Parameters
    ----------
    self.full_name : full name passed to the original init
    self.pub_count : number of names (inc. all full names, last names, sons, brothers)
    self.pub_type : type of publisher if found in pub_ends
    self.pub_names : all names (inc. all full names, last names - not including sons, brothers)
    self.pub_associates : son(s)/brother(s)

    Attributes
    ----------
    .getNameVariants() : returns all name variants for VIAF search

    """
    name_type = 'publisher'

    def __assign(self):
        self.name_parts = ''
        self.pub_count = ''
        self.pub_type = ''
        self.pub_names = ''
        self.pub_associates = ''

        temp = re.sub(',',' , ',self.full_name)
        if '&' in self.full_name or 'and' in self.full_name or 'And' in self.full_name:
            self.name_parts = [x.strip().lower() for x in re.split('&|and|And|,', temp)]
        else:
            self.name_parts = [x.strip().lower() for x in temp.split()]

        self.pub_type = self.name_parts[-1]
        self.pub_type_variants = get_fuzzy_pub_ends(self.pub_type)
        self.pub_count = len(self.name_parts[:-1])
        self.pub_associates = ''.join([remove_punct(x).lower() for x in self.name_parts if x in pub_associates])
        self.pub_names = ';'.join([word.replace("'s", "") for word in self.name_parts[:-1] if word not in pub_associates])

    def __getvariants(self):
        self.all_variants = [self.full_name]
        # kinda stuck here
        # will fix later
        self.all_variants = list(set([' '.join(x.lower().split()) for x in self.all_variants]))

    def __init__(self, name):
        self.full_name = name
        self.__assign()
        self.__getvariants()

# define AuthName

class PersonName(NameObj):
    """
    Object type for potential author names. Inherits NameObj & string functions.

    Parameters
    ----------
    .full_name : full name originally passed to original init
    .name_parts : all name parts
    .title : title
    .first_name : first name
    .first_initial : first initial, can be autogenerated from first name
    .middle_name : middle name
    .middle_initial : middle initial(s), can be autogenerated from middle name(s)
    .initials : first and middle initial(s), can be autogenerated from first/middle name(s)
    .last_name : last name
    .name_part_count : total number of name parts passed to the original init

    Attributes
    ----------
    .getNameVariants() : returns all name variants for VIAF search

    """
    name_type = 'person'

    def __assign(self):
        self.first_name = ''
        self.first_initial = ''
        self.middle_name = ''
        self.middle_initial = ''
        self.initials = ''

        # just title & last name
        if self.name_part_count < 3:
            pass

        # title, first name/initial, last name
        elif self.name_part_count == 3:
            if (len(self.name_parts[1])) < 3:
                self.first_initial = self.name_parts[1]
            else:
                self.first_name = self.name_parts[1]

        # title, first name/initial, middle name/initial, last name
        elif self.name_part_count == 4:
            if (len(self.name_parts[1])) < 3 and (len(self.name_parts[2])) < 3:
                self.first_initial = self.name_parts[1]
                self.middle_initial = self.name_parts[2]
            else:
                if (len(self.name_parts[1])) < 3:
                    self.first_initial = self.name_parts[1]
                    self.middle_name = self.name_parts[2]
                elif (len(self.name_parts[2])) < 3:
                    self.first_name = self.name_parts[1]
                    self.middle_initial = self.name_parts[2]
                else:
                    self.first_name = self.name_parts[1]
                    self.middle_name = self.name_parts[2]

        elif self.name_part_count > 4:

            # all initials
            if all([len(x)<3 for x in self.name_parts[1:-1]]):
                initial_list = []
                for x in self.name_parts[1:-1]:
                    initial_list.append(x)
                self.initials = ' '.join(initial_list)

            # all names
            elif all([len(x)>2 for x in self.name_parts[1:-1]]):
                self.first_name = self.name_parts[1]
                middle_name_list = []
                for x in self.name_parts[1:-1]:
                    middle_name_list.append(x)
                self.middle_name = ' '.join(middle_name_list)

            # first initial, middle names
            elif (len(self.name_parts[1])<3 and all([len(x)>2 for x in self.name_parts[2:-1]])):
                self.first_initial = self.name_parts[1]
                middle_name_list = []
                for x in self.name_parts[2:-1]:
                    middle_name_list.append(x)
                self.middle_name = ' '.join(middle_name_list)

            # first name, middle initials
            elif (len(self.name_parts[1])>2 and all([len(x)<3 for x in self.name_parts[2:-1]])):
                self.first_name = self.name_parts[1]
                middle_initial_list = []
                for x in self.name_parts[2:-1]:
                    middle_initial_list.append(x)
                self.middle_initial = ' '.join(middle_initial_list)

    def __generate(self):
        if self.first_name:
            self.first_initial = self.first_name[0]
            if self.middle_name:
                self.initials = ' '.join([x[0] for x in self.name_parts[1:-1]])
                self.middle_initial = ' '.join([x[0] for x in self.middle_name.split()])
            if self.middle_initial:
                self.initials = ' '.join([x[0] for x in self.name_parts[1:-1]])
        elif self.first_initial and self.middle_initial:
            self.initials = ' '.join([x[0] for x in self.name_parts[1:-1]])
        else:
            if self.middle_name:
                self.middle_initial = ' '.join([x[0] for x in self.middle_name.split()])

    def __reformat(self):
        if self.initials:
            self.initials = fix_initials(self.initials)
        if self.middle_initial:
            self.middle_initial = fix_initials(self.middle_initial)
        if self.first_initial:
            self.first_initial = fix_initials(self.first_initial)

    def __getvariants(self):
        self.first_name_variants = ['']

        if self.first_name:
            self.first_name_variants.append(self.first_name)
            if self.title_gender == 'F':
                lookup = female_name_dict.lookup(self.first_name.capitalize(), Verbosity.CLOSEST)
                for i, x in enumerate(lookup):
                    self.first_name_variants.append(lookup[i]._term)
            else:
                lookup = male_name_dict.lookup(self.first_name.capitalize(), Verbosity.CLOSEST)
                for i, x in enumerate(lookup):
                    self.first_name_variants.append(lookup[i]._term)
        if self.first_initial:
            self.first_name_variants.append(self.first_initial)

        # currently can't do anything with this, this might change
        self.last_name_variants = [self.last_name]

        self._firsts = self.first_name_variants
        self._middles = ['']
        if self.middle_name:
            self._middles.append(self.middle_name)
        if self.middle_initial:
            self._middles.extend(self.middle_initial.split(';'))
        self._lasts = self.last_name_variants

        self.all_variants = []
        for f in self._firsts:
            for m in self._middles:
                for l in self._lasts:
                    if f=='':
                        self.all_variants.append(' '.join([x.lower() for x in [f,l]]))
                    else:
                        self.all_variants.append(' '.join([x.lower() for x in [f,m,l]]))

        self.all_variants = list(set([' '.join(x.split()) for x in self.all_variants]))

    def __init__(self, name):
        self.full_name = name
        self.name_parts = [x.lower() for x in self.full_name.split()]
        self.title = remove_punct(self.name_parts[0])
        # ASSUMES ALMOST ALL NEUTRAL TITLES ARE MEN
        self.title_gender = title_gender_dict[self.title]
        # will add later
        self.guessed_gender = ''
        self.last_name = self.name_parts[-1]
        self.name_part_count = len(self.name_parts)

        self.__assign()
        self.__generate()
        self.__reformat()
        self.__getvariants()

    #def combine(authname, authname):
        #pass

    def __repr__(self):
        return self.full_name
