from rest_framework.decorators import api_view
from rest_framework.response import Response
import json
import hashlib
import os
import cv2
import datetime, time
from dateutil.parser import parse
from api.models import Annotation, History, Level, User
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from api.apps import *
from django.db.models import Q
from api.views.annotation import AddAnnotation
from api.views.loginsession import *
from api.apps import *
from lib.TGMT.TGMTthread import ThreadWithReturnValue
from lib.TGMT.TGMTutil import *
from lib.TGMT.TGMTimage import *
from lib.TGMT.TGMTfile import *
from django.conf import settings
from module.CCCD.Extractor import idcard_extractor

####################################################################################################

@api_view(["POST"])           
def ExtractIDCard(request):
    try:
        dirName = "idcard"
        _randFilename = datetime.datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S") + "_" + GenerateRandomString() + ".jpg"
        uploaded_file_abs = os.path.join(settings.MEDIA_ROOT, dirName, _randFilename)
        hasNewImage = SaveImageFromRequest(request, dirName, _randFilename)

        if(not hasNewImage):
            return ErrorResponse("Ảnh không hợp lệ")

        startTime = time.time()

        frame = cv2.imread(uploaded_file_abs)

        #info = idcard_extractor.info

        annotations = idcard_extractor.Detection(frame)
        extracted_result=[]

        threads = []
        info ={}
        
        for i, box in enumerate(annotations):
            printt(box)
            if re.search(r'\d{9,12}', box[1][0]):
                info['ID_number'] = (re.split(r':|[.]|O|N|S|o|/|\s+', box[1][0]))[-1].strip()
                info['ID_number_box'] = box[0]
                continue

            top_left     = (int(box[0][0][0]), int(box[0][0][1]))
            top_right    = (int(box[0][1][0]), int(box[0][1][1]))
            bottom_right = (int(box[0][2][0]), int(box[0][2][1]))
            bottom_left  = (int(box[0][3][0]), int(box[0][3][1]))
    
            t = ThreadWithReturnValue(target=idcard_extractor.WarpAndRec, args=(frame, top_left, top_right, bottom_right, bottom_left))
            threads.append(t)
    
        for t in threads:
            t.start()   

        for t in threads:
            extracted_result.append(t.join())

        info = idcard_extractor.GetInformationAndSave(extracted_result, info['ID_number'], info['ID_number_box'])

        history = History()
        history.imagePath        = os.path.join(dirName, _randFilename)
        history.idNumber         = info['ID_number']
        history.fullName         = info['Name']
        history.dateOfBirth      = info['Date_of_birth']
        history.gender           = info['Gender']
        history.nationality      = info['Nationality']
        history.placeOfOrigin    = info['Place_of_origin']
        history.placeOfResidence = info['Place_of_residence']
        history.timeCreate       = utcnow()
        history.save()


        

        texts = [info['Name'], info['Date_of_birth'], info['Gender'], info['Nationality'], info['Place_of_origin'], info['Place_of_residence']]
        boxes = [info['Name_box'], info['Date_of_birth_box'], info['Gender_box'], info['Nationality_box'], info['Place_of_origin_box'], info['Place_of_residence_box']]
        with open(os.path.join(settings.MEDIA_ROOT, dirName, 'annotation.txt'), 'a', encoding='utf-8') as f:

            for i in range(len(texts)):            
                filePath = os.path.join(dirName, (re.split(r'[.]', _randFilename)[-2] + '_{0}.jpg'.format(i)))
                filePathAbs = os.path.join(settings.MEDIA_ROOT, filePath)
                if boxes[i]:
                    idcard_extractor.WarpAndSave(frame=frame, fileName=filePathAbs, top_left=boxes[i][0], top_right=boxes[i][1], bottom_right=boxes[i][2], bottom_left=boxes[i][3])
                    text = re.split(r'\\|/', filePathAbs)[-1] + '\t' + texts[i]
                    f.write(text +'\n')

                    AddAnnotation(filePath, texts[i])
                else:
                    continue
            f.close()

        elapsed = time.time() - startTime
        elapsed = round(elapsed, 2)
        info["elapsed"] = elapsed
        
        return Response(info)

    except Exception as e:
        return ErrorResponse("Có lỗi: " + str(e))
    
####################################################################################################

