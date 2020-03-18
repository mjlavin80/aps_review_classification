# eva bacas - 2.19.20 - book review cleaning and word count

# This script takes a folder of book review files and returns a CSV containing file ID, percent real words, and word counts.


# import necessary packages
import os
import re
import pandas as pd
import pickle
from nltk.corpus import stopwords
from symspellpy.symspellpy import SymSpell, Verbosity

# maximum edit distance per dictionary precalculation
max_edit_distance_dictionary = 2
prefix_length = 7
# create object
sym_spell = SymSpell(max_edit_distance_dictionary, prefix_length)
# load dictionary
dictionary_path = "../data/frequency_dictionary_en_82_765.txt"
term_index = 0
count_index = 1
sym_spell.load_dictionary(dictionary_path, term_index, count_index)

author_surname_dict = pickle.load(open('../data/author_surname_dict.pkl','rb'))

def is_word(word):
    """
    Returns true if word is found in sym_spell dictionary, otherwise returns false.
    """
    try:
        fake = sym_spell._words[word]
        return True
    except:
        return False

def is_surname(surname):
    """
    Returns true if name is found in sym_spell author surname dictionary, otherwise returns false.
    """
    try:
        fake = author_surname_dict._words[surname.lower()]
        return True
    except:
        return False

def clean_text(txt):
    """
    Strips whitespace, removes sentence ending characters and quotes, removes whitespace again.
    """
    stripped_txt = ' '.join(txt.split())
    toks = re.split('[ .,;:!\?\'\"]', stripped_txt)
    return [w.lower() for w in toks if w]

def find_dashes(toks):
    """
    Returns list of indices for words ending in dashes.
    """
    dash_indices = [i for i, word in enumerate(toks) if (len(word)>1) and (word.endswith('-'))]
    return dash_indices

def fix_hyphenated_words(toks):
    """
    Replaces hyphenated words with single word.
    """
    dash_indices = find_dashes(toks)
    to_be_deleted = []
    for i in dash_indices:
        #if neither are words, e.g. pieces of names or misspellings
        if (is_word(toks[i][:-1])==False or is_word(toks[i+1])==False):
            #replace first item with combined, delete second item
            to_be_deleted.append(i+1)
            toks[i] = (toks[i][:-1] + toks[i+1])
            #if combined is a word
        elif (is_word((toks[i][:-1] + toks[i+1]))):
            to_be_deleted.append(i+1)
            toks[i] = (toks[i][:-1] + toks[i+1])
        elif (is_surname((toks[i][:-1] + toks[i+1]))):
            to_be_deleted.append(i+1)
            toks[i] = (toks[i][:-1] + toks[i+1])
        else:
            pass
    #do this after so u don't heck up the indices
    toks = [w for i, w in enumerate(toks) if i not in to_be_deleted]
    return toks

def check_quality(txt):
    """
    Returns ratio of real words to total words in document, excluding stopwords.
    """
    #lowercase, remove whitespace & sent ending punctuation
    toks = cleanText(txt)
    #fix hyphenated word issues
    toks = fixHyphenatedWords(toks)
    no_stop = [w for w in toks if w not in stopwords.words('english')]
    real_words = [w for w in no_stop if isWord(w)]
    return len(real_words)/len(no_stop)

def get_word_count(txt):
    """
    Returns word count.
    """
    #lowercase, remove whitespace & sent ending punctuation
    toks = clean_text(txt)
    #fix hyphenated word issues
    toks = fix_hyphenated_words(toks)
    return len(toks)

def preprocess_text(txt):
    #adding space around certain problem punctuation
    txt = re.sub(',',' , ',txt)
    txt = re.sub(';',' ; ',txt)
    txt = re.sub(':',' : ',txt)
    txt = re.sub('"',' " ',txt)
    txt = re.sub('&',' & ',txt)
    txt = re.sub("'(?!s)"," ' " ,txt)
    # remove extra whitespace
    txt = re.sub(' +',' ',txt)
    # fix hyphenated words
    txt = ' '.join(fix_hyphenated_words(txt.split()))
    #putting space back
    txt = re.sub(' , ',', ',txt)
    txt = re.sub(' ; ','; ',txt)
    txt = re.sub(' : ',': ',txt)
    #and fixing hyphen issues
    txt = re.sub('-(?!\w)',' - ',txt)
    txt = re.sub('(?<!\w)-',' - ',txt)
    return txt
