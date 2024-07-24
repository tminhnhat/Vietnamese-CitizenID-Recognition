import math
from unidecode import unidecode
from api.views.activity import AddActivity
from api.views.log import WriteLog
from api.views.loginsession import *
from rest_framework.decorators import api_view
import json
from urllib.parse import urlparse
import time
from datetime import date, timedelta
from api.models import Person, PersonGroup, User, Appear
from mongoengine.queryset.visitor import Q
from dateutil.parser import parse
from api.apps import *
from django.conf import settings
from lib.modulemgr import faceCore
from lib.TGMT.TGMTfile import *
from lib.TGMT.TGMTimage import *
from lib.TGMT.TGMTpaging import Paging
from api.excel_utils import *

####################################################################################################

@api_view(["POST"])           
def AddPerson(request):
    saveDir = ""
    owner = None
    try:
        _token = GetParam(request, "token")
        jwt = api.auth.decode(_token)


        _fullName = RequireParamExist(request, "fullName", "họ tên")
        RequireParamExist(request, "imageBase64", "ảnh khuôn mặt")


        _birthday = GetParam(request, "birthday")

        _owner = GetParam(request, "owner")
        if(_owner == None or _owner == ""):
            _owner = jwt["owner"]
        
        owner = User.objects.get(email=_owner, isDeleted=False)
        
        person = Person(
            personID = GeneratePersonID(owner),
            dateCreate = utcnow()
        )

        person.dirName = GenerateDirname(person)
        person.fullName = _fullName
        person.fullName_ascii = unidecode(person.fullName)
        person.gender = GetParam(request, "gender")
        person.phone = GetParam(request, "phone")
        person.group_pk = GetParam(request, "group_pk")
        person.groupName = GetParam(request, "groupName")
        if(_birthday != None and _birthday != "" ):
            person.birthday = _birthday
        person.cmnd = GetParam(request, "cmnd")
        _issuedDate = GetParam(request, "issuedDate")
        if(_issuedDate != None and _issuedDate != ""):
            person.issuedDate = _issuedDate
        person.address = GetParam(request, "address")
        person.note = GetParam(request, "note")
        person.owner = _owner
        person.orgName = jwt["orgName"]

        

        saveDir = os.path.join(_owner, person.personID)
        MkDir(os.path.join(settings.MEDIA_ROOT, saveDir))
        MkDir(os.path.join(settings.MEDIA_ROOT, saveDir, "appear"))

        #save image        
        imgList = SaveImageFromRequest(request, saveDir)
        if(len(imgList) == 0):
            return ErrorResponse("Không save được ảnh")

        uploaded_file_abs = os.path.join(settings.MEDIA_ROOT, imgList[0])
        person.avatar = imgList[0]

        #find landmark
        landmarks = faceCore.GetFaceLandmarks(person.avatar, True)
        if(len(landmarks) == 0):
            RemoveFile(uploaded_file_abs)
            return ErrorResponse("Không có khuôn mặt trong ảnh")
        elif(len(landmarks) > 1):
            RemoveFile(uploaded_file_abs)
            return ErrorResponse("Có nhiều hơn 1 khuôn mặt trong ảnh")

        person.save()

        UpdateAvatar(person)

        owner.countPerson += 1
        owner.save()

        AddActivity(jwt["email"], "Thêm khách hàng", person.personID + " - " + person.fullName)

        return JsonResponse(person.to_json())
    except Exception as e:      
        RemoveDir(os.path.join(settings.MEDIA_ROOT, saveDir))
        if(owner != None):
            owner.currentPersonIdx -= 1
            owner.save()
        WriteLog("Thêm khách hàng thất bại", str(e))
        return ErrorResponse(str(e))

####################################################################################################

