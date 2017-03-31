import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
import seaborn as sns 
from re import findall
from sklearn.feature_extraction.text import TfidfVectorizer
from gensim import corpora, models, similarities, matutils
import re
from math import log,pow
import math
import pickle
from .distance import *
from .build_model import *

__all__=["similarityTest","testPW_lsi","runTest"]


COMMON_PW = 369648
tfidf=''
lsi=''
index=''
input_documents=''
input_documents =''


def similarityTest(testString, freqDF, tfidf_model=tfidf, lsi_model=lsi, input_documents=input_documents, index=index, max_sims=25):
    '''returns the top n simmilar passwords from the test password'''
    testString = [testString]
    test_vecs = tfidf_model.transform(testString)
    test_vecs_corp = matutils.Sparse2Corpus(test_vecs.transpose())
    lsi_test_corp = lsi_model[test_vecs_corp]
    testsims = sorted(enumerate(index[lsi_test_corp][0]), key=lambda item: -item[1])[0:max_sims]
    simMatrix = []
    for sim_doc_id, sim_score in testsims:
        data = []
        data.append(input_documents[sim_doc_id])
        data.append(sim_score)
        data.append(freqDF.iloc[sim_doc_id,1])
        simMatrix.append(data)
    return simMatrix


def testPW_lsi(test_password, bottom_thresh=.6, top_thresh=.85):
    freq_list = []
    for i in similarityTest(test_password):
        if i[1] > top_thresh:
            freq_list.append(i[2])
        if bottom_thresh < i[1] < top_thresh:
            freq_list.append(i[2]*i[1])
    if not freq_list:
        return 0
    return (sum(freq_list)/COMMON_PW)*100


def runTest(pw, base=False, verbose=False):
    tipsDict = {'similar':0, 'kbd':0, 'length':0, 'symbols':0, 'case':0, 'nums':0, 'lsi':0, 'KBD':0 }
    simi = '*** Try again, You are using a very common password***\n'
    KbD = '*** You have too many characters adjacent to each other on your keyboard \nexample: qwert or wsxedc \nhackers know that trick, try again for a better score ***\n'
    le = '*** That\'s a pretty short password, long passwords are exponentially harder to crack,  I know you can do it ***\n'
    symbo = '*** You might want to add a few more symbols,  that increases the difficulty for a hacker ***\n'
    cas = '*** Play around with upper and lower case, you\'ll have a stronger password for it ***\n'
    nu = '*** Computers love numbers! So does your score! \n give me some more numbers ***\n'
    base_entropy = calculate_entropy(pw)
    new_entropy = base_entropy
    commonality = testPW_lsi(pw)
    tipsDict['commonality'] = commonality
    if commonality == 0:
        new_entropy += 10
        tipsDict['similar'] = 10
    if commonality > .5:
        new_entropy -= (commonality+4)**2
        tipsDict['similar'] = '-'+str((lsi+4)**2)
    kbd = median_KBD(pw)
    tipsDict['KBD'] = kbd
    if kbd < 3:
        new_entropy -= (3-kbd)**2
        tipsDict['kbd'] = '-'+str((3-kbd)**2)
    if 7 <= len(pw) <= 9:
        new_entropy -= ((9-len(pw))**2)
        tipsDict['length'] = '-'+str(((9-len(pw))**2))
    if 5 <= len(pw) < 7:
        new_entropy -= ((7-len(pw)+1.3)**3)
        tipsDict['length'] = '-'+str(((7-len(pw)+1.3)**3))
    if len(pw) > 10:
        new_entropy +=(len(pw)-2)
        tipsDict['length'] = (len(pw)-2)
    sym_rat = symbol_ratio(pw)
    if sym_rat < .15:
        new_entropy -= 8
        tipsDict['symbols'] = 1
    if sym_rat > .4:
        new_entropy += 10
        tipsDict['symbols'] = 10
    case_rat = case_ratio(pw)
    if case_rat < .15:
        new_entropy -= 10
        tipsDict['case'] = '-10'
    if .4 < case_rat < .8:
        new_entropy += 10
        tipsDict['case'] = 10
    num_rat = NumLet_ratio(pw)
    if num_rat < .15:
        new_entropy -=10
        tipsDict['nums'] = '-10'
    if .4 > num_rat > .8:
        new_entropy += 10
        tipsDict['nums'] = 10
    if new_entropy<0:
        new_entropy = 0
    if new_entropy > 250:
        new_entropy = 250
    if new_entropy > 125:
        print('You have a very strong password!')
    if new_entropy < 90 and tipsDict['similar']!=0:
        print(simi)
    if new_entropy < 90 and tipsDict['kbd']!=0:
        print(KbD)
    if new_entropy < 90 and tipsDict['length']!=0:
        print(le)
    if new_entropy < 90 and tipsDict['case']!=0:
        print(cas)
    if new_entropy < 90 and tipsDict['nums']!=0:
        print(nu)
    print('\nYour score out of 250 was:', new_entropy)
    if base == True:
        print('\nBaseEntropy:', base_entropy)
    if verbose == True:
        print('\nPassword tested:',pw, '\nRules:',tipsDict)




