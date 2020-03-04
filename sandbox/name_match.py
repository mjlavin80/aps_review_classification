import pandas as pd 
from collections import Counter
import re



def title_cleanup(string):
    lowered = string.lower().split('|')[0]
    new = "".join([u for u in lowered if u.isalpha() or u == ' '])
    return " ".join(new.split()[0:6])

def author_cleanup(string):
    lowered = string.lower().split('|')[0]
    no_parens = re.sub("\(.+?\)", "", lowered)
    no_parens = no_parens.rstrip(',')
    no_parens = no_parens.rstrip(' ')
    no_parens = no_parens.replace('.', '')
    no_parens = no_parens.replace('[', '')
    no_parens = no_parens.replace(']', '')
    #split on comma, make first last
    split = no_parens.split(',')
    if type(split) == list:
        head = split[0:1]
        tail = split[1:]

        final = " ".join(tail+head)
    else:
        final = split
    return final 

def author_cleanup_last(string):
    lowered = string.lower().split('|')[0]
    no_parens = re.sub("\(.+?\)", "", lowered)
    no_parens = no_parens.rstrip(',')
    no_parens = no_parens.rstrip(' ')
    no_parens = no_parens.replace('.', '')
    no_parens = no_parens.replace('[', '')
    no_parens = no_parens.replace(']', '')
    #split on comma, make first last
    split = no_parens.split(',')
    if type(split) == list:
        
        return split[0]
    else:
        return split

def author_cleanup_first(string):
    lowered = string.lower().split('|')[0]
    no_parens = re.sub("\(.+?\)", "", lowered)
    no_parens = no_parens.rstrip(',')
    no_parens = no_parens.rstrip(' ')
    no_parens = no_parens.replace('.', '')
    no_parens = no_parens.replace('[', '')
    no_parens = no_parens.replace(']', '')
    #split on comma, make first last
    split = no_parens.split(',')
    if type(split) == list:
        first = split[-1].split()
        try:
            return first[0]
        except:
            return split[-1]
    else:
        return split

#get author and title list
df_pre = pd.read_csv('fiction_metadata.csv', dtype={'oclc':'str','recordid':'str', 'datetype': 'str', 'startdate':'str' }).fillna('')
df_pre = df_pre.loc[df_pre['date'].isin([str(u) for u in range(1878, 1926)])].reset_index(drop=True)

df_post = pd.read_csv('fiction_metadata_post_1923.csv', dtype={'metadatasuspicious':'str'}).fillna('')
df_post = df_post.loc[df_post['inferreddate'].isin([str(u) for u in range(1923, 1928)])].reset_index(drop=True)

df_all = df_pre[['author', 'title', 'date']]
df_post_new = df_post[['author', 'title', 'inferreddate']]
df_post_new.rename(columns={'inferreddate':'date'}, inplace=True)
df_all = df_all.append(df_post_new)

#first five/six words, lowercase, remove special characters and punctuation
df_all['title'] = df_all['title'].apply(title_cleanup)
df_all['author_last'] = df_all['author'].apply(author_cleanup_last)
df_all['author_first'] = df_all['author'].apply(author_cleanup_first)
df_all['author_full'] = df_all['author'].apply(author_cleanup)

#dedupe on author, title
df_all = df_all.drop_duplicates(['author_full', 'title']).reset_index(drop=True)

authors_by_last_name = {}

#make a dictionary of lastnames
for row in df_all.iterrows():
    #make the value a list of first_names (ignore any that are one letter)
    if len(row[1]['author_first']) > 2:
        try:
            author = authors_by_last_name[row[1]['author_last']]
            if row[1]['author_first'] not in authors_by_last_name[row[1]['author_last']]:
                if row[1]['author_first'] != row[1]['author_last']:
                    authors_by_last_name[row[1]['author_last']].append(row[1]['author_first'])
        except:
            authors_by_last_name[row[1]['author_last']] = [row[1]['author_first']]

solo_names = {}
for name in authors_by_last_name.keys():
    if len(authors_by_last_name[name]) == 1:
        solo_names[name] = authors_by_last_name[name][0]

