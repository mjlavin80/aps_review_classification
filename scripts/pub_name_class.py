# eva bacas, 3.2.19
# this file defines the PublisherName class & getPublishers function

# import required packages
import re
from review_name_class.py import ReviewNameObj, cleanPubMatches, removeDashForPub

pub_ends = ['company','co','incorporated','inc','firm','press','group','publishers','publishing',
                    'publications','pub','books','ltd','limited','society','house','associates']
pub_ends_list = '|'.join([x.capitalize()+'\.?(?!\w)' for x in pub_ends])

class PublisherName(ReviewNameObj):
    """
    Object type for publisher names. Inherits ReviewNameObj and string functions.

    Parameters
    ----------
    self.full_name : full name passed to the original init
    self.pub_count : number of names (inc. all full names, last names, sons, brothers)
    self.pub_type : type of publisher if found in pub_ends
    self.pub_names : all names (inc. all full names, last names - not including sons, brothers)
    self.pub_associates : son(s)/brother(s)

    """
    name_type = 'publisher'

    def __assign(self):
        self.pub_count = ''
        self.pub_type = ''
        self.pub_names = ''
        self.pub_associates = ''

        if removePunct(self.name_parts[-1]) in pub_ends:
            self.pub_type = self.name_parts[-1]
            self.pub_count = len(self.name_parts[:-1])
            self.pub_associates = [x for x in self.name_parts if x in pub_associates]
            self.pub_names = ';'.join([word.replace("'s", "") for word in self.name_parts[:-1]])
        else:
            self.pub_count = len(self.name_parts)
            self.pub_associates = [x for x in self.name_parts if x in pub_associates]
            self.pub_names = ';'.join([word.replace("'s", "") for word in self.name_parts[:-1]])

    def __find_variations(self):
        # in the future i will set this up to autogenerate variations inc. various pub ends
        self.potential_variations = ''

    def __init__(self, name):
        self.full_name = name
        self.name_parts = [x.lower() for x in self.full_name.split('&|and|And')]
        self.__assign()

def getPublishers(text, aps_id):
    """
    Takes a text and its aps_id. Both inputs are required.
    Returns a list of potential publishers. Searches using pub_ends, capitalization, and associates.

    For reference:
    -------------
    pub_ends = ['co','company','inc','incorporated','firm','press','group', 'pub','publishers','publishing',
                    'publications','books','ltd','limited','society','house','associates']

    pub_associates = ['sons','son','brother','brothers']

    """

    pubs = []

    # iter only works once before emptying
    p_iter = re.finditer(pub_ends_list, txts[0])
    p_indices = [(m.end(), m.group()) for m in p_iter]

    for i, index in enumerate(p_indices):
        try:
            if (i<len(p_indices)+1):
                match = re.finditer("(?<= [^A-Z&\.])[\S]{,10} ?[A-Z][\w&. ]*?" + index[1] + '(?!\w)',
                                txts[0][p_indices[i-1][0]:(p_indices[i][0] + 1)])
                all_matches = [(m.end(), removeDashForPub(m.group())) for m in match]
                if len(all_matches) > 0:
                    pubs.extend(cleanPubMatches(all_matches))
        except:
            pass

    pubs = [PublisherName(word) for word in pubs]

    for pub in pubs:
        pub.review_id = aps_id

    return list(set(pubs))
