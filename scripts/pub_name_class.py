# eva bacas, 3.2.19
# this file defines the PublisherName class

# import required packages
import re
from review_name_class.py import ReviewNameObj, removePunct

# create lists of pub_ends and pub_associates
pub_ends = ['company','co','incorporated','inc','firm','press','group','publishers','publishing',
                    'publications','pub','books','ltd','limited','society','house','associates']
pub_associates = ['sons','son','brother','brothers']

class PublisherName(ReviewNameObj):
    """
    Object type for publisher names. Inherits ReviewNameObj and string functions.

    Parameters
    ----------
    self.full_name : full name passed to the original init
    self.pub_count : number of names (inc. all full names, last names, sons, brothers)
    self.pub_type : type of publisher if found in pub_ends
    self.pub_names : all names (inc. all full names, last names - not including sons, brothers)
    self.pub_associates : son(s)/brother(s)

    Attributes
    ----------
    .getNameVariants() : returns all name variants for VIAF search

    """
    name_type = 'publisher'

    def __assign(self):
        self.pub_count = ''
        self.pub_type = ''
        self.pub_names = ''
        self.pub_associates = ''

        if removePunct(self.name_parts[-1]) in pub_ends:
            self.pub_type = self.name_parts[-1]
            self.pub_count = len(self.name_parts[:-1])
            self.pub_associates = [x for x in self.name_parts if x in pub_associates]
            self.pub_names = ';'.join([word.replace("'s", "") for word in self.name_parts[:-1]])
        else:
            self.pub_count = len(self.name_parts)
            self.pub_associates = [x for x in self.name_parts if x in pub_associates]
            self.pub_names = ';'.join([word.replace("'s", "") for word in self.name_parts[:-1]])

    def __find_variations(self):
        # in the future i will set this up to autogenerate variations inc. various pub ends
        self.potential_variations = ''

    def __init__(self, name):
        self.full_name = name
        self.name_parts = [x.lower() for x in self.full_name.split('&|and|And| ')]
        self.__assign()
