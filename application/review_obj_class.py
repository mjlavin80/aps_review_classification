# eva bacas, 3.5.20
# this file defines the ReviewObj class & functions necessary to find PersonNames & PubNames in ReviewObj

from application.name_obj_classes import PubName, PersonName, remove_punct
from application.text_preprocessing import preprocess_text
from nltk import word_tokenize
import re
import pickle
from symspellpy.symspellpy import SymSpell, Verbosity

pub_ends = ['company','co','incorporated','inc','firm','press','group','publishers','publishing',
                    'publications','pub','books','ltd','limited','society','house','associates']
pub_ends = [x.capitalize() for x in pub_ends]

city_dict = pickle.load(open('../data/city_dict.pkl', 'rb'))

def is_part_of_pub(pub_part):
    if (pub_part == 'and') or (pub_part =='&'):
        return True
    elif city_dict.lookup(pub_part.lower(), Verbosity.CLOSEST, max_edit_distance=2):
        return False
    else:
        return pub_part[0].isupper()

def obscure_single_match(text, x, y):
    text_list = list(text)
    text_list[x:y] = list(len(text[x:y]) * '@')
    return ''.join(text_list)

def remove_duplicate_pubnames(pnlist):
    cleaned = []
    for e, (x, y) in enumerate(pnlist):
        starts = [a for (a,b) in pnlist[e+1:]]
        if x in starts:
            pass
        else:
            cleaned.append(pnlist[e])
    return cleaned

def get_publishers(review):
    """
    Takes a ReviewObj.
    Returns a list of potential publishers. Searches using pub_ends, capitalization, and associates.

    For reference:
    -------------
    pub_ends = ['co','company','inc','incorporated','firm','press','group', 'pub','publishers','publishing',
                    'publications','books','ltd','limited','society','house','associates']

    pub_associates = ['sons','son','brother','brothers']

    """

    pubs = []
    char_spans = []
    tok_spans = []

    toks = review.cleaned_toks
    txt = review.cleaned_text

    pubnames = []

    for e, tok in enumerate(toks):
        if tok.replace(",","").replace(".","") in pub_ends:
            if is_part_of_pub(toks[e-1]):
                pub_name = []
                pub_span = []
                for pos in range(e-1, e-6, -1):
                    if toks[pos] == '.':
                        break
                    if toks[pos] in pub_ends:
                        break
                    if not is_part_of_pub(toks[pos]):
                        break
                    pub_name.append(toks[pos])
                    pub_span.append(pos)
                if any([x.isalpha() for x in [word for word in pub_name if word !='and']]) and any([len(x)>2 for x in [word for word in pub_name if word !='and']]):
                    pubnames.append((pub_span[-1], e+1))

    pubnames = remove_duplicate_pubnames(pubnames)

    if len(pubnames) > 0:
        temp_txt = txt
        for (x, y) in pubnames:
            newname = ' '.join(toks[x:y])
            pubs.append(newname)
            tok_spans.append((x,y))
            match = re.search(newname, temp_txt)
            char_spans.append(match.span())
            temp_txt = obscure_single_match(temp_txt, *match.span())

    pubs = [PubName(word) for word in pubs]

    for e, pub in enumerate(pubs):
        pub.review_id = review.review_id
        pub.review_loc_toks = tok_spans[e]
        pub.review_loc_chars = char_spans[e]

    return pubs

titles = """Doctor,Dr,Mr,Mrs,Miss,Msgr,Monsignor,Rev,Reverend,Hon,Honorable,Honourable,Prof,Professor,Madame,Madam,Lady,Lord,Sir,Dame,Master,Mistress,Princess,Prince,Duke,Duchess,Baron,Father,Chancellor,Principal,President,Pres,Warden,Dean,Regent,Rector,Provost,Director
"""
titles = titles.rstrip().split(',')
title_list = '\.?\s(?=[A-Z])|'.join(titles) + '\.?\s(?=[A-Z])'

def remove_punct_not_following_title_or_initial(name):
    name_parts = name.split()
    cleaned_name = []
    for part in name_parts:
        if part[-1] in '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~':
            if (len(part)>2) and (part[:-1] not in titles):
                cleaned_name.append(part[:-1])
            else:
                cleaned_name.append(part)
        else:
            cleaned_name.append(part)
    return ' '.join(cleaned_name)

