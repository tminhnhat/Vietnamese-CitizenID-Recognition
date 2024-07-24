import math

from lib.TGMT.TGMTmat import Base64ToMat, IsMatEmpty, MatToBase64
from rest_framework.decorators import api_view
import json
import cv2
from dateutil.parser import parse
from api.models import Person
from django.conf import settings
from api.apps import *
import api.auth
from mongoengine.queryset.visitor import Q
import base64, os, time
from lib.TGMT.TGMTimage import PreprocessImage, SaveBase64ToImg
from lib.TGMT.TGMTfile import *
from lib.TGMT.TGMTpaging import Paging
from lib.TGMT.TGMTthread import *
from lib.modulemgr import faceCore
import numpy as np

from lib.modulemgr import angleDetector


####################################################################################################
@api_view(["POST"])           
def Compare(request):
    try:
        startTime = time.time()

        folder = datetime.datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S") + "_" + GenerateRandomString()
        folder = os.path.join("compare", folder)

        #save image 1
        _randFilename = GenerateRandomString() + ".jpg"
        uploaded_file_abs1 = os.path.join(settings.MEDIA_ROOT, folder, _randFilename)
        _base64_image1 = request.POST.get("imageBase64_1")
        SaveBase64ToImg(folder, _randFilename, _base64_image1)
        
        if(not PreprocessImage(uploaded_file_abs1)):
            return ErrorResponse("Ảnh khuôn mặt 1 không hợp lệ")



        #save image 2
        _randFilename = GenerateRandomString() + ".jpg"
        uploaded_file_abs2 = os.path.join(settings.MEDIA_ROOT, folder, _randFilename)
        _base64_image2 = request.POST.get("imageBase64_2")
        SaveBase64ToImg(folder, _randFilename, _base64_image2)

        
        if(not PreprocessImage(uploaded_file_abs2)):
            return ErrorResponse("Ảnh khuôn mặt 2 không hợp lệ")
        


        #get face landmark 2 in main thread
        landmarks1 = faceCore.GetFaceLandmarks(uploaded_file_abs1)
        if(len(landmarks1) == 0):
            raise Exception("Không tìm thấy khuôn mặt trong ảnh 1") 
        elif(len(landmarks1) > 1):
            raise Exception("Có nhiều khuôn mặt trong ảnh 1") 


        landmarks2 = faceCore.GetFaceLandmarks(uploaded_file_abs2)
        if(len(landmarks2) == 0):
            raise Exception("Không tìm thấy khuôn mặt trong ảnh 2") 
        elif(len(landmarks2) > 1):
            raise Exception("Có nhiều khuôn mặt trong ảnh 2") 

        landmark1 = landmarks1[0]
        landmark2 = landmarks2[0]

        distance = faceCore.CalcFaceDistance(landmark1, landmark2)
        
        elapsedTime = time.time() - startTime

        objResult = {}
        percent = (1.0 - float(distance)) * 100
        percent = math.ceil(percent)

        objResult["percent"] = percent
        objResult["isMatch"] = percent >= settings.THRESHOLD
        objResult["elapsedTime"] = elapsedTime


        return ObjResponse(objResult)
    except Exception as e:
        print(str(e))
        return ErrorResponse(str(e))
        
####################################################################################################

def shape_to_np(shape, dtype="int"):
    # initialize the list of (x, y)-coordinates
    coords = np.zeros((68, 2), dtype=dtype)
    # loop over the 68 facial landmarks and convert them
    # to a 2-tuple of (x, y)-coordinates
    for i in range(0, 68):
        coords[i] = (shape.part(i).x, shape.part(i).y)
    # return the list of (x, y)-coordinates
    return coords

####################################################################################################

def rect_to_bb(rect):
    # take a bounding predicted by dlib and convert it
    # to the format (x, y, w, h) as we would normally do
    # with OpenCV
    x = rect.left()
    y = rect.top()
    w = rect.right() - x
    h = rect.bottom() - y
    # return a tuple of (x, y, w, h)
    return (x, y, w, h)

####################################################################################################

pose_predictor_68_point = None
frontalDetector = None

def DrawLandmarkToMat(frame):
    global frontalDetector
    global pose_predictor_68_point
    if(frontalDetector == None):
        frontalDetector = dlib.get_frontal_face_detector()
        predictor_68_point_model = face_recognition_models.pose_predictor_model_location()    
        pose_predictor_68_point = dlib.shape_predictor(predictor_68_point_model)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # detect faces in the grayscale image
    rects = frontalDetector(gray, 1)
    if(len(rects) == 0):
        return frame

    for (i, rect) in enumerate(rects):
        # determine the facial landmarks for the face region, then
        # convert the facial landmark (x, y)-coordinates to a NumPy
        # array
        shape = pose_predictor_68_point(gray, rect)
        shape = shape_to_np(shape)
        # convert dlib's rectangle to a OpenCV-style bounding box
        # [i.e., (x, y, w, h)], then draw the face bounding box
        (x, y, w, h) = rect_to_bb(rect)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        # show the face number
        # cv2.putText(frame, "Face #{}".format(i + 1), (x - 10, y - 10),
        #     cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        # loop over the (x, y)-coordinates for the facial landmarks
        # and draw them on the image
        for (x, y) in shape:
            cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

    return frame

####################################################################################################

