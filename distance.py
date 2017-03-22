__all__ = ["arrayForChar","getCharacterCoord","euclideanKeyboardDistance",
            "find_bigrams","distance_list","distance_list_sqr","mean_KBD",
            "median_KBD","rms_kbdScore","stdev_score","pw_length","vowel_count",
            "cons_count","letter_count","caps_count","lowerC_count","num_count",
            "symbol_count","checksum","VowCon_ratio","VowLen_ratio","NumLet_ratio",
            "symbol_ratio","case_ratio","KBD_risk","moving_average","cleanPW",
            "calculate_entropy"
            ]

import re
import numpy as np
import pandas as pd 
from math import log, pow

SHIFT_COST = 3.0
qwertyKeyboardArray = [
    ['`','1','2','3','4','5','6','7','8','9','0','-','='],
    ['q','w','e','r','t','y','u','i','o','p','[',']','\\'],
    ['a','s','d','f','g','h','j','k','l',';','\''],
    ['z','x','c','v','b','n','m',',','.','/'],
    ['', '', ' ', ' ', ' ', ' ', ' ', '', '^Q^Q']
    ]

qwertyShiftedKeyboardArray = [
    ['~', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')','_', '+'],
    ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '{', '}', '|'],
    ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ':', '"'],
    ['Z', 'X', 'C', 'V', 'B', 'N', 'M', '<', '>', '?'],
    ['', '', ' ', ' ', ' ', ' ', ' ', '', '']
    ]

layoutDict = {'QWERTY': (qwertyKeyboardArray, qwertyShiftedKeyboardArray)}

keyboardArray = qwertyKeyboardArray
shiftedKeyboardArray = qwertyShiftedKeyboardArray

def arrayForChar(c):
    if (True in [c in r for r in keyboardArray]):
        return keyboardArray
    elif (True in [c in r for r in shiftedKeyboardArray]):
        return shiftedKeyboardArray
    else:

        raise ValueError("|"+ c +"|" + " not found in any keyboard layouts")


def getCharacterCoord(char, array):
    row_loc = -1
    column_loc = -1
    for row in array:
        if char in row:
            row_loc = array.index(row)
            column_loc = row.index(char)
            return (row_loc, column_loc)
    raise ValueError(char + " not found in given keyboard layout")

def euclideanKeyboardDistance(char1, char2):
    coord1 = getCharacterCoord(char1, arrayForChar(char1))
    coord2 = getCharacterCoord(char2, arrayForChar(char2))
    if arrayForChar(char1) == arrayForChar(char2):
        return ((coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2)**(0.5)
    else:
        return (((coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2)**(0.5))+SHIFT_COST        
    
    
def find_bigrams(input_list):
    bigram_list = []
    for i in range(len(input_list)-1):
        bigram_list.append((input_list[i], input_list[i+1]))
    return bigram_list

def distance_list(i):
    cost_list=[]
    bigram_list=find_bigrams(i)
    for bigram in list(bigram_list):
        cost_list.append(euclideanKeyboardDistance(*bigram))
    return cost_list
    
def distance_list_sqr(i):
    cost_list=[]
    bigram_list=find_bigrams(i)
    for bigram in list(bigram_list):
        cost_list.append((euclideanKeyboardDistance(*bigram))**2)
    return cost_list


def mean_KBD(password):
    n=distance_list(password)
    return np.mean(n)

def median_KBD(password):
    n=distance_list(password)
    return np.median(n)

def rms_kbdScore(password):
    n=(distance_list(password))
    m=np.sqrt(np.mean(n))
    return m

#this is an experiment, it's unclear if this will provide more accurate scoring
def stdev_score(password):
    st=np.std(distance_list(password))
    return st
    
    
#overall length
def pw_length(password):
    pw=password
    length=len(pw)
    return length
#vowel count
def vowel_count(password):
    vowels=findall('[aeiouyAEIOUY]',password)
    return len(vowels)
#consonant count
def cons_count(password):
    consonants= findall('[bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ]',password)
    return len(consonants)
#letter count
def letter_count(password):
    letters= findall('[a-zA-Z]',password)
    return len(letters)
#capital letters count
def caps_count(password):
    letters= findall('[A-Z]',password)
    return len(letters)
#lower case letters count
def lowerC_count(password):
    letters=findall('[a-z]',password)
    return len(letters)
#number count    
def num_count(password):
    numbers= findall('[0-9]',password)
    return len(numbers)
#symbol count   
def symbol_count(password):
    symbols=findall('[#$%=@!{},`~&*()\'<>?.:;_|^/\+\']',password)
    return len(symbols)
#check sum to ensure symbol_count performs correctly    
def checksum(password):
    check= letter_count(password)+num_count(password)+symbol_count(password)
    return check
  
    
#vowel to consonant ratio
def VowCon_ratio(password):
    vowels= vowel_count(password)
    consonants= cons_count(password)
    if vowels==0:
#        ratio="no vowels"
        ratio=0
    elif consonants>0:
        ratio =vowels/consonants

    else:
#        ratio = "no consonants"
        ratio = ""
    return ratio
#vowel to length ratio
def VowLen_ratio(password):
    vowels= vowel_count(password)
    length=pw_length(password)
    if vowels>0:
        ratio = vowels/length
    else:
#        ratio = "no vowels"
        ratio = 0        
    return ratio
#numbers to letters ratio
def NumLet_ratio(password):
    letters= letter_count(password)
    numbers= num_count(password)
    if letters==0:
#        ratio = 'no letters'
        ratio = 0
    elif numbers>0:
        ratio=numbers/letters
    else:
#        ratio='no numbers'
        ratio=0
    return ratio

def symbol_ratio(password):
    symbols= symbol_count(password)
    PWlength= pw_length(password)
    if symbols>0:
        ratio=symbols/PWlength
    else:
        ratio=0
    return ratio

def case_ratio(password):
    lowers=lowerC_count(password)
    uppers=caps_count(password)
    if letter_count(password)==0:
#        return 'no letters'
        ratio = 0    
    elif uppers == 0:
        ratio = 0
    elif lowers>0:
        ratio=uppers/lowers
    else:
#        ratio= "all caps"
        ratio= 0
    return ratio

def KBD_risk(password):
    m = average_score(password)
    st=stdev_score(password)
    score =(m*st)/2
    return score

def moving_average(a, n=3) :
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n


def cleanPW(password):
    l = []
    for c in password:
        if c not in ['ª','»','é','¼','©']:
            l.append(c)
    return str(''.join(l))

# regex's for entropy
numeric=re.compile('\d')
loweralpha=re.compile('[a-z]')
upperalpha=re.compile('[A-Z]')
symbols=re.compile('[-_.:,;<>?"#$%&/()!@~]')
num_of_symbols=20 



def calculate_entropy(password):
    charset = 0
    if numeric.search(password):
        charset += 10
    if loweralpha.search(password):
        charset += 26
    if upperalpha.search(password):
        charset += 26
    if symbols.search(password):
        charset += num_of_symbols
    try: 
        entropy = log(pow(charset,len(password)),2)
    except(ValueError):
        entropy = log(pow(20,len(password)),2)
    return entropy

# this works but I think it needs more tunning 
# guess = .010
# attackCores = 100 # number of cores guessing in parallel.

# guessTime = guess / attackCores


# def entropy_time(entropy):
#     return (0.5 * math.pow(2, entropy)) * guessTime
      
COMMON_PW = 369648