def clean_name(name):
    name = remove_punct_not_following_title_or_initial(name)
    cleaned_name = []
    return ' '.join([word for word in name.split() if (word[0].isalpha())])

def get_names_following_titles(review):
    """
    Returns names following titles - specifically capitalized titles followed by capitalized names.
    Names can be any number of words in length, and can include punctuation.
    """
    names = []
    spans = []

    txt = review.no_pubs_text

    iterx = re.finditer(title_list, txt)
    indices = [(m.start(), m.group()) for m in iterx]

    for e, index in enumerate(indices):

        if (e==len(indices)-1):
            end_index = -1
        else:
            end_index = indices[e+1][0]

        end_span = len(txt[indices[e][0]:end_index])
        get_match = re.finditer('[A-Z]\w+[^A-Z]|[A-Z].[^A-Z]', txt[indices[e][0]:end_index])
        matches = [(m.span(), m.group()) for m in get_match]
        matches.reverse()

        for n, m in enumerate(matches):
            if n<len(matches)-1:
                if (m[0][1] != matches[n-1][0][0]):
                    end_span = m[0][1]

        result = txt[indices[e][0]:(indices[e][0] + end_span - 1)]

        if len(result) > len(indices[e][1]):
            names.append(txt[indices[e][0]:(indices[e][0] + end_span - 1)])
            spans.append(indices[e][0])

    names = [word.replace("'s", "") for word in names]
    names = [PersonName(clean_name(word)) for word in names]

    for e, name in enumerate(names):
        name.review_id = review.review_id
        name.review_loc_chars = (spans[e], spans[e]+len(name))

    return names

class ReviewObj():
    """
    Object type for book reviews.
    Takes aps_id followed by review text. Both are required.

    Parameters
    ----------
    self.review_id : aps_id
    self.original_text : text passed to the original init
    self.cleaned_text : cleaned text for generating names
    self.pub_names : list of PubNames contained within the review
    self.person_names : list of PersonNames contained within the review
    self.cleaned_toks : cleaned_text tokenized using NLTK word_tokenize
    self.coll_toks_ind : tokens but all spaces in NameObjs replaced by hyphens
    self.coll_toks_all : tokens but PubNames, PersonNames replaced by ■,●

    """

    def __obscure_matches(self, name = 'ex'):
        text_list = list(self.cleaned_text)
        if name == 'pub':
            for (x, y) in [pub.review_loc_chars for pub in self.pub_names]:
                text_list[x:y] = list(len(self.cleaned_text[x:y]) * '@')
        if name == 'person':
            for (x, y) in [pers.review_loc_chars for pers in self.person_names]:
                text_list[x:y] = list(len(self.cleaned_text[x:y]) * '@')
        if name == 'both':
            for (x, y) in [pub.review_loc_chars for pub in self.pub_names]:
                text_list[x:y] = list(len(self.cleaned_text[x:y]) * '■')
            for (x, y) in [pers.review_loc_chars for pers in self.person_names]:
                text_list[x:y] = list(len(self.cleaned_text[x:y]) * '●')
        return ''.join(text_list)

    def __prep_for_collocations(self):
        text_list = list(self.cleaned_text)
        for (x, y) in [pub.review_loc_chars for pub in self.pub_names]:
            text_list[x:y] = list(self.cleaned_text[x:y].replace(' ','_'))
        for (x, y) in [pers.review_loc_chars for pers in self.person_names]:
            text_list[x:y] = list(self.cleaned_text[x:y].replace(' ','_'))
        return ''.join(text_list)

    def __findnames(self):
        self.pub_names = get_publishers(self)
        self.no_pubs_text = self.__obscure_matches(name = 'pub')
        self.person_names = get_names_following_titles(self)
        self.no_people_text = self.__obscure_matches(name = 'person')

    def __init__(self, aps_id, txt):
        self.review_id = aps_id
        self.original_text = txt
        self.cleaned_text = preprocess_text(txt)
        self.cleaned_toks = word_tokenize(self.cleaned_text)

        self.__findnames()

        self.coll_toks_ind = word_tokenize(self.__prep_for_collocations())
        self.coll_toks_all = word_tokenize(self.__obscure_matches(name = 'both'))
