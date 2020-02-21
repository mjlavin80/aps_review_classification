# eva bacas - 2.19.20 - book review cleaning and word count
 
# This script takes a folder of book review files and returns a CSV containing file ID, percent real words, and word counts.
    
    
# import necessary packages
import os
import re
import pandas as pd
from nltk.corpus import stopwords
from symspellpy.symspellpy import SymSpell, Verbosity

# maximum edit distance per dictionary precalculation
max_edit_distance_dictionary = 2
prefix_length = 7
# create object
sym_spell = SymSpell(max_edit_distance_dictionary, prefix_length)
# load dictionary
dictionary_path = "../frequency_dictionary_en_82_765.txt"
term_index = 0 
count_index = 1
sym_spell.load_dictionary(dictionary_path, term_index, count_index)

def isWord(word):
    """
    Returns true if word is found in sym_spell dictionary, otherwise returns false.
    """
    try:
        fake = sym_spell._words[word]
        return True
    except: 
        return False
    
def cleanText(txt):
    """
    Strips whitespace, removes sentence ending characters and quotes, removes whitespace again.
    """
    stripped_txt = ' '.join(txt.split())
    toks = re.split('[ .,;:!\?\'\"]', stripped_txt)
    return [w.lower() for w in toks if w]

def findDashes(toks):
    """
    Returns list of indices for words ending in dashes.
    """
    dash_indices = [i for i, word in enumerate(toks) if (len(word)>1) and (word.endswith('-'))]
    return dash_indices

def fixHyphenatedWords(toks):
    """
    Replaces hyphenated words with single word.
    """
    dash_indices = findDashes(toks)
    to_be_deleted = []
    for i in dash_indices:
        #if neither are words, e.g. pieces of names or misspellings
        if (isWord(toks[i][:-1])==False and isWord(toks[i+1])==False):
            #replace first item with combined, delete second item
            to_be_deleted.append(i+1)
            toks[i] = (toks[i][:-1] + toks[i+1])
        #if combined is a word
        elif (isWord((toks[i][:-1] + toks[i+1]))):
            to_be_deleted.append(i+1)
            toks[i] = (toks[i][:-1] + toks[i+1])
        else:
            pass
    #do this after so u don't heck up the indices
    toks = [w for i, w in enumerate(toks) if i not in to_be_deleted]
    return toks

def checkQuality(txt):
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

def getWordCount(txt):
    """
    Returns word count.
    """
    #lowercase, remove whitespace & sent ending punctuation
    toks = cleanText(txt)
    #fix hyphenated word issues
    toks = fixHyphenatedWords(toks)
    return len(toks)

def removeTxt(file_id):
    return file_id[:-4]

# ** replace with name of directory containing files **
directory = "../../aps_reviews_50/aps_reviews/"

filenames = os.listdir(directory)

# open files
txts = []
for file in filenames:
    with open(directory + file) as f:
        txts.append(f.read())
        
# create pandas df to save as CSV       
txt_df = pd.DataFrame()

# load info into df        
txt_df['texts'] = txts
txt_df['cleaned_texts'] = txt_df.texts.map(cleanText).map(fixHyphenatedWords)
txt_df['id_num'] = filenames
txt_df['id_num'] = txt_df.id_num.map(removeTxt)
txt_df['word_count'] = txt_df.texts.map(getWordCount)
txt_df['percent_real_words'] = txt_df.texts.map(checkQuality)

# save
txt_df.to_csv('book_review_word_counts.csv')

print("Script complete. CSV saved as book_review_word_counts.csv.")
