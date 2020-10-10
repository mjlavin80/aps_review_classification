from nltk import word_tokenize
from nltk.corpus import stopwords
from fuzzysearch import find_near_matches
from collections import Counter
import re
import string
from random import shuffle

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

def find_dashes(toks):
    """
    Returns list of indices for words ending in dashes.
    """
    dash_indices = [i for i, word in enumerate(toks) if (len(word)>1) and (word.endswith('-'))]
    return dash_indices

def remove_function_head(sequence):
    if sequence:
        if sequence[0][0].islower():
            sequence.pop(0)
            return remove_function_head(sequence)
        else:
            return sequence
    else:
        return None
    
def remove_function_tail(sequence):
    if sequence: 
        if sequence[-1].lower() in stopwords.words('english'):
            sequence.pop()
            return remove_function_tail(sequence)
        else:
            return sequence
    else:
        return None

def remove_honorifics(sequence):
    honorifics = """Doctor,Dr,Mr,Mrs,Miss,Msgr,Monsignor,Rev,Reverend,Hon,Honorable,Honourable,Prof,Professor,Madame,Madam,Lady,Lord,Sir,Dame,Master,Mistress,Princess,Prince,Duke,Duchess,Baron,Father,Chancellor,Principal,President,Pres,Warden,Dean,Regent,Rector,Provost,Director"""
    honorific_list = honorifics.lower().split(',')
    if sequence:
        if len(sequence) == 1 and sequence[0].lower() in honorific_list:
            return None
        else:
            return sequence
    else:
        return None

def cull_title(text_block, patterns):
    
    for i in patterns:
        text_block = text_block.replace(i, "")
        
    culled_title_candidates = [list(),]
    for token in word_tokenize(text_block):
        if token[0].isupper() or token.lower() in stopwords.words('english') or token in string.punctuation:
            if len(culled_title_candidates[-1]) > 0:
                if token not in string.punctuation:
                    culled_title_candidates[-1].append(token)
            else:
                if token[0].isupper():
                    culled_title_candidates[-1].append(token)
        else:
            if len(culled_title_candidates[-1]) > 0:
                culled_title_candidates.append(list())
    # remove any culled_title_candidate if it's just an honorific
    candidates_no_tail = []
    for sequence in culled_title_candidates:
        
        if len(sequence) > 0:
            #remove lowercase function word heads and tails recursively
            sequence = remove_function_tail(sequence)
            sequence = remove_function_head(sequence)
            sequence = remove_honorifics(sequence)
            if sequence:
                candidates_no_tail.append(" ".join(sequence).lower())
    non_titles = ['new publications','the latest books and authors', 'latest books and authors', 'books and authors', \
                  'the latest books', 'latest books', 'minor notices', 'no title', 'a book-shelf for the month', 'book-shelf', \
                  'some recent books', 'some recent fiction', 'recent books', 'recent fiction', 'latest fiction', 'current books', 'current fiction' \
                   'books and authors', 'our book table', 'current literature', 'literature', 'book reviews' 'reviews', 'review',]
    candidates_tidy = []
    for i in candidates_no_tail:
        title = i
        for z in non_titles:
            title = title.replace(z, '')
        title = title.strip()
        if title != '':
            candidates_tidy.append(title)
    return candidates_tidy

