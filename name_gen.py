from nameparser import HumanName
import pandas as pd
from itertools import combinations
from itertools import permutations
import jellyfish as jf
import random as rm

f = open('names.txt','r+')
f_out = open('names_out.txt','w+')
f_dict_out = open('names_dict_out.txt','w+')

f_list = f.readlines()
sampleNumber = 8

#levenstein distance of 1
def edits1(word):
    "All edits that are one edit away from `word`."
    letters    = 'abcdefghijklmnopqrstuvwxyz'
    des_set = ()
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    deletes    = [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters]
    unchanged = [word]
    
    des_set += ('unchanged',)
    des_set += ('lev1_del',)*len(deletes)
    des_set += ('lev1_trans',)*len(transposes)
    des_set += ('lev1_replaces',)*len(replaces)
    des_set += ('lev1_trans',)*len(transposes)
    des_set += ('lev1_inserts',)*len(inserts)

    
    return set(unchanged+ deletes + transposes + replaces + inserts), des_set

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

lev1_des_set = ()
symb_des_set =()
names_dict_sampled={}
for name_org in f_list:
    name_org = name_org.strip()
    print(name_org)
    
    #keep the original metaphone
    metaphone_name_org = jf.metaphone(name_org)
    metaphone_name_org_set = metaphone_name_org.split(' ')

    #generate list of dict
    temp_words,lev1_des_set = edits1(name_org)
    
    set_pos = 0
    #keep the original keys
    org_keys = []

    #the original sequence
    name_org_json = HumanName(name_org)
    name_org_dict_org = name_org_json.as_dict()
    keys_org = name_org_dict_org.keys()
    name_org_dict={}

    #keep all the variations of the same name_org
    name_dict_population={}
    
    #cleansed the dict
    for key in keys_org:
        if len(name_org_dict_org[key].strip()) > 0:
            name_org_dict[key] = name_org_dict_org[key]
    name_org_keys = list(name_org_dict.keys())

        
    for name in temp_words:
        name_n_list = []
        des_n_list = []        
        
        name_n_list.append(name)
        des_n_list.append(lev1_des_set[set_pos])

        #replace space by symbol
        symb_cnt = name.count(' ')+name.count('-')
        for cnt in range(1,symb_cnt+1):
            
            name_2 = nth_repl(name,' ','-',cnt)
            if name_2 not in name_n_list:
                name_n_list.append(name_2)
                des_n_list.append((lev1_des_set[set_pos],'symb_rep'))
            
            name_3 = nth_repl(name,' ','',cnt)
            if name_3 not in name_n_list:
                name_n_list.append(name_3)
                des_n_list.append((lev1_des_set[set_pos],'symb_rep'))

            name_4 = nth_repl(name,'-',' ',cnt)
            if name_4 not in name_n_list:
                name_n_list.append(name_4)
                des_n_list.append((lev1_des_set[set_pos],'symb_rep'))
            
            name_5 = nth_repl(name,'-','',cnt)
            if name_5 not in name_n_list:
                name_n_list.append(name_5)
                des_n_list.append((lev1_des_set[set_pos],'symb_rep'))

            #print(name_n_list)
            name_n_pos = 0
            for name_n in name_n_list:
                #print(name_n)
                des_n = des_n_list[name_n_pos]
                #print(str(des_n))
                
                name_json = HumanName(name_n)
                name_dict_org = name_json.as_dict()
                keys = name_dict_org.keys()
                name_dict = {}
                
                #cleansed the dict
                for key in keys:
                    if len(name_dict_org[key].strip()) > 0:
                        name_dict[key] = name_dict_org[key]

                name_keys = list(name_dict.keys())
                #if name_n_pos == 0 and set_pos==0:
                #    org_keys=name_keys
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
                        is_metaphone_mismatch = 0
                        metaphone_out_words = jf.metaphone(out_words)
                        metaphone_out_words_set = metaphone_out_words.split(' ')
                        for metaphone_out in metaphone_out_words_set:
                            if metaphone_out not in metaphone_name_org:
                                is_metaphone_mismatch+=1
                        output_txt = name_org+'\t'+out_words+'\t'+metaphone_name_org+'\t'+metaphone_out_words+'\t'+str(name_keys)+'\t'+str(name_org_keys)+'\t'+str(des_n)+'\t'+str(is_metaphone_mismatch)+'\t'+str(name_keys==name_org_keys)
                        dict_output_txt = {'name_org': name_org,'out_words': out_words,'metaphone_name_org': metaphone_name_org,'metaphone_out_words': metaphone_out_words,'name_keys': str(name_keys),'name_org_keys': str(name_org_keys),'des_n': str(des_n),'is_metaphone_mistmatch':str(is_metaphone_mismatch), 'seq_unchanged':str(name_keys==name_org_keys)}
                        name_dict_population[out_words] = dict_output_txt
                        f_out.write(output_txt+'\n')
                name_n_pos+=1
        set_pos+=1
    names_dict_sampled[name_org] = rm.sample(name_dict_population.items(), k=sampleNumber)
    f_dict_out.write(str(names_dict_sampled[name_org])+'\n')
f_out.close()
f_dict_out.close()

#df = pd.DataFrame.from_dict(names_dict_sampled, orient='index')

#output the result to dataframe
org_key = names_dict_sampled.keys()
entryCnt=0

for key in org_key:
    org_name_out = pd.Series(key)
    alterList = names_dict_sampled[key]
    for entry in alterList:
        amend_name_out = pd.Series(entry[0])
        temp_pd = pd.DataFrame.from_dict(entry[1],orient='index').T
        #temp_pd = pd.concat([amend_des_out.T],axis=1)
        if entryCnt == 0:
            outpd = temp_pd
        else:
            outpd = pd.concat([outpd,temp_pd],axis=0)
        entryCnt+=1

outpd.to_csv(r'output.txt',sep='\t')
