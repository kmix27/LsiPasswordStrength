from gensim import corpora, models, similarities, matutils
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import pickle
import json
import re
import os
from .distance import *

__all__ = ["char_freq","dataset_features","build_models",
            "save_models","open_models","openjson","savejson",
            "build_existing","rebuild_dataset"
            ]
# options:
#open the char freq and stats as I have it from json
#rebuild from new dataset
#
#
#
#

numeric=re.compile('\d')
loweralpha=re.compile('[a-z]')
upperalpha=re.compile('[A-Z]')
symbols=re.compile('[-_.:,;<>?"#$%&/()!@~]')

def char_freq(dataset):
    '''calculates the frequency of passwords in the dataset.
    dataset = pandas dataframe with column password which contains all passwords
    return = dictionary of characters and their frequency in all passwords in the dataset'''
    d={}
    for pw in dataset.password:
        if type(pw) == float:
            pass
        else:
            for char in pw:
                if char in d:
                    d[char] += 1
                else:
                    d[char] = 1
    return d

def dataset_features(dataset, filename):
    '''
    dataset = a pandas dataframe with a password column
    filename = text of file name without extension
    return =  dict of dataset features
    '''
    kbd_m = dataset.password.map(mean_KBD).mean()
    kbd_s = dataset.password.map(mean_KBD).std()
    ent = dataset.password.map(calculate_entropy)
    ent_m = ent.mean()
    ent_s = ent.std()
    leng = dataset.password.map(len)
    len_m = leng.mean()
    len_s = leng.std()
    lwr_prp = dataset.password.map(lambda x: len(loweralpha.findall(x))/len(x))
    lwr_prp_m = lwr_prp.mean()
    lwr_prp_s = lwr_prp.std()
    lwr_cnt = dataset.password.map(lambda x: len(loweralpha.findall(x)))
    lwr_cnt_m = lwr_cnt.mean()
    lwr_cnt_s = lwr_cnt.std()
    upr_prp = dataset.password.map(lambda x: len(upperalpha.findall(x))/len(x))
    upr_prp_m = upr_prp.mean()
    upr_prp_s = upr_prp.std()
    upr_cnt = dataset.password.map(lambda x: len(upperalpha.findall(x)))
    upr_cnt_m = upr_cnt.mean()
    upr_cnt_s = upr_cnt.std()
    sym_prp = dataset.password.map(lambda x: len(symbols.findall(x))/len(x))
    sym_prp_m = sym_prp.mean()
    sym_prp_s = sym_prp.std()
    sym_cnt = dataset.password.map(lambda x: len(symbols.findall(x)))
    sym_cnt_m = sym_cnt.mean()
    sym_cnt_s = sym_cnt.std()
    num_prp = dataset.password.map(lambda x: len(numeric.findall(x))/len(x))
    num_prp_m = num_prp.mean()
    num_prp_s = num_prp.std()
    num_cnt = dataset.password.map(lambda x: len(numeric.findall(x)))
    num_cnt_m = num_cnt.mean()
    num_cnt_s = num_cnt.std()
    features  = dict(lwr_prp_m=lwr_prp_m,lwr_prp_s=lwr_prp_s,
                    lwr_cnt_m=lwr_cnt_m,lwr_cnt_s=lwr_cnt_s,
                    upr_prp_m=upr_prp_m,upr_prp_s=upr_prp_s,
                    upr_cnt_m=upr_cnt_m,upr_cnt_s=upr_cnt_s,
                    sym_prp_m=sym_prp_m,sym_prp_s=sym_prp_s,
                    sym_cnt_m=sym_cnt_m,sym_cnt_s=sym_cnt_s,
                    num_prp_m=num_prp_m,num_prp_s=num_prp_s,
                    num_cnt_m=num_cnt_m,num_cnt_s=num_cnt_s,
                    kbd_m=kbd_m,kbd_s=kbd_s,
                    ent_m=ent_m,ent_s=ent_s,
                    len_m=len_m,len_s=len_s, filename=filename)
    return features


def build_models(dataset, n_grams=(1,4),max_features=15000, num_topis=500):
    '''
    builds up the models used for similarity 
    returns in this order :
    tfidf model
    lsi model
    matrix similarity index
    list of input documents  
    '''
    input_documents = list(dataset.password.values)
    tfidf4 = TfidfVectorizer(analyzer='char',lowercase=False,ngram_range=n_grams, max_features=max_features)
    vecs4 = tfidf4.fit_transform(input_documents)
    tfidf_corpus4 = matutils.Sparse2Corpus(vecs4.transpose())
    id2word4 = dict((v, k) for k, v in tfidf4.vocabulary_.items())
    id2word4 = corpora.Dictionary.from_corpus(tfidf_corpus4, 
                                     id2word=id2word4)
    lsi4 = models.LsiModel(tfidf_corpus4, id2word=id2word4, num_topics=num_topis)
    lsi_corpus4 = lsi4[tfidf_corpus4]
    doc_vecs4 = [doc for doc in lsi_corpus4]
    index4 = similarities.MatrixSimilarity(doc_vecs4, 
                                  num_features=len(id2word4))
    return tfidf4, lsi4, index4, input_documents


