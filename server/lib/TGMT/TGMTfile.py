import os, fnmatch
import shutil
import threading
import datetime

from api.apps import printt
from .TGMTutil import GenerateRandomString
from django.conf import settings as raspango

def MkDir(dirPath):
    if not os.path.exists(dirPath):
        os.mkdir(dirPath)

def GetDirName(fullpath):    
    return GetFileName(fullpath)

def GetParentDirPath(fullpath):    
    return os.path.abspath(os.path.join(fullpath, os.pardir))

def GetParentDirName(fullpath):    
    return GetFileName(GetParentDirPath(fullpath))    

def GetPathWithoutExt(filePath):
    filePathWithouExt, ext = os.path.splitext(filePath)
    return filePathWithouExt

def GetFileName(filePath):
    fileName = os.path.basename(filePath)
    return fileName

def GetFileNameWithoutExt(filePath):
    fileName = GetFileName(filePath)
    fileNameWithoutExt, ext = os.path.splitext(fileName)
    return fileNameWithoutExt

def RemoveDir(dirPath):
    if(os.path.exists(dirPath)):
        shutil.rmtree(dirPath)

def RemoveFile(filePath):
    if(os.path.exists(filePath)):
        os.remove(filePath)

def RemoveFileAsync(filePath):
    t = threading.Thread(target=RemoveFile, args=(filePath,))
    t.start()

def GenerateRandFileName(ext):
    dateVN = datetime.datetime.utcnow() + datetime.timedelta(hours=7)
    return dateVN.strftime("%Y-%m-%d_%H-%M-%S") + "_" + GenerateRandomString() + ext

def ReadFile(filePath):
    content = ""
    with open(filePath, 'r') as f:
        content = f.read()
        f.close()

    return content

def WriteToFile(filePath, content):
    with open(filePath, 'w') as f:
        f.write(content)
        f.close()

def FindFileInDir(dirPath, pattern, fullPath=True, searchChildDir=False):
    result = []
    for fullpathDir, subdirs, files in os.walk(dirPath):
        isChildDir = len(fullpathDir) > len(dirPath)
        if(not searchChildDir and isChildDir):
            continue
        

        for fileName in files:            
            if fnmatch.fnmatch(fileName, pattern):
                if(fullPath):
                    result.append(os.path.join(fullpathDir, fileName))
                else:
                    currentDirName = fullpathDir.replace(raspango.MEDIA_ROOT, "")                    
                    result.append(os.path.join(currentDirName, fileName))

    return result


def GetChildDir(parent_dir):
    if(not os.path.exists(parent_dir)):
        return []
    return [name for name in os.listdir(parent_dir)
        if os.path.isdir(os.path.join(parent_dir, name))]
            
def RemoveDirIfEmpty(dirPath):
    filePaths = FindFileInDir(dirPath, "*.*", True, True)
    if(len(filePaths) == 0):
        RemoveDir(dirPath)