@api_view(["POST"])           
def GetPerson(request):    
    try:
        _token = GetParam(request, "token")
        jwt = api.auth.decode(_token)

        _personID = GetParam(request, 'personID')
        _person_pk = GetParam(request, 'person_pk')

        if(_personID != None and _personID != ""):
            person = Person.objects.get(personID=_personID, isDeleted=False)
        elif(_person_pk != None and _person_pk != "" and len(_person_pk) == 24):
            person = Person.objects.get(pk=_person_pk, isDeleted=False)
        else:
            return ErrorResponse("Thiếu tham số")

        return JsonResponse(person.to_json())
    except Exception as e:
        return ErrorResponse(str(e))
        
####################################################################################################

@api_view(["POST"])           
def GetPersonList(request):
    try:
        _token = GetParam(request, "token")
        jwt = api.auth.decode(_token)

        personList = QueryPerson(request, jwt)
        respond = Paging(request, personList)        
        
        return ObjResponse(respond)
    except Exception as e:
        return ErrorResponse(str(e))

####################################################################################################

#cannot detect face
@api_view(["POST"])           
def Checkin(request):
    try:
        startTime = time.time()

        _token = GetParam(request, "token")
        jwt = api.auth.decode(_token)

        #RequireParamExist(request, "imageBase64", "ảnh khuôn mặt")

        _owner = GetParam(request, 'owner') 
        if(_owner == None or _owner == ""):
            _owner = jwt["owner"]
        else:
            RequireLevel(jwt, ["Root"])

        _cardID = GetParam(request, 'cardID')
        _personID = GetParam(request, 'personID')
        _person_pk = GetParam(request, 'person_pk')

        try:
            if(_personID != None and _personID != ""):            
                person = Person.objects.get(personID=_personID, owner=_owner, isDeleted=False)
            elif(_person_pk != None and _person_pk != "" and len(_person_pk) == 24):
                person = Person.objects.get(pk=_person_pk, isDeleted=False)
            elif(_cardID != None and _cardID != "" ):
                person = Person.objects.get(cardID=_cardID, isDeleted=False)
            else:
                return ErrorResponse("Thiếu tham số")
        except Person.MultipleObjectsReturned:
            return ErrorResponse("Bị trùng thẻ")
        except Person.DoesNotExist:
            return ErrorResponse("Không tìm thấy nhân viên")
        


        #save image
        saveDir = os.path.join(_owner, person.personID, "appear")        
        imgList = SaveImageFromRequest(request, saveDir)
        imagePath = ""
        if(len(imgList) > 0):
            imagePath = imgList[0]

        

        elapsedTime = time.time() - startTime

        #create appear info
        appear = Appear(           
                timeAppear = utcnow(),
                imagePath = imagePath,
                distance = 1.0,
                percent = 0,
                owner = _owner,
                gate = jwt["email"],
                personExist = True,
                personType = person.personType,
                fullName = person.fullName,
                fullName_ascii = unidecode(person.fullName),
                person_pk = str(person.pk),
                person_id = str(person.personID),
                elapsed = elapsedTime
            )
        
        shouldAlert = False
        if(person.group_pk != None and person.group_pk != ""):                
            try:
                group = PersonGroup.objects.get(pk=person.group_pk, isDeleted=False)
                appear.groupName = group.name
                if(group.alert): shouldAlert = True
            except PersonGroup.MultipleObjectsReturned:
                pass
            except PersonGroup.DoesNotExist:
                pass


        appear.save()

        percent = 0
        objResult = json.loads(appear.to_json())
        objResult["shouldAlert"] = shouldAlert
        objResult["distance"] = 1.0
        objResult["percent"] = percent
        objResult["isMatch"] = True
        objResult["elapsedTime"] = elapsedTime

        return ObjResponse(objResult)
    except Exception as e:
        return ErrorResponse(str(e))

####################################################################################################

