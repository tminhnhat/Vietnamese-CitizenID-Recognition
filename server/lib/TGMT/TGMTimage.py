from PIL import Image, ExifTags
from django.conf import settings as raspango
from django.core.files.storage import FileSystemStorage
import base64
import os
from lib.TGMT.TGMTfile import GetFileName
from lib.TGMT.TGMTutil import GenerateRandomString
import datetime
from api.apps import *



####################################################################################################

def ResizeImageByPath(imgPath, desireWidth):
    img = Image.open(imgPath)
    img = img.convert('RGB')
    
    width, height = img.size
    if(width > desireWidth):
        wpercent = (desireWidth/float(img.size[0]))
        hsize = int((float(img.size[1])*float(wpercent)))
        img = img.resize((desireWidth,hsize))
        img.save(imgPath)
    img.close()

    return True

####################################################################################################


def ResizeImage(imgPath, desireWidth):
    img = Image.open(imgPath)
    width, height = img.size
    if(width > desireWidth):
        wpercent = (desireWidth/float(img.size[0]))
        hsize = int((float(img.size[1])*float(wpercent)))
        img = img.resize((desireWidth,hsize), Image.ANTIALIAS)
        img.save(imgPath)
    img.close()

    if(width < raspango.FACE_MIN_SIZE):
        return False
    return True

####################################################################################################

def RotateImageWithExif(imgPath):
    try:
        image=Image.open(imgPath)
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation]=='Orientation':
                break
        exif=dict(image._getexif().items())

        if exif[orientation] == 3:
            image=image.rotate(180, expand=True)
        elif exif[orientation] == 6:
            image=image.rotate(270, expand=True)
        elif exif[orientation] == 8:
            image=image.rotate(90, expand=True)
        image.save(imgPath)
        image.close()

    except (AttributeError, KeyError, IndexError):
        # cases: image don't have getexif
        pass
    return True

####################################################################################################
#return true if has new image
def SaveImageFromRequest(request, saveDir, fileName = None):
    if(fileName == None):
        fileName = (utcnow() + datetime.timedelta(hours=7)).strftime("%Y-%m-%d_%H-%M-%S") + "_" + GenerateRandomString() + ".jpg"

    _imageBase64 = GetParam(request, "imageBase64")

    if(_imageBase64 != None and _imageBase64 != ""):                
        return SaveBase64ToImg(saveDir, fileName, _imageBase64)

    elif (request.method == 'POST' and "selectedFile" in request.FILES):     
        #upload only 1 image
        uploadfile = request.FILES['selectedFile']
        upload_folder_abs = os.path.join(raspango.MEDIA_ROOT, saveDir)
        fs = FileSystemStorage(upload_folder_abs, raspango.MEDIA_URL)
        fs.save( fileName, uploadfile)
        filePath = os.path.join(saveDir, fileName)
        filePathAbs = os.path.join(raspango.MEDIA_ROOT, filePath)
        PreprocessImage(filePathAbs)
        return [filePath]
    return []
    

####################################################################################################

def SaveBase64ToImg(folder_name, file_name, imageData):    
    if(imageData == None or imageData == "" ):
        raise Exception("Thiếu data ảnh")

    filePaths = []

    upload_folder_abs = os.path.join(raspango.MEDIA_ROOT, folder_name)
    if not os.path.exists(upload_folder_abs):
        os.makedirs(upload_folder_abs)

    has_multiple_images = True if imageData.count("|") > 1 else False
    imageData = imageData.replace(" ", "+")
    imageData = imageData.replace("data:image/jpeg;base64,", "")
    imageData = imageData.replace("data:image/png;base64,", "")
    if has_multiple_images:
        imageData = imageData.split("|")

    if has_multiple_images:
        for img in imageData:
            if(len(img) == 0):
                continue

            filePath = GenerateRandomString() + ".jpg"
            filePathAbs = os.path.join(upload_folder_abs, filePath)
            with open(filePathAbs, 'wb') as f:
                f.write(base64.b64decode(img))
                filePaths.append(filePath)
    else:
        filePathAbs = os.path.join(upload_folder_abs, file_name)
        with open(filePathAbs, 'wb') as f:
            f.write(base64.b64decode(imageData))
            filePaths.append(os.path.join(folder_name, file_name))

    if(len(filePaths) == 0):
        raise Exception("Không save được ảnh")

    return filePaths
    
####################################################################################################

def Compress(imgPath):
    img = Image.open(imgPath)
    img = img.convert('RGB')
    img.save(imgPath, quality=99)
    img.close()
    return True

####################################################################################################

def PreprocessImage(imgPath):
    isValid = RotateImageWithExif(imgPath)
    if(isValid):
        isValid &= ResizeImage(imgPath, 1000)
    if(isValid):
        isValid &= Compress(imgPath)
    return isValid

####################################################################################################

def ProcessMultiple(imgPaths):
    for imgPath in imgPaths:
        PreprocessImage(imgPath)
        #SaveThumbnail(imgPath)


####################################################################################################

def CropImage(imgPath):     
    img = Image.open(imgPath)
    if(img.mode == 'RGBA'):
        img = img.convert('RGB')
        img.save(imgPath)
        
    width, height = img.size
    if(width == height):
        img.close()
        return
    if(width > height):
        width = height
        padding = int((width - height)/2)
        img = img.crop((padding, 0, width, height))
    else:
        height = width    
        padding = int((height - width)/2)
        img = img.crop((0, padding, width, height))

    img.save(imgPath)
    img.close()