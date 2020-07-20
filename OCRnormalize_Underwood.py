correction_rules = {}
with open('../data/CorrectionRules.txt') as f:
filelines = file.readlines()
for line in filelines:
    line = line.rstrip()
    fields = line.split("\t")
    correction_rules[fields[0]] = fields[1]

hyphen_rules = {}

with open('../data/HyphenRules.txt') as f:
    filelines = f.readlines()
    filelines.reverse()
    # Doing this so that unhyphenated forms get read before hyphenated ones.

for line in filelines:
    line = line.rstrip()
    fields = line.split("\t")
    Word = fields[0].rstrip()
    Corr = fields[1].rstrip()
    hyphen_rules[Word] = Corr
    if " " not in Corr:
        lexicon[Corr] = 1
    else:
        StripWord = Word.replace("-", "")
        hyphen_rules[StripWord] = Corr
        # That's so that we split "tigermoth" as well as "tiger-moth" into "tiger moth."
            
    if "-" in Word:
        StripWord = Word.replace("-", "")
        StripCorr = Corr.replace(" ", "")
        StripCorr = StripCorr.replace("-", "")
        if StripWord != StripCorr and StripWord not in hyphen_rules:
            hyphen_rules[StripWord] = Corr
            
        ## The purpose of this is a bit obscure to me. It may be deletable.

fuse_rules = dict()
with open('../data/FusingRules.txt') as f:
    filelines = f.readlines()
        
    for Line in filelines:
        Line = Line.rstrip()
        LineParts = Line.split(delim)
        Word = LineParts[0].rstrip()
        Word = tuple(Word.split(' '))
        Corr = LineParts[1].rstrip()
        fuse_rules[Word] = Corr

syncope_rules = {}
with open('../data/SyncopeRules.txt') as f:
    filelines = f.readlines()
        
    for line in filelines:
        line = line.rstrip()
        fields = line.split(delim)
        syncope_rules[fields[0]] = fields[1]

variant_rules = {}
with open('../data/VariantSpellings.txt') as f:
    filelines = f.readlines()
        
    for line in filelines:
        line = line.rstrip()
        fields = line.split(delim)
        variant_rules[fields[0]] = fields[1]

## End loading of rulesets.

## Each ruleset is basically a dictionary lookup with a substitution ... could be one big txt file and dictionary
        

            
                
                
            
            
    