def QueryPerson(request, jwt):
    _search_string = GetParam(request, "search_string")
    _order_by = GetParam(request, 'order_by')    
    _owner = GetParam(request, 'owner')
    _group_pk = GetParam(request, 'group_pk')
    _personType = GetParam(request, 'personType')
    _building_pk = GetParam(request, 'building_pk')
    _showKnownPersonOnly = GetParam(request, 'showKnownPersonOnly')

    if(_owner == None or _owner == ""):
        _owner=jwt["owner"]
    else:
        if(_owner != jwt["owner"] and jwt["level"] != "Root"):
            raise Exception("Bạn không có quyền truy cập")

    if(_owner == "all"):
        if(jwt["level"] == "Root"):
            personList = Person.objects(isDeleted=False)
        else:
            personList = Person.objects(owner=_owner, isDeleted=False)
    else:
        personList = Person.objects(owner=_owner, isDeleted=False)

    if(_showKnownPersonOnly != None and _showKnownPersonOnly == "True"):
        personList = personList(fullName__ne="Khách mới")
        
    if(_group_pk != None and _group_pk != "" and _group_pk != "all"):
        personList = personList(group_pk=_group_pk)

    if(_building_pk != None and _building_pk != "" and _building_pk != "all"):
        personList = personList(building_pk=_building_pk)

    if(_personType != None and _personType != ""):
        personList = personList(personType=_personType)

    if(_search_string != None and _search_string != ""):
        if(len(_search_string) == 24):
            personList = personList(pk=_search_string)
        else:
            _search_string_ascii = unidecode(_search_string)
            personList = personList.filter(Q(fullName__icontains=_search_string) |
                                            Q(fullName_ascii__icontains=_search_string_ascii) | 
                                            Q(phone__icontains=_search_string) | 
                                            Q(cmnd__icontains=_search_string) | 
                                            Q(personID__icontains=_search_string))

    if(_order_by != None and _order_by == "desc"):
        personList = personList.order_by("-dateCreate")

    return personList

####################################################################################################