def save_models(tfidf,lsi,index,input_documents):
    '''
    helper to save the results of build_models
    '''
    with open(os.path.expanduser('~/.lsipw/models/tfidf.pkl'),'wb') as idf_mod:
        pickle.dump(tfidf, idf_mod)
    lsi.save(os.path.expanduser('~/.lsipw/models/lsi.model'))
    index.save(os.path.expanduser('~/.lsipw/models/index.model'))
    with open(os.path.expanduser('~/.lsipw/models/input_documents.txt'),'w') as dox:
        dox.write(str(input_documents))


def open_models():
    '''
    Helper to open saved models from the dot files
    '''

    with open(os.path.expanduser('~/.lsipw/models/tfidf.pkl'),'wb') as idf_mod:
        tfidf = pickel.load(tfidf, idf_mod)
    lsi = models.LsiModel.load(os.path.expanduser('~/.lsipw/models/lsi.model'))
    index = similarities.MatrixSimilarity.load(os.path.expanduser('~/.lsipw/models/index.model'))
    with open(os.path.expanduser('~/.lsipw/models/input_documents.txt'),'r') as dox:
        input_documents = eval(dox.read())
    return tfidf, lsi, index, input_documents

def openjson():
    '''
    helper to open json files
    returns character_frequencies, dataset_stats
    '''
    with open(os.path.expanduser('~/.lsipw/data/char_freq.json'),'r') as f:
        freq = json.load(f)
    with open(os.path.expanduser('~/.lsipw/data/set_stats.json'),'r') as s:
        stats = json.load(s)
    return freq , stats

def savejson(freq, stats):
    '''
    helper to save the freq and stats dicts created by 
    dataset_stats() and char_freq()
    '''
    with open(os.path.expanduser('~/.lsipw/data/char_freq.json'),'w') as cf:
        json.dump(freq,cf)
    with open(os.path.expanduser('~/.lsipw/data/set_stats.json'),'w') as ss:
        json.dump(stats,ss)



def build_existing(filename, rebuild_models=False):
    '''
    opens existing files and models
    filename = top_n dataset ex: n30000.csv
    rebuild models flag default false true will rebuild and save 
    the modeling on the dataset
    returns in this order :
    top_n df, df_stats, char_freq, tfidf model, lsi model, matrix sim index, input_documentslist
    '''
    df = pd.read_csv(os.path.expanduser('~/.lsipw/data/'+filename))
    freq, stats = openjson()
    if rebuild_models == True:
        tfidf, lsi, index, input_documents = build_models(dataset=df)
        save_models(tfidf,lsi,index, input_documents)
    elif rebuild_models==False:
        tfidf, lsi, index, input_documents = open_models()
    return df, stats, freq, tfidf, lsi, index, input_documents



def rebuild_dataset(filename,top_n,file_type, fullDF=False):
    '''
    starts from scratch, builds models saves and all of the things
    filename = password file name, no extension
        if .csv file_type = csv
            csv file must be two columns
            col 1 is username, col 2 is password
        if .txt filetype = txt
            file must not have a header
            file must be tab delimited
    returns 7 objects in order:
        tfidf model, lsi model , matrix sim index, car freq dict, dataset stats, top_n df , input_documents list
    fullDF True adds to the end of those returns the full password repo * returns total
    '''
    if file_type == 'csv':
        df = pd.read_csv(os.path.expanduser('~/.lsipw/data/' + filename + '.csv'))
    elif file_type == 'txt':
        df = pd.read_csv(os.path.expanduser('~/.lsipw/data/'+ filename + '.txt'),header=None,delimiter='\t')
    else:
        raise ValueError('unsupported file type {}'.format(filetype))
    df.columns = ['username', 'password']
    pw_vc = df.password.value_counts()
    pw_vc = pw_vc.reset_index()
    pw_vc.columns = ['password', 'freq']
    pw_vc['password'] = pw_vc.password.map(cleanPW)
    df_top = pw_vc.head(top_n)
    csvsave = 'n'+str(top_n)
    df_top.to_csv(os.path.expanduser('~/.lsipw/data/'+csvsave+'.csv'))
    freq = char_freq(df_top)
    stats = dataset_features(df_top,csvsave)
    savejson(freq,stats)
    tfidf, lsi, index, input_documents = build_models(dataset=df_top)
    save_models(tfidf,lsi,index, input_documents)
    if fullDF == True:
        return tfidf, lsi, index, freq, stats, df_top, input_documents, df
    return tfidf, lsi, index, freq, stats, df_top ,input_documents



