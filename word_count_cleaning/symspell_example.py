import os

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