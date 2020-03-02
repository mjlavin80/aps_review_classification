# eva bacas, 3.2.19
# this file defines the AuthName class

#import necessary packages
import pickle
from symspellpy.symspellpy import SymSpell, Verbosity
from nltk.metrics import edit_distance
from review_name_class.py import ReviewNameObj, cleanIndices, fixInitials, cleanTextForNameSearch,
removePeriodsNotFollowingTitleOrInitial

# create list of titles
titles = """Doctor,Dr,Mr,Mrs,Miss,Msgr,Monsignor,Rev,Reverend,Hon,Honorable,Honourable,Prof,Professor,Madame,Madam,Lady,Lord,Sir,Dame,Master,Mistress,Princess,Prince,Duke,Duchess,Baron,Father,Chancellor,Principal,President,Pres,Warden,Dean,Regent,Rector,Provost,Director
"""
titles = titles.rstrip().split(',')

# create title gender dict
title_gender_dict = {}
w_list = ['Mrs','Miss','Madame','Madam','Lady','Dame','Mistress','Princess','Duchess']
for x in titles:
    if x in w_list:
        title_gender_dict[x] = 'F'
    else:
        title_gender_dict[x] = 'M'

# import symspell dictionaries
author_surname_dict = pickle.load(open('author_surname_dict.pkl','rb'))
first_name_dict = pickle.load(open('first_name_dict.pkl', 'rb'))








def getCapitalizedWords(txt):
    """
    Returns strings of capitalized words up 3 words long.
    Removes words/phrases containing stopwords and words found later in the text lowercased.
    """
    #listen idk why it won't just let me put in an optional repeat either
    all_words = []

    #three words
    all_words.extend([match for match in re.findall('[A-Z]\S* [A-Z]\S* [A-Z]\S+', txt) if
                      all([(removePunct(word).lower() not in stopword_list) for word in match.split()])
                      and all([(removePunct(word).lower() not in txt) for word in match.split()])])

    #two words
    two_words = [match for match in re.findall('[A-Z]\S* [A-Z]\S+', txt) if
                      all([(removePunct(word).lower() not in stopword_list) for word in match.split()])
                      and all([(removePunct(word).lower() not in txt) for word in match.split()])
                      and all([match not in x for x in all_words])]

    all_words.extend(two_words)

    #one word
    one_words = [match for match in re.findall('[A-Z]\S+', txt) if
                      (removePunct(match).lower() not in stopword_list)
                      and (removePunct(match).lower() not in txt)
                      and all([match not in x for x in all_words])]

    all_words.extend(one_words)

    return [word for word in [' '.join([removePunct(y) for y in x.split() if removePunct(y) not in titles])
                      for x in all_words] if (len(word)>1)]






def getNamesFollowingTitles(txt, aps_id):
    """
    Returns names following titles - specifically capitalized titles followed by capitalized names.
    Names can be any number of words in length, and can include punctuation.

    object factory
    potentially add index from original text in dict

    """
    names = []

    # iter only works once before emptying
    iterx = re.finditer(title_list, txt)
    indices = [(m.start(), m.group()) for m in iterx]
    indices = [cleanIndices(m) for m in indices]

    for i, index in enumerate(indices):
        if (i<len(indices)-1):
            try:
                match = re.match(indices[i][1] + '\w{2,}[.,;:!\?\'\"]', txt[indices[i][0]:indices[i+1][0]])
                names.append(match.group()[:-1])
            except:
                try:
                    match = re.match(indices[i][1] + '.*? [a-z]|\Z',
                                     txt[indices[i][0]:indices[i+1][0]])
                    names.append(match.group()[:-2])
                except:
                    pass
        else:
            try:
                match = re.match(indices[i][1] + '\w{2,}[.,;:!\?\'\"]', txt[indices[i][0]:])
                names.append(match.group()[:-1])
            except:
                try:
                    match = re.match(indices[i][1] + '.*? [a-z]|\Z',
                                     txt[indices[i][0]:])
                    names.append(match.group()[:-2])
                except:
                    pass

    names = [word.replace("'s", "") for word in names]
    names = [removePeriodsNotFollowingTitleOrInitial(word) for word in names]
    names = [AuthName(cleanName(word)) for word in names]

    return list(set(names))