@api_view(["POST"])
def DrawLandmark(request):
    try:
        
        _base64_image = request.POST.get("imageBase64")
        frame = Base64ToMat(_base64_image)       
        frame = DrawLandmarkToMat(frame)

        objResult = {}

        img = MatToBase64(frame)
        objResult["img"] = img

        return ObjResponse(objResult)
    except Exception as e:
        return ErrorResponse(str(e))

####################################################################################################

@api_view(["POST"])
def FindDirNotExistInDB(request):
    try:
        _token = request.POST.get("token")
        jwt = api.auth.decode(_token)

        owners = User.objects(level="Admin", isDeleted=False)
        results = []

        for owner in owners:
            childDirs = GetChildDir(os.path.join(settings.MEDIA_ROOT, owner.email))
            personIDs = Person.objects(owner= owner.email, isDeleted=False).values_list("personID")

            
            for childDir in childDirs:
                if(childDir not in personIDs):
                    results.append(childDir + "    " + owner.email)
                

        order_by = GetParam(request, "order_by")
        if(order_by != None and order_by == "asc"):
            results.sort()
        else:
            results.sort(reverse=True)
        return ObjResponse(results)
    except Exception as e:
        print(str(e))
        return ErrorResponse(str(e))

####################################################################################################

@api_view(["POST"])
def FaceDirection(request):
    try:
        base64string = GetParam(request, "imageBase64")        
        frame = Base64ToMat(base64string)
        
        direction, ratio = angleDetector.Detect(frame)
        if(direction == "left"):           
            return SuccessResponse("Khuôn mặt xoay trái "+ "{0:.3g}".format(ratio))
        elif(direction == "right"):
            return SuccessResponse("Khuôn mặt xoay phải " + "{0:.3g}".format(ratio))
        elif(direction == "up"):
            return SuccessResponse("Khuôn mặt ngước lên " + "{0:.3g}".format(ratio))
        elif(direction == "down"):
            return SuccessResponse("Khuôn mặt cúi xuống " + "{0:.3g}".format(ratio))
        else:
            return SuccessResponse("Khuôn mặt nhìn thẳng " + "{0:.3g}".format(ratio))                
    except Exception as e:
        print(str(e))
        return ErrorResponse(str(e))

####################################################################################################

@api_view(["POST"])
def CheckBrightness(request):
    try:        
        _base64_image = request.POST.get("imageBase64")
        frame = Base64ToMat(_base64_image)   
        
        result, mean = CheckBright(frame)


        return SuccessResponse(result + " {0:.3g}".format(mean))
    except Exception as e:
        printt(str(e))
        return ErrorResponse(str(e))

####################################################################################################

@api_view(["POST"])
def CheckAbnormal(request):
    try:
        _token = GetParam(request, "token")
        loginSession = api.auth.decode(_token)

        personList = Person.objects(owner="lovetodie100@yahoo.com", isDeleted=False)
        personList = Paging(request, personList)

        arrPerson = personList["objects"]

        result = []

        for (i, person) in enumerate(arrPerson):
            dirPath = os.path.join(settings.MEDIA_ROOT, person["owner"], person["personID"])
            imagePaths = FindFileInDir(dirPath, "*.jpg", True, False)       
            
            
            for currentImgPath in imagePaths:
                printt(currentImgPath)
                err = ""
                imgPath = currentImgPath.replace(settings.MEDIA_ROOT, "")

                frame = cv2.imread(currentImgPath)
                direction, ratio = angleDetector.Detect(frame)
                if(direction == "left"):
                    err = "Khuôn mặt xoay trái"
                elif(direction == "right"):
                    err = "Khuôn mặt xoay phải"
                elif(direction == "up"):
                    err = "Khuôn mặt ngước lên"
                elif(direction == "down"):
                    err = "Khuôn mặt cúi xuống"

                if(err != ""):
                    result.append({"imgPath" : imgPath, "error": err, "personID" : person["personID"]})
                    continue

                #crop face
                matFace = None #face cropped
                expandRatio = 1.5 #GetParam(request, "expandRatio")
                if(expandRatio != None and expandRatio != ""):
                    expandRatio = float(expandRatio)
                    [frame_height, frame_width] = frame.shape[:2]
                    realWidth = int(frame_width / expandRatio)
                    realHeight = int(frame_height / expandRatio)
                    left = int((frame_width - realWidth) / 2)
                    top = int((frame_height - realHeight) / 2)         
                    width  = realWidth
                    height = realHeight


                    bottom = top + height
                    right  = left + width 
                    matFace = frame[top:bottom, left:right]

                #detect brightness
                if(not IsMatEmpty(matFace)):
                    bright, mean = CheckBright(matFace)
                    if(bright == "Dark"):
                        err = "Dark"
                    elif(bright == "Bright"):
                        err = "Right"


                if(err != ""):
                    result.append({"imgPath" : imgPath, "error": err, "personID" : person["personID"]})
                    continue

                #detect hidden
                if(not IsMatEmpty(matFace)):
                    ret = abnormalDetector.Predict(matFace)
                    if(ret == "hidden"):
                        err = "Khuôn mặt bị che"
                    elif(ret == "mask_full"):
                        err = "Đeo khẩu trang"

                
                if(err != ""):
                    result.append({"imgPath" : imgPath, "error": err, "personID" : person["personID"]})
                    continue

        personList["objects"] = result
        return ObjResponse(personList)
    except Exception as e:
        return ErrorResponse(str(e))