class ReviewObject():
    """
    object class for a book review, including variables for labels, full text, parsed entities, match data, etc.
    tokens_raw (list)
    tokens_tidy (list)
    title_candidates {candidate_string: score, candidate_string: score}
    author_candidates {candidate_string: score, candidate_string: score}
    publisher_candidates {candidate_string: score, candidate_string: score}
    candidate_mappings {"authors": { candidate_string: {match_string: match_score, match_string: match_score}}, "titles": None, "publishers": None}
    
    """
    def __init__(self, title, full_text, known_publishers, **kwargs):
        # instantiate with metdata from db
        self.title = title
        self.full_text = full_text
        self.known_publishers = known_publishers 
        self.__dict__.update(kwargs)
        self.make_tokens()
        self.make_tidy()
        self.extract_title_candidates()
        self.extract_author_candidates()
        self.extract_publisher_candidates()
        self.map_candidates_to_entities()
        self.select_top_matches()
        
    def make_tokens(self):
        self.tokens_raw = word_tokenize(self.full_text)

    def make_tidy(self):
        #adding space around certain problem punctuation
        txt = re.sub(',',' , ',self.full_text)
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
        self.text_tidy = re.sub('(?<!\w)-',' - ',txt)
        self.tokens_tidy = word_tokenize(self.text_tidy)
        
        self.text_tidy_lower = self.text_tidy.lower()
        self.tokens_tidy_lower = word_tokenize(self.text_tidy_lower)
        
    
    def extract_title_candidates(self):
        """
        1. Look for capitalized string in review title
        2. Look for before and after cues, get capitalized strings
        3. If no cues, look for capitalized strings
        4. Cull obvious false positives 
        """
        patterns = ["chapter of", "chapters of", "latest", "book called", "volume called", "novel called", "volume of", "edition of", "novel", \
                    "study of", "entitled", "the author of", "with the title", "the manner in which" \
                    "book", "story", "life of"]
        
        title_candidates = []
        if self.record_title:
            title_candidates.extend(re.findall("\".+\"", self.record_title))
            title_candidates.extend(re.findall("\'.+\'", self.record_title))
            
        culled_title_candidates_all = []
        for text_block in title_candidates:
            culled_title_candidates_all.extend(cull_title(text_block, patterns))
                
        if len(culled_title_candidates_all) == 0:
            title_candidates.append(self.record_title)
            culled_title_candidates_all = []
            for text_block in title_candidates:
                culled_title_candidates_all.extend(cull_title(text_block, patterns))

            for i in patterns:
                pattern = "".join([i, ".+?\."])
                title_candidates.extend(re.findall(pattern, self.text_tidy))


            for text_block in title_candidates:
                culled_title_candidates_all.extend(cull_title(text_block, patterns))
        
        self.title_candidates = Counter(culled_title_candidates_all)
    
    def extract_author_candidates(self):
        """
        1. Look for honorifics, try to extrapolate surnames
        2. Look for surnames in review title
        2. Look for before and after cues + surnames in text
        3. If no cues, look for capitalized N-grams ending with surnames
        4. Score each candidate entry based on how it was found
        """
        titles = """Doctor,Dr,Mr,Mrs,Miss,Msgr,Monsignor,Rev,Reverend,Hon,Honorable,Honourable,Prof,Professor,Madame,Madam,Lady,Lord,Sir,Dame,Master,Mistress,Princess,Prince,Duke,Duchess,Baron,Father,Chancellor,Principal,President,Pres,Warden,Dean,Regent,Rector,Provost,Director"""
        titles = titles.split(',')

        full_names = {}

        for e,i in enumerate(self.tokens_tidy):
            maybe_title = "".join([z for z in i if z.isalpha()])
            if maybe_title in titles:

                surname = []
                for p in [e+1, e+2, e+3]:
                    try:
                        if self.tokens_tidy[p][0].isupper():
                            surname.append(self.tokens_tidy[p])
                    except:
                        pass
                if len(surname) > 0:
                    surname = " ".join(surname).replace("'s", "")
                    surname_cleaned = []
                    for s in surname:
                        if s not in '!"#$%&\'()*+,-/:;<=>?@[\\]^_`{|}~':
                            surname_cleaned.append(s)
                    surname_cleaned = "".join(surname_cleaned)
                    try:
                        check = full_names[surname]
                    except:
                        full_names[surname] = {}
                    try:
                        full_names[surname]['title'].append(maybe_title)
                    except:
                        full_names[surname]['title'] = [maybe_title,]
                    try:
                        full_names[surname]['surname_cleaned'].append(surname_cleaned)
                    except:
                        full_names[surname]['surname_cleaned'] = [surname_cleaned,]
        
        for surname in full_names.keys():
            s = surname.split()
            for e, i in enumerate(self.tokens_tidy):
                if self.tokens_tidy[e:e+len(s)] == s:
                    forename = "".join([x for x in self.tokens_tidy[e-1] if x.isalpha()])
                    if forename.istitle() and forename not in titles:
                        try:
                            full_names[surname]['forename'].append(forename)
                        except:
                            full_names[surname]['forename'] = [forename,]
                try:
                    forenames = full_names[surname]['forename']
                except:
                    full_names[surname]['forename'] = []

        for name in full_names.keys():
            for i in full_names[name]['forename']:
                try: 
                    full_names[name]['full_name'].append(i + " " + name)
                except:
                    full_names[name]['full_name'] = [i + " " + name,]
            try:
                full = full_names[surname]['full_name']
            except:
                full_names[name]['full_name'] = []
        
        full_name_candidates = {}

        for n in full_names.keys():
            for f in full_names[n]['full_name']:
                try:
                    full_name_candidates[f.lower()] += 1
                except:
                    full_name_candidates[f.lower()] = 1
        
        author_surname_candidates = {}
        
        # add title and surnames
        for n,o in full_names.items():
            for i in o['surname_cleaned']:
                try:
                    author_surname_candidates[i.lower()] +=1
                except:
                    author_surname_candidates[i.lower()] =1
                
                # check if surname in a full name
                name_part = False
                for full in full_name_candidates.keys():
                    if i in full:
                        name_part = True
                if not name_part:
                    try: 
                        full_name_candidates[i.lower()] += 1
                    except:
                        full_name_candidates[i.lower()] = 1
                        
        self.author_candidates = full_name_candidates
        self.author_surname_candidates = author_surname_candidates
    
    def extract_publisher_candidates(self):
        """
        1. Fuzzy match against known publishers, and count mentions
        2. If no matches, look for pub ends and capitalization, and count each candidate
        """
        pub_ends = ['company','co','incorporated','inc','firm','press','group','publishers','publishing', \
            'publications','pub','books','ltd','limited','society','house','associates', 'book', 'university']
        
        self.publisher_candidates = {}
        
        #this list is defined outside the class
        for p in self.known_publishers:
            #base fuzziness on length of pubname
            if len(p) < 6:
                fuzz=0
            elif len(p) > 5 and len(p) < 10:
                fuzz=1
            elif len(p) > 9 and len(p) < 15:
                fuzz=2
            else:
                fuzz=3
            
            matches = find_near_matches(p, self.text_tidy, max_l_dist=fuzz)
            
            if len(matches) > 0:
                match_strings = [self.text_tidy[m.start:m.end] for m in matches]
                for i in match_strings:
                    try:
                        self.publisher_candidates[p] += 1
                    except:
                        self.publisher_candidates[p] = 1
                        
        if self.publisher_candidates == {}:
            publisher_candidates = [list(),]
            for token in self.tokens_tidy:
                if token[0].isupper() or token in ['and', '&'] or token in string.punctuation:
                    if len(publisher_candidates[-1]) > 0:
                        if token not in string.punctuation:
                            publisher_candidates[-1].append(token) 
                    else:
                        if token[0].isupper():
                            publisher_candidates[-1].append(token)
                else:
                    if len(publisher_candidates[-1]) > 0:
                        publisher_candidates.append(list())
    
            matches = []
            for sequence in publisher_candidates:
                for token in sequence:
                    normed_token = token.lower().translate(str.maketrans('', '', string.punctuation))
        
                    if normed_token in pub_ends:
                        matches.append(" ".join(sequence).lower())
                        break
                        
            self.publisher_candidates = Counter(matches)

    def map_candidates_to_entities(self):
        """
        1. Set keys with no values if no candidates 
        2. Map and score publisher matches
        3. Map and score author matches
        4. Map and score title matches
        5. Map and score whole book matches
        
        """
        pass
    
    def percentiles(self, mycounter):
        if len(mycounter.most_common()) > 0:
            a = list([i[0] for z in range(i[1])] for i in mycounter.most_common())
            flat_list = [item for sublist in a for item in sublist]
            results = {}
            for i in range(1000):
                shuffle(flat_list)
                try:
                    results[flat_list[0]] +=1
                except:
                    results[flat_list[0]] =1
            return Counter({i[0]:i[1]/1000 for i in results.items()})
        else:
            return Counter()
        
    def select_top_matches(self):
        """
        Return top publishers, titles, and authors thought to be the correct matches 
        """
        self.title_candidates = Counter(self.title_candidates)
        self.author_candidates = Counter(self.author_candidates)
        self.author_surname_candidates = Counter(self.author_surname_candidates)
        self.publisher_candidates = Counter(self.publisher_candidates)
        self.top_titles = self.percentiles(self.title_candidates)
        self.top_authors = self.percentiles(self.author_candidates)
        self.top_author_surnames = self.percentiles(self.author_surname_candidates)
        self.top_publishers = self.percentiles(self.publisher_candidates)
        

    def __repr__(self):
        return "Review Object titled '%s' with the following instance variables: %s " % (self.title, "'"+"', '".join(self.__dict__.keys())+"'")
    
        