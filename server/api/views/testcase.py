from rest_framework.decorators import api_view
import json
import hashlib
import threading
from dateutil.parser import parse
from api.models import User, LoginSession
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.conf import settings
from api.apps import *
import api.auth
from mongoengine.queryset.visitor import Q
import base64, os, time
from lib.TGMT.TGMTfile import *

####################################################################################################
startime = None
numThread = 0

def FindLandmark(imagePath, index):
    startEncoding = time.time()
    image = face_recognition.load_image_file(imagePath)
    landmarks = face_recognition.face_encodings(image)
    elapsedEncoding = time.time() - startEncoding
    # if(len(landmarks) > 0):
    #     print("#" + str(index) + ": " + str(elapsedEncoding))
    # else:
    #     print("#" + str(index) + ": cannot find landmark " + str(elapsedEncoding))

    global numThread
    if(index == numThread):
        elapsed = time.time() - startime
        print("Total elapsed: " + str(elapsed))


def RunMultiple(numThread):
    imagePath = os.path.join(settings.MEDIA_ROOT, "2021-07-17_06-13-00_DpfWkBh3c1.jpg")

    i =0
    while(i< numThread):
        #print(">>>>>Start thread #" + str(i + 1))
        th = threading.Thread(target=FindLandmark, args=[imagePath, (i+1)] )
        th.start()
        i+=1
    print(">>>>>")

@api_view(["POST"])
def TestDlib(request):
    try:
        global startime
        startime = time.time()
        
        # img = Image.open(imagePath)
        # buffered = BytesIO()
        # img.save(buffered, format="JPEG")
        # imageBase64 = str(base64.b64encode(buffered.getvalue()))

        # randFileName = GenerateRandFileName(".jpg")
        # imagePaths = SaveBase64ToImg("temp", randFileName, imageBase64)
        # imagePath = os.path.join(settings.MEDIA_ROOT, imagePaths[0])

        global numThread
        numThread = int(GetParam(request, "numThread"))
        

        t = threading.Thread(target=RunMultiple, args=(numThread,))
        t.start()
        


        

        return SuccessResponse("Đã test xong")
    except Exception as e:
        return ErrorResponse(str(e))


def RemoveAppear(imagePath):  
    time.sleep(2)
    RemoveFileAsync(os.path.join(settings.MEDIA_ROOT, imagePath))

def RemoveAppearAsync(imagePath):
    t = threading.Thread(target=RemoveAppear, args=(imagePath, ))
    t.start()