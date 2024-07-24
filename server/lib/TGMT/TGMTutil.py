import os
import re
import string
import random

####################################################################################################

def GenerateRandomString(length=10):
    return ''.join(random.choices(string.ascii_lowercase + "_" + string.ascii_uppercase +  string.digits, k=length))

####################################################################################################

def GenerateRandomNumber(min, max):
    n = random.randint(min, max)
    return n

####################################################################################################

def urlify(s):
    s = re.sub(r"[^\w\s]", '', s)
    s = re.sub(r"\s+", '-', s)
    return s

####################################################################################################

def GenerateRandomName(name):
    fileName, fileExt = os.path.splitext(name)
    fileName = urlify(fileName)
    return fileName + '.' + GenerateRandomString() + fileExt

####################################################################################################

def IsNumeric(string):
    if(type(string) == type(-1) or type(string) == type(1.0)):
        return True
    
    return bool(re.match(r'^-?\d+(?:\.\d+)?$', string))