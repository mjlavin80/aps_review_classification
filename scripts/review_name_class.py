# eva bacas, 3.2.19
# this file defines the ReviewName class & functions used by PublisherName & AuthName

class ReviewNameObj(str):
    review_id = ''
    review_loc = ''

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
