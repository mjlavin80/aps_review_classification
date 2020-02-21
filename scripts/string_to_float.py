def string_to_float(text):
    small = {
    'zero': 0,
    'one': 1,
    'two': 2,
    'three': 3,
    'four': 4,
    'five': 5,
    'six': 6,
    'seven': 7,
    'eight': 8,
    'nine': 9,
    'ten': 10,
    'eleven': 11,
    'twelve': 12,
    'thirteen': 13,
    'fourteen': 14,
    'fifteen': 15,
    'sixteen': 16,
    'seventeen': 17,
    'eighteen': 18,
    'nineteen': 19,
    'twenty': 20,
    'thirty': 30,
    'forty': 40,
    'fifty': 50,
    'sixty': 60,
    'seventy': 70,
    'eighty': 80,
    'ninety': 90 }
    if text == '4o' or text == '2o':
        return None
    try:
        newfloat = float(text)
        return newfloat
    except:
        try:
            text = text.replace('-', ' ').lower()
            tokens = text.split()
            if len(tokens) > 1:
                new = []
                for e, t in enumerate(tokens):
                    try:
                        if tokens[e+1] == 'cents':
                            new.append(int(t)*1.0/100)
                        else:
                            new.append(int(t))
                    except:
                        try: 
                            if tokens[e+1] == 'cents':
                                new.append(small[t]*1.0/100)
                            else:
                                new.append(small[t])
                        except:
                            pass
                newfloat = float(sum(new))
                
            else:
                tnew = text.replace('o', '0')
                tnew = tnew.replace('s.', '5.')
                tnew = tnew.replace('S.', '5.')
                tnew = tnew.replace('$s.', '$5.')
                tnew = tnew.replace('$S.', '$5.')
                tnew = [n for n in tnew if n.isdigit() or n == '.']
                newfloat = float(''.join(tnew))
            return newfloat
        except:
            return None
            
string_to_float("s.5o")