@api_view(["POST"])           
def UpdatePerson(request):
    try:
        _token = GetParam(request, "token")
        jwt = api.auth.decode(_token)
        
        _person_pk = GetParam(request, "person_pk")
               

        try:
            person = Person.objects.get(pk=_person_pk, isDeleted=False)
            isExist = True
        except Person.MultipleObjectsReturned:
            return ErrorResponse("Bị trùng ID")
        except Person.DoesNotExist:
            return ErrorResponse("Không tìm thấy người")
       
        
        _newPersonID = GetParam(request, "newPersonID")
        if(_newPersonID != None and _newPersonID != "" and _newPersonID != person.personID):
            #find exist person
            try:
                existPerson = Person.objects.get(personID=_newPersonID, owner=person.owner, isDeleted=False)
                return ErrorResponse("Mã này đã được sử dụng")
            except Person.MultipleObjectsReturned:
                return ErrorResponse("Mã này đã được sử dụng")
            except Person.DoesNotExist:
                pass
            

            #rename folder
            oldDir = os.path.join(settings.MEDIA_ROOT, person.owner, person.personID)
            newDir = os.path.join(settings.MEDIA_ROOT, person.owner, _newPersonID)
            if(os.path.exists(newDir)):
                return ErrorResponse("Đã có folder: " + _newPersonID)
            os.rename(oldDir, newDir)

            appears = Appear.objects(person_pk=_person_pk, isDeleted=False)
            for a in appears:
                a.person_id = _newPersonID
                a.imagePath = a.imagePath.replace(person.personID, _newPersonID)
                a.save()

            person.personID = _newPersonID
            person.dirname = _newPersonID


        _fullName = GetParam(request, "fullName")
        if(_fullName != None and _fullName !=""):
            person.fullName = _fullName
            person.fullName_ascii = unidecode(_fullName)

        _gender = GetParam(request, "gender")
        if(_gender != None and _gender !=""):
            person.gender = _gender

        _phone = GetParam(request, "phone")
        if(_phone != None and _phone !=""):
            person.phone = _phone

        _personType = GetParam(request, "personType")
        if(_personType != None and _personType !=""):
            person.personType = _personType

        _startShift = GetParam(request, "startShift")
        _endShift = GetParam(request, "endShift")
        if(_startShift != None and _startShift !="" and _endShift != None and _endShift !=""):
            person.startShift = _startShift
            person.endShift = _endShift

        _group_pk = GetParam(request, "group_pk")
        if(_group_pk != None and _group_pk !=""):
            person.group_pk = _group_pk
            person.groupName = GetParam(request, "groupName")
        else:
            person.group_pk = ""
            person.groupName = ""

        _building_pk = GetParam(request, "building_pk")
        _buildingName = GetParam(request, "buildingName")
        if(_building_pk != None and _building_pk !="" and _buildingName != None and _buildingName !=""):
            person.building_pk = _building_pk
            person.buildingName = _buildingName
        else:
            person.building_pk = ""
            person.buildingName = ""


        _birthday = GetParam(request, "birthday")
        if(_birthday != None and _birthday != "" ):
            person.birthday = _birthday

        _cmnd = GetParam(request, "cmnd")
        if(_cmnd != None):
            person.cmnd = GetParam(request, "cmnd")

        _issuedDate = GetParam(request, "issuedDate")
        if(_issuedDate != None and _issuedDate !=""):
            person.issuedDate = _issuedDate

        _address = GetParam(request, "address")
        if(_address != None):
            person.address = _address
        
        
        _note = GetParam(request, "note")
        if(_note != None):
            person.note = _note

        

        _cardID = GetParam(request, "cardID")
        if(_cardID != None and _cardID !=""):
            try:
                p = Person.objects.get(cardID=_cardID, pk__ne=str(person.pk),  isDeleted=False)
                return ErrorResponse("Nhân viên " + p.fullName + " (" + p.personID + ") đã dùng thẻ này")
            except Person.MultipleObjectsReturned:
                return ErrorResponse("Bị trùng thẻ")
            except Person.DoesNotExist:
                pass
            
        person.cardID = _cardID

        avatarAbs = ""
        if(person.avatar != None and person.avatar != ""):
            avatarAbs = os.path.join(settings.MEDIA_ROOT, person.avatar)

        if(avatarAbs == "" or not os.path.exists(avatarAbs) or "appear" in avatarAbs):
            UpdateAvatar(person)

        
        #update all appears of person
        appears = Appear.objects(person_pk=str(person.pk), isDeleted=False)
        for a in appears:
            a.person_id = str(a.person_id)
            a.fullName = _fullName
            a.fullName_ascii = unidecode(_fullName)
            a.save()

        person.timeUpdate = utcnow()
        person.userUpdate = jwt["email"]
        person.totalAppear = len(appears)
        person.save()

        #add one more image into this person
        #save file to temp folder
        _randFilename = GenerateRandFileName(".jpg")
        filePath = os.path.join(person.owner, person.personID, _randFilename)
        uploaded_file_abs = os.path.join(settings.MEDIA_ROOT, filePath)
        imgList = SaveImageFromRequest(request, os.path.join(person.owner, person.personID), _randFilename)
        if(len(imgList) > 0):
            #resize image if wider than 1000
            if(not PreprocessImage(uploaded_file_abs)):
                return ErrorResponse("Ảnh khuôn mặt không hợp lệ")
            
            #save landmark
            landmarks = faceCore.GetFaceLandmarks(filePath, True)
            if(len(landmarks) == 0):
                RemoveFile(uploaded_file_abs)
                return ErrorResponse("Không có khuôn mặt trong ảnh")
            elif(len(landmarks) > 1):
                RemoveFile(uploaded_file_abs)
                return ErrorResponse("Có nhiều hơn 1 khuôn mặt trong ảnh")

            UpdateAvatar(person)


        AddActivity(jwt["email"], "Cập nhật khách hàng", person.personID + " - " + person.fullName)

        return SuccessResponse("Cập nhật thành công")            
    except Exception as e:
        WriteLog("Cập nhật khách hàng thất bại", str(e))
        return ErrorResponse(str(e))