def find_top_author(text, name_dict):
    """ This function looks at a block of text, possibly a book review, and 
    uses a dictionary of names to find the top first name and last name pair 
    mentioned in the text. A statistical method for name inference would probably 
    be preferable to this method"""
    #Note: this function needs a lot of work!!!

    # 1. titles list is incomplete
    # 2. assumes surname will be one word
    # 3. returns empty if top last name not in author names dictionary 
    # 4. returns empty if the last name is found but the first name isn't
    # 5. code to choose the most frequently mentioned last name / first name pair might be coded wrong
    # 6. current not check 
    # 7. has no fuzziness ... in the example review we have "Lucien Carr", "Mr. Carr", "and "Ldclen Carr"
    # So the algorithm could theoretically resolve to Lucien Carr since that's a name and Ldclen isn't
    # Lucien Carr isn't in the author names dictionary but we could program this to find top names not in the dict

    #get the most frequent mr or mrs., miss, dr in the review 
    #and all the characters after the honorific until the next space (non-greedy)    
    results = re.findall('dr\. .+? |rev\. .+? |miss .+? |mr\..+? |mrs\..+? ', text.lower())
    
    #remove possessives
    results = [word.replace("'s", "") for word in results]
    print(results)

    if len(results) > 0:
        top = Counter(results).most_common(1)
        
        #oof, this is ugly
        lastname = top[0][0].replace(',', '').replace('miss ', '').replace('mrs. ', '').replace('mr. ', '').replace('dr. ', '').replace('rev. ', '').replace('"', '').replace('.', '').rstrip(" ")    
            
        #get authors with same last name
        first_name_results = []
        try:
            au_first_names = authors_by_last_name[lastname]
            
            for au_name in au_first_names:
                first_name_matches = re.search(au_name, text.lower())
                if first_name_matches:
                    first_name_results.append(au_name)
            if len(first_name_results) > 0:
                topfirst = Counter(first_name_results).most_common(1)
                
                firstname = topfirst[0][0]
                
            else:
                firstname = ''
        except:
            firstname = ''
        if firstname == '':
        	for i in both:
        		first_name_matches = re.search(i, text.lower())
        		if first_name_matches:
                    first_name_results.append(i)
            
        #match a first name or pass
        if len(lastname) > 4:
            return [lastname, firstname]
        else:
            return ["no match", "no match"]

if __name__ == '__main__':
    mytext = """
    Missouri: A Bone of Contention '                 WE  aware that most of the States of the Union had their nicknames, more or less complimentary, but to name Missouri ' a bone of contention ' is a stroke of wit. It does, however, rightly describe the Missouri of the past, and vividly writes in a phrase her political history. Until the triumph of the Union armies and the close of the Civil War, Missouri was in the jaws of the watch-dogs of slavery and freedom. In war or in peace, the subiect of legislative com-                 promise or of military struggle, Missouri was an uncertain factor. Now, after -five years of national peace, her history may be calmly and impartially written. Indeed, the task has been done, and well done, and the , Lucien Carr of Harvard, may be congratulated upon his work,  is strong, unimpassioned, scholarly, and as impressed with the firm touch which comes of local knowledge as are the imprinted rocks in the cabinets at Cambridge. Long familiarity with the wealth of archaeology in the Peabody Museuml seems to have given him the power of comparison and generalization in the evolution of a commonwealth, while  acquaintance with living men enables him to blend the results of the study and the field in pleasing literary form. Five of his seventeen chapters give a luminous picture of the early French and Spanish discoveries and domination. Then follow three chapters treating of the                 Missouri. By Ldclen Carr. $ti... (American Commonwealths.) Boston:                 Itoughto., Sftfltn & Co.                 l , the compromise, and the  into the U nion of this State named after the great river which flows through it. In his treatment of the period from 1844 to i861, as well as that of war time, some readers may charge Mr. Carr with unduly favoring the Southern and even Confederate view; but to people living this side of the now-vanished Mason and Dixon's line, this is doubtless a benefit; for only when Northern people are able to ' put themselves in the place' of Southerners and see with Southern eyes, can they be sure that they have achieved that impartiality which is essential to the writing of final history. He shows that the Missourians were neither secessionists nor slavery propagandists. He both criticises and justifies the action of the second convention which, in the uncertain hours when other States  seceding and Missouri's Governor had been driven into exile, org  a provisional government, and  saved Missouri Irons ' the pit of political degradation into which the States in rebellion were sunk during the period of reconstruction.' Mr. Carr practically and almost abruptly ends his history at the close of the War, believing that the career of Missouri as a bone of contention ended with the abolition of slavery. The fifty years' struggle was over, the State recovered rapidly froni the wounds of the Civil War, wealth increased wonderfully, and the Negro was liberally dealt with in most if not all points relating to citizenship. Taken as a whole, this book, with its sustained interest, high average literary merit, and thorough treatment of the voluminous facts, fully justifies its place in the series of ' histories of such States as have exercised a positive influence in the shaping of the national Government, or have had a striking political - . . history.' Like the others, it has a good map and index.                         
    """
    print(find_top_author(mytext, authors_by_last_name))


