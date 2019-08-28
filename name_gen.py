from nameparser import HumanName
import pandas as pd
from itertools import combinations
from itertools import permutations
import jellyfish as jf

f = open('names.txt','r+')
f_out = open('names_out.txt','w+')

f_list = f.readlines()

#levenstein distance of 1
def edits1(word):
    "All edits that are one edit away from `word`."
    letters    = 'abcdefghijklmnopqrstuvwxyz'
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    deletes    = [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters]
    unchanged = [word]
    return set(deletes + transposes + replaces + inserts+ unchanged)

#replace the nth occurance of a string
def nth_repl(s, sub, repl, nth):
    find = s.find(sub)
    # if find is not p1 we have found at least one match for the substring
    i = find != -1
    # loop util we find the nth or we find no match
    while find != -1 and i != nth:
        # find + 1 means we start at the last match start index + 1
        find = s.find(sub, find + 1)
        i += 1
    # if i  is equal to nth we found nth matches so replace
    if i == nth:
        return s[:find]+repl+s[find + len(sub):]
    return s


for name_org in f_list:
    name_org = name_org.strip()
    print(name_org)

    #generate list of dict
    temp_words = edits1(name_org)
    
    for name in temp_words:
        name_n_list = []
        name_n_list.append(name)

        #replace space by symbol
        symb_cnt = name.count(' ')+name.count('-')
        for cnt in range(1,symb_cnt+1):
            
            name_2 = nth_repl(name,' ','-',cnt)
            if name_2 not in name_n_list:
                name_n_list.append(name_2)
            
            name_3 = nth_repl(name,' ','',cnt)
            if name_3 not in name_n_list:
                name_n_list.append(name_3)

            name_4 = nth_repl(name,'-',' ',cnt)
            if name_4 not in name_n_list:
                name_n_list.append(name_4)
            
            name_5 = nth_repl(name,'-','',cnt)
            if name_5 not in name_n_list:
                name_n_list.append(name_5)

            #print(name_n_list)
            for name_n in name_n_list:
                #print(name_n)
                name_json = HumanName(name_n)
                name_dict_org = name_json.as_dict()
                keys = name_dict_org.keys()
                name_dict = {}
                
                #cleansed the dict
                for key in keys:
                    if len(name_dict_org[key].strip()) > 0:
                        name_dict[key] = name_dict_org[key]

                name_keys = list(name_dict.keys())
                len_name_keys=len(name_keys)
                #print(name_dict)

                #word sequence swapped
                seq = list(range(0,len_name_keys))
                seq_type = name_keys
                len_seq = len(seq)
                perm = permutations(seq)
                symb = ' '
                out_words_list = []
                
                for seq in perm:
                    seq_print=('')
                    #each tuple
                    #print(seq)
                    out_words=''
                    for temp_key in seq:
                        name_dict_type = seq_type[int(temp_key)]
                        temp_word = name_dict[name_dict_type].strip()
                        seq_print = seq_print+ ('/'+name_dict_type)
                        if len(temp_word)>0:
                            if out_words == '':
                                out_words = temp_word
                            else:
                                out_words+= symb+temp_word
                    #print(out_words)
                    #print('***')
                    if out_words not in out_words_list:
                        out_words_list.append(out_words)
                        f_out.write(name_org+'\t'+out_words+'\t'+jf.metaphone(name_org)+'\t'+jf.metaphone(out_words)+'\t'+str(seq_print)+'\n')


f_out.close()
        

    #soundex
    #https://languages.oup.com/licensing-and-developers