####################################################################################################

def MergePersonInternal(jwt, oldPerson_pk, newPerson_pk):   
    if(oldPerson_pk == newPerson_pk):
        return 0

    person = None
    personToMerge = None

    try:
        person = Person.objects.get(pk=oldPerson_pk, isDeleted=False)
        personToMerge = Person.objects.get(pk=newPerson_pk, isDeleted=False)
    except Person.DoesNotExist:
        return 0

    _owner = personToMerge.owner
    #create dir in case person has no dir
    MkDir(os.path.join(settings.MEDIA_ROOT, _owner, personToMerge.personID))
    MkDir(os.path.join(settings.MEDIA_ROOT, _owner, personToMerge.personID, "appear"))


    #move all files from old person to new person
    personDirAbs = os.path.join(settings.MEDIA_ROOT, _owner, person.personID)
    for fullpathDir, subdirs, files in os.walk(personDirAbs):
        for name in files:
            currentFilePath = os.path.join(fullpathDir, name)
            newFilePath = currentFilePath.replace(person.personID, personToMerge.personID)
            os.replace(currentFilePath, newFilePath)



    #delete old person in database
    person.isDeleted = True
    person.save()

    #update all appears of old person to new person
    appears = Appear.objects(person_pk=oldPerson_pk, isDeleted=False)
    for a in appears:
        a.fullName = personToMerge.fullName
        a.fullName_ascii = personToMerge.fullName_ascii
        a.person_id = str(personToMerge.personID)
        a.person_pk = newPerson_pk
        a.imagePath = a.imagePath.replace(person.personID, personToMerge.personID)
        a.save()


    personToMerge.avatar = person.avatar
    personToMerge.totalAppear += person.totalAppear
    personToMerge.save()
    UpdateAvatar(personToMerge)


    RemoveDirIfEmpty(os.path.join(settings.MEDIA_ROOT, _owner, person.personID, "appear"))
    RemoveDirIfEmpty(os.path.join(settings.MEDIA_ROOT, _owner, person.personID))


    AddActivity(jwt["email"], "Gộp khách hàng", person.personID + " - " + person.fullName + 
    " => " + personToMerge.personID + " - " + personToMerge.fullName )

    return len(appears)

####################################################################################################

@api_view(["POST"])           
def MergePerson(request):
    try:
        _token = GetParam(request, "token")
        jwt = api.auth.decode(_token)

        
        _person_pk = RequireParamExist(request, "person_pk", "khách hàng cũ")
        _mergeInto = RequireParamExist(request, "mergeInto", "khách hàng mới") #new person pk
        numAppearsMerged = MergePersonInternal(jwt, _person_pk, _mergeInto)

        return SuccessResponse("Gộp thành công {} lượt vào".format(numAppearsMerged))        
    except Exception as e:
        return ErrorResponse(str(e))


####################################################################################################

@api_view(["POST"])           
def GetImageList(request):
    try:
        _token = GetParam(request, "token")
        jwt = api.auth.decode(_token)

        dirName = GetParam(request, "dirName")

        person = None
        if(dirName == None or dirName == ""):
            person_pk = GetParam(request, "person_pk")
            if(person_pk == None or person_pk == ""):
                return ErrorResponse("Thiếu dữ liệu")

            person = Person.objects.get(pk=person_pk, isDeleted=False) 
            dirName = person.personID

        imgDir = os.path.join(settings.MEDIA_ROOT, person.owner, dirName)
        
        imgPaths = []
        for fullpathDir, subdirs, files in os.walk( imgDir):
            if("appear" in fullpathDir):
                    continue

            for fileName in files:
                name, ext = os.path.splitext(fileName)
                if(ext.lower() == ".jpg" or ext.lower() == ".png"):
                    imgPaths.append(os.path.join(person.owner, dirName, fileName))

        
        return ObjResponse(imgPaths)
    except Exception as e:
        return ErrorResponse(str(e))

