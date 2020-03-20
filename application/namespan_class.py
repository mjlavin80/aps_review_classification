# eva bacas, 3.18.20
# this file defines the NameSpan class and the NameSpanGenerator object

from application.name_obj_classes import get_fuzzy_pub_ends
from application.review_obj_class import ReviewObj
from nltk.metrics import edit_distance
import numpy as np
import copy

class NameSpan():
    """
    Object type for named entities. Currently contains both person names and publisher names.

    Parameters
    ----------
    self.name = NameObj
     - will contain either a PersonName or PubName object
    self.review_id : aps_id
    self.span : character span in review text
    self.start_char : start character in review text
    self.end_char : end character in review text
    self.label : name type
     - either "person" or "publisher"
    self.name_id : unique id for span object (review_id plus the start_char)
    self.group : grouping by similarity to other objects w the same label in review
     - defaults to -1
    self.collocates : 2 words preceding and following each NameSpan

    """
    def __init__(self, NameObj):
        self.name = NameObj
        self.review_id = NameObj.review_id
        self.review_doc = '' # ReviewObj will go here?
        self.span = NameObj.review_loc_chars
        self.start_char = NameObj.review_loc_chars[0]
        self.end_char = NameObj.review_loc_chars[1]
        self.label = NameObj.name_type
        self.name_id = int(self.review_id + str(self.start_char))
        self.group = -1
        self.collocates = []

def group_people(spanlist):

    names = sorted([(span.name, span.name_id) for span in spanlist], key=lambda x: len(x[0].last_name))
    group_dict = {}
    used_ids = []
    for e, (name, name_id) in enumerate(names):
        if (name_id not in used_ids):
            id_holder = [name_id]
            for name2, name_id2 in names:
                if (e < (len(name) - 1)) and (name_id!=name_id2):
                    if (edit_distance(name.last_name, name2.last_name[:len(name.last_name)+1]) < 2) and (name_id2 not in used_ids):
                        if (name.first_initial==name2.first_initial and name.middle_initial==name2.middle_initial or name.title==name2.title) or (name.first_initial==name2.first_initial or name.middle_initial==name2.middle_initial and name.title==name2.title):
                            id_holder.append(name_id2)
                            used_ids.append(name_id2)
            used_ids.append(name_id)
            for x in id_holder:
                group_dict[x] = e

    for span in spanlist:
        span.group = group_dict[span.name_id]

    return spanlist

def calc_edit_distances(plist,plist2):
    eds = []
    for x in plist[:-1]:
        for y in plist2[:-1]:
            eds.append(edit_distance(x,y))
    fuzzypubs1 = get_fuzzy_pub_ends(plist[-1])
    fuzzypubs2 = get_fuzzy_pub_ends(plist2[-1])
    fuzz = 10
    for x in fuzzypubs1:
        for y in fuzzypubs2:
            if edit_distance(x,y) < fuzz:
                fuzz = edit_distance(x,y)
    eds.append(fuzz)

    return eds

# def calc_edit_distances(plist,plist2):
#     eds = []
#     for x in plist[:-1]:
#         for y in plist2[:-1]:
#             eds.append(edit_distance(x,y))
#     fuzzypubs1 = get_fuzzy_pub_ends(plist[-1])
#     fuzzypubs2 = get_fuzzy_pub_ends(plist2[-1])
#     fuzz = []
#     for x in fuzzypubs1:
#         for y in fuzzypubs2:
#             fuzz.append(edit_distance(x,y))
#     eds.append(min(fuzz))
#
#     return eds

def group_pubs(spanlist):

    pubs = sorted([(span.name, span.name_id) for span in spanlist], key=lambda x: x[0].pub_count)
    group_dict = {}
    used_ids = []
    for e, (pub, name_id) in enumerate(pubs):
        if (name_id not in used_ids):
            id_holder = [name_id]
            for pub2, name_id2 in pubs:
                if np.mean(calc_edit_distances(pub.name_parts, pub2.name_parts)) < 3:
                    id_holder.append(name_id2)
                    used_ids.append(name_id2)
            used_ids.append(name_id)
            for x in id_holder:
                group_dict[x] = e

    for span in spanlist:
        span.group = group_dict[span.name_id]

    return spanlist

class NameSpanGenerator:
    """
    NameSpanGenerator.generate() takes a ReviewObj and returns all NameSpans.
    """

    def generate(self):
        all_spans = []
        if self.person_names:
            per_spans = [NameSpan(x) for x in self.person_names]
            all_spans.extend(group_people(per_spans))
        if self.pub_names:
            pub_spans = [NameSpan(x) for x in self.pub_names]
            all_spans.extend(group_pubs(pub_spans))
        self.spans = all_spans

        ni = [x.name.review_loc_toks for x in self.spans]
        toks = copy.deepcopy(self.coll_toks_ind)
        for e, span in enumerate(self.spans):
            if (ni[e] < 2):
                ftoks = list((2-ni[e])*"^")
                ftoks.extend((toks))
                span.collocates = ftoks[0:(ni[e]+3+(2-ni[e]))]
            elif (ni[e] > (len(toks)-3)):
                btoks = toks
                btoks.extend(list( (ni[e]-(len(toks)-3)) * "$") )
                span.collocates = btoks[(ni[e]-2):]
            else:
                span.collocates = self.coll_toks_ind[ni[e]-2:ni[e]+3]

        return self
