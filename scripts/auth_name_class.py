# eva bacas, 3.2.19
# this file defines the AuthName class

#import necessary packages
import pickle
from symspellpy.symspellpy import SymSpell, Verbosity
from nltk.metrics import edit_distance
from review_name_class.py import ReviewNameObj, cleanIndices, fixInitials

# create list of titles
titles = """Doctor,Dr,Mr,Mrs,Miss,Msgr,Monsignor,Rev,Reverend,Hon,Honorable,Honourable,Prof,Professor,Madame,Madam,Lady,Lord,Sir,Dame,Master,Mistress,Princess,Prince,Duke,Duchess,Baron,Father,Chancellor,Principal,President,Pres,Warden,Dean,Regent,Rector,Provost,Director
"""
titles = titles.rstrip().split(',')

# import symspell dictionaries
author_surname_dict = pickle.load(open('author_surname_dict.pkl','rb'))
first_name_dict = pickle.load(open('first_name_dict.pkl', 'rb'))