####################################################################################################

@api_view(["POST"])           
def GetSimilarPerson(request):
    try:
        _token = GetParam(request, "token")
        jwt = api.auth.decode(_token)

        _owner = ""
        if(jwt["level"] == "Root"):
            _owner = GetParam(request, "owner")
        if(_owner == None or _owner == ""):
            _owner = jwt["owner"]      
        

        folder = "find"
        imgList = SaveImageFromRequest(request, folder)
        imgPath = ""
        if(len(imgList) == 0):
            imgPath = GetParam(request, "imgPath")
            if(imgPath == None or imgPath == ""):
                return ErrorResponse("Không save được ảnh")
            

            domain = urlparse(imgPath).netloc
            index = imgPath.index(domain)
            imgPath = imgPath[index + len(domain):]
            imgPath = imgPath.replace("/media/", "")
            imgPath = imgPath.replace("/", settings.SLASH)
            imgList = [imgPath]
            _owner = imgPath.split(settings.SLASH)[0]

        if(_owner == "root" or _owner == "all"):
            return ErrorResponse("Owner không hợp lệ")
        
        imgPathAbs = os.path.join(settings.MEDIA_ROOT, imgList[0])
        if(not os.path.exists(imgPathAbs)):
            return ErrorResponse("Không tìm thấy ảnh")

        landmarks = faceCore.GetFaceLandmarks(imgPathAbs, True)
        if(len(landmarks) == 0):
            return ErrorResponse("Không tìm thấy khuôn mặt trong ảnh")
        baseLandmark = landmarks[0]
        
        parentDir = os.path.join(settings.MEDIA_ROOT, _owner)
        results = faceCore.FindTopSimilarPersons(parentDir, baseLandmark)
        # matchDirName = GetParentDirName(imgMinDistancePath)

        faceCore.GetPersonMostSimilarInArray(results)
        persons = []

        _personID = ""
        for obj in results:
            try:
                splited = obj["imgPath"].split(settings.SLASH)
                _personID = splited[1]


                person = Person.objects.get(personID=_personID, owner=_owner, isDeleted=False)
                personObj = json.loads(person.to_json())
                percent = (1.0 - float(obj["distance"])) * 100
                percent = math.ceil(percent)
                personObj["percent"] = percent
                personObj["avatar"] = obj["imgPath"]
                persons.append(personObj)
            except Person.MultipleObjectsReturned:
                return ErrorResponse("Có 2 khách hàng cùng mã số: " + _personID)
            except Person.DoesNotExist:
                return ErrorResponse("Không tìm thấy database của: " + _personID)

            
        AddActivity(jwt["email"], "Tìm khách hàng bằng ảnh", "")
        return ObjResponse(persons)
    except Exception as e:
        WriteLog("Tìm khách bằng ảnh thất bại", str(e))
        return ErrorResponse(str(e))

####################################################################################################

@api_view(["POST"])           
def DeletePerson(request):
    try:
        _token = GetParam(request, "token")
        jwt = api.auth.decode(_token)

        RequireLevel(jwt, ["Root", "Admin"])        

        _person_pk = RequireParamExist(request, "person_pk", "mã person")

        try:
            person = Person.objects.get(pk=_person_pk, isDeleted=False)
        except Person.MultipleObjectsReturned:
            return ErrorResponse("Trùng person pk")
        except Person.DoesNotExist:
            return ErrorResponse("Person không tồn tại")

        if(person.owner != jwt["email"] and jwt["level"] != "Root"):
            return ErrorResponse("Bạn không phải là chủ sở hữu nên không có quyền xóa")


        
        dirPathAbs = os.path.join(settings.MEDIA_ROOT, person.owner, person.dirName)
        RemoveDir(dirPathAbs)


        appears = Appear.objects(person_pk=str(person.pk), isDeleted=False)
        for a in appears:
            a.isDeleted = True
            a.save()

        try:
            owner = User.objects.get(email=person.owner, isDeleted=False)
            owner.countPerson -= 1
            owner.save()
        except Exception as e:
            pass
        
        person.isDeleted=True
        person.save()
     
        AddActivity(jwt["email"], "Xóa khách hàng", person.personID + " - " + person.fullName)

        return SuccessResponse("Xóa khách hàng thành công")            
    except Exception as e:
        WriteLog("Xóa khách hàng thất bại", str(e))
        return ErrorResponse(str(e))

