# eva bacas, 3.2.19
# this file defines the AuthName class

#import necessary packages
import os
import pandas as pd
import re
from collections import Counter
import numpy as np
import pickle
from nltk.metrics import edit_distance
%pprint

# create list of titles
titles = """Doctor,Dr,Mr,Mrs,Miss,Msgr,Monsignor,Rev,Reverend,Hon,Honorable,Honourable,Prof,Professor,Madame,Madam,Lady,Lord,Sir,Dame,Master,Mistress,Princess,Prince,Duke,Duchess,Baron,Father,Chancellor,Principal,President,Pres,Warden,Dean,Regent,Rector,Provost,Director
"""
titles = titles.rstrip().split(',')

# create first name symspell dictionary
from symspellpy.symspellpy import SymSpell, Verbosity

# maximum edit distance per dictionary precalculation
max_edit_distance_dictionary = 2
prefix_length = 7
# create object
first_name_symspell = SymSpell(max_edit_distance_dictionary, prefix_length)
# load dictionary
dictionary_path = "name_freq_dict.txt"
term_index = 0
count_index = 1
first_name_symspell.load_dictionary(dictionary_path, term_index, count_index, separator=",")
