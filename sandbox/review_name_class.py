# eva bacas, 3.2.19
# this file defines the ReviewName class & functions used by PublisherName & AuthName

# import necessary packages
import re

# create list of titles
titles = """Doctor,Dr,Mr,Mrs,Miss,Msgr,Monsignor,Rev,Reverend,Hon,Honorable,Honourable,Prof,Professor,Madame,Madam,Lady,Lord,Sir,Dame,Master,Mistress,Princess,Prince,Duke,Duchess,Baron,Father,Chancellor,Principal,President,Pres,Warden,Dean,Regent,Rector,Provost,Director
"""
titles = titles.rstrip().split(',')

class ReviewNameObj(str):
    review_id = ''
    review_loc = ''

def removePunct(word, dash = True):
    if dash == True:
        return ''.join([x for x in word if (x.isalnum()) or (x == '-') or (x=='–')])

def fixInitials(initials):
    i_list = initials.split()
    i_list = [removePunct(x) for x in i_list]
    return ';'.join(i_list)





# get rid of all after this

def cleanIndices(index_tuple):
    """
    Removes all non-period punctuation from the string component of an index tuple.
    Returns cleaned tuple.
    """
    x = index_tuple[0]
    y = index_tuple[1]
    if y[-1] in '!"#$%&\'()*+,-/:;<=>?@[\\]^_`{|}~':
        y = y[:-1]
    return (x,y)

# Functions used by PublisherName

def removeDashForPub(pub_match):
    """
    Takes single PublisherName string.
    Removes dashes not within names (between two word characters).
    Returns cleaned PublisherName.
    """
    return re.sub(r'(?<!/w)-(?!/w)', '', pub_match)

def cleanPubMatches(match_list):
    """
    Takes list of PublisherName matches in the form of index tuples.
    Trims PublisherName matches down to just name components.
    Returns cleaned PublisherNames. Integer part of indices is NOT returned.
    """
    cleaned_matches = []
    for match in match_list:
        index_to_start = 0
        for i, x in enumerate(match[1].split()):
            if x[0].islower() and x[0]!='&':
                index_to_start = i+1
        cleaned_matches.append(' '.join(match[1].split()[index_to_start:]))
    return cleaned_matches

# Functions used by AuthName

def cleanTextForNameSearch(txt):
    """
    Removes all non-newline whitespace and adds spaces around commas, semicolons, and colons.
    """
    #delete extra whitespace
    txt = re.sub(' +',' ',txt)

    #delete characters that should never be in this dataset (i think)
    txt = re.sub("\\'\(\)\*/<=>@\[\]^_`\|~","",txt)

    #adding space around certain punctuation
    txt = re.sub(',',' , ',txt)
    txt = re.sub(';',' ; ',txt)
    txt = re.sub(':',' : ',txt)
    txt = re.sub('"',' " ',txt)
    txt = re.sub("'"," ' " ,txt)
    return txt

def removePeriodsNotFollowingTitleOrInitial(name):
    """
    Takes string, removes periods not following a title or an initial.
    """
    name_parts = name.split()
    cleaned_name = []
    for part in name_parts:
        if (len(part)>2) and (part.endswith('.')) and (part[:-1] not in titles):
            cleaned_name.append(part[:-1])
        else:
            cleaned_name.append(part)
    return ' '.join(cleaned_name)

def cleanName(name):
    return ' '.join([word for word in name.split() if (word[0].isalpha())])