####################################################################################################

@api_view(["POST"])           
def GetMaxPerson(request):
    try:
        _token = GetParam(request, "token")
        jwt = api.auth.decode(_token)
        
        numPerson = 0
        if(jwt["level"] == "Gate"):
            owner = User.objects.get(email=jwt["owner"], isDeleted=False)
            numPerson = owner.numPerson
        else:
            user = User.objects.get(email=jwt['email'], isDeleted=False)
            numPerson = user.numPerson

        result = {
            'numPerson' : numPerson
        }
        return JsonResponse(json.dumps(result))
    except Exception as e:
        return ErrorResponse(str(e))

####################################################################################################

def GeneratePersonID(owner):
    owner.currentPersonIdx += 1
    owner.countPerson += 1
    owner.save()

    personID = "P" + "{:05d}".format(owner.currentPersonIdx)
    
    return personID
                
####################################################################################################

def GenerateDirname(person):
    return person.personID

####################################################################################################

@api_view(["POST"])
def ReportExcelPerson(request):
    try:
        _token = GetParam(request, "token")
        jwt = api.auth.decode(_token)
                                
        personList = QueryPerson(request, jwt)

        if(len(personList) == 0):
            return ErrorResponse("Không tìm thấy khuôn mặt")

        #excel part
        wb = Workbook()
        ws = wb.active
        fontTitle = Font(b=True, size=20)
        
        ws["A1"] ="DANH SÁCH KHUÔN MẶT"  
        
        border = Border()
        al = Alignment(horizontal="center", vertical="center")        

        ws["B3"] = "Số lượng nhân viên"
        ws["B4"] = "Số lượng khách hàng"

        ws["C3"] = personList(personType="Staff").count()
        ws["C4"] = personList(personType="Guest").count()

        style = NamedStyle(name="highlight")
        style_range(ws, "D3:D6", style)        

        column_list = ["STT", "MÃ SỐ", "HỌ TÊN", "NĂM SINH", "SỐ ĐIỆN THOẠI", "PHÂN LOẠI", "SỐ LẦN", "LẦN ĐẦU", "LẦN CUỐI"]
        maxColumn = chr(ord('A') + len(column_list) - 1)
        style_range_merge(ws, "A1:" + maxColumn + "1", border=border, fill=None, font=fontTitle, alignment=al)
        
        ws.append(column_list)
        index = 1

        
        for person in personList:
            row = []
            row.append(index)
            row.append("P" + str(person.personID))
            row.append(person.fullName) 
            row.append("" if person.birthday == None else person.birthday.strftime("%d/%m/%Y"))
            row.append(person.phone)
            row.append("Nhân viên" if person.personType in ["Nhân viên", "Staff"] else "Khách hàng")
            row.append(person.totalAppear)
            if(person.firstTimeAppear != None):
                row.append((person.firstTimeAppear + timedelta(hours=7)).strftime("%d/%m/%Y %H:%M:%S"))
            else:
                row.append("")
            if(person.lastTimeAppear != None):
                row.append((person.lastTimeAppear + timedelta(hours=7)).strftime("%d/%m/%Y %H:%M:%S"))
            else:
                row.append("")

            
            ws.append(row)

            index = index + 1

        for col in ws.columns:
            max_length = 0
            for cell in col:
                if cell.coordinate in ws.merged_cells: # not check merge_cells
                    continue
                try: # Necessary to avoid error on empty cells
                    lengthOfCell = GetMaxLengthOfCell(str(cell.value))
                    if lengthOfCell > max_length:
                        max_length = lengthOfCell
                except:
                    pass
            
            if(max_length > 60): max_length = 60
            ws.column_dimensions[col[0].column].width = max_length + 6


        table1_max_row = 7 + len(personList)
        create_table(ws, "Table1", "A7:" + maxColumn +"{}".format(table1_max_row))

        
        respond = createHttpRespond(wb)

        AddActivity(jwt["email"], "Xuất report khách hàng")
        return respond
    except Exception as e:
        WriteLog('Xuất report khách hàng thất bại', str(e))
        return ErrorResponse(str(e))

####################################################################################################

@api_view(["POST"])           
def DeleteImage(request):
    try:
        _token = request.POST.get("token")
        jwt = FindLoginSession(_token)
        if(jwt["level"] not in ["Root","Admin"]):
            return ErrorResponse("Bạn không có quyền xóa")

        person_pk = request.POST.get("person_pk")
        if(person_pk != None and len(person_pk)==24):
            person = Person.objects.get(pk=person_pk, isDeleted=False)
        else:
            personID = GetParam(request, "personID")
            person = Person.objects.get(personID=personID, owner="anhvietlienket@gmail.com", isDeleted=False)


        _imagePath = request.POST.get("imagePath")
        if("media" in _imagePath):
            mediaIdx = _imagePath.index("media")
            _imagePath = _imagePath[mediaIdx+6:]

        _imagePathAbs = os.path.join(settings.MEDIA_ROOT, _imagePath)
        if(not os.path.exists(_imagePathAbs)):
            return ErrorResponse("Ảnh không tồn tại")


        filename, ext = os.path.splitext(_imagePathAbs)
        ext = ext.replace(".", "")


        RemoveFile(_imagePathAbs)        
        landmarkFile = filename + ".bin"
        if(os.path.exists(landmarkFile)):
            os.remove(landmarkFile)

        UpdateAvatar(person)

        AddActivity(jwt["email"], "Xóa ảnh mẫu khách hàng", person.personID + " - " + person.fullName)
        return SuccessResponse("Xóa ảnh thành công")
    except Exception as e:
        WriteLog('Xóa ảnh mẫu khách hàng thất bại', str(e))
        return ErrorResponse(str(e))

####################################################################################################

def UpdateAvatar(person):
    dirPath = os.path.join(settings.MEDIA_ROOT, person.owner, person.personID)
    imgList = FindFileInDir(dirPath, "*.jpg", False, False)            
    if(len(imgList) > 0):
        person.avatar = imgList[len(imgList) - 1]
        person.save()

####################################################################################################

def CountNumTemplateImage(person):
    personDirAbs = os.path.join(settings.MEDIA_ROOT, person.owner, person.personID)
    filePaths = FindFileInDir(personDirAbs, "*.jpg")
    return len(filePaths)

####################################################################################################

def AddTemplateImage(person, imagePath):
    numTemplateImage = CountNumTemplateImage(person)
    numSecondFromAddTemplate = 0
    if(person.timeAddTemplate == None):
        numSecondFromAddTemplate = 4000
    else:
        numSecondFromAddTemplate = (utcnow() - person.timeAddTemplate).seconds
    if(numTemplateImage<20 or (numSecondFromAddTemplate > 3600)):
        imagePathAbs = imagePath
        if(settings.MEDIA_ROOT not in imagePath):
            imagePathAbs = os.path.join(settings.MEDIA_ROOT, imagePath)
        templateImgAbs = imagePathAbs.replace("appear/", "").replace("appear\\", "")
        
        if(imagePathAbs != templateImgAbs):
            shutil.copy2(imagePathAbs, templateImgAbs)
        landmarks = faceCore.GetFaceLandmarksAsync(templateImgAbs, True)
        person.timeAddTemplate = utcnow()
        person.save()