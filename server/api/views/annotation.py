from rest_framework.decorators import api_view
import json
import math
import datetime
from datetime import timedelta, datetime
from unidecode import unidecode
from api.models import Person, PersonGroup, User, History, ChartValue, Annotation
from mongoengine.queryset.visitor import Q
from dateutil.parser import parse
from api.apps import *
from api.views.activity import AddActivity
from api.views.attendance import CalcAttendance
from api.views.common import QueryAnnotations
from api.views.log import WriteLog
from api.views.user import GenerateLoginSession
from lib.TGMT.TGMTimage import *
from lib.TGMT.TGMTfile import *
from lib.TGMT.TGMTpaging import Paging
import time
import cv2
from api.views.loginsession import *
from lib.modulemgr import faceCore
from lib.modulemgr import angleDetector
from django.conf import settings
from api.views.person import CountNumTemplateImage, GeneratePersonID, GenerateDirname, MergePersonInternal, UpdateAvatar
from api.excel_utils import *

def AddAnnotation(_imagePath, _text):
    annotation = Annotation()
    annotation.imagePath = _imagePath
    annotation.text = _text
    annotation.timeCreate = utcnow()
    annotation.save()

####################################################################################################

@api_view(["POST"])           
def UpdateAnnotation(request):
    oldPerson = None
    newPerson = None
    try:
        _token = GetParam(request, "token")
        jwt = api.auth.decode(_token)


        _annotation_pk = GetParam(request, "annotation_pk")
        _newPerson_pk = GetParam(request, "newPerson_pk")


        annotation = Annotation.objects.get(pk=_annotation_pk, isDeleted=False)
        if(annotation.person_pk == _newPerson_pk):
            return ErrorResponse("Cùng 1 người")

        try:
            oldPerson = Person.objects.get(pk=annotation.person_pk, isDeleted=False)
            newPerson = Person.objects.get(pk=_newPerson_pk, isDeleted=False)
        except Person.MultipleObjectsReturned:
            return ErrorResponse("Trùng pk")
        except Person.DoesNotExist:
            return ErrorResponse("Không tìm thấy người")


        MkDir(os.path.join(settings.MEDIA_ROOT, newPerson.owner, newPerson.personID))          
        MkDir(os.path.join(settings.MEDIA_ROOT, newPerson.owner, newPerson.personID, "annotation"))
        
        #move all file to new dir
        oldImgPath = annotation.imagePath
        oldImgPathAbs = os.path.join(settings.MEDIA_ROOT, oldImgPath)
        newImgPath = oldImgPath.replace(oldPerson.personID, newPerson.personID)
        newImgPathAbs = os.path.join(settings.MEDIA_ROOT, newImgPath)
    
        if(os.path.exists(oldImgPathAbs)):
            if(os.path.exists(newImgPathAbs)):
                os.remove(oldImgPathAbs)
            else:
                os.rename(oldImgPathAbs, newImgPathAbs)
           

        #copy image to make template image
        templateImagePath = newImgPath.replace("/annotation", "").replace("\\annotation", "")
        templateImagePathAbs = os.path.join(settings.MEDIA_ROOT, templateImagePath)
        if(not os.path.exists(templateImagePathAbs)):
            shutil.copy2(newImgPathAbs, templateImagePathAbs)
            landmarks = faceCore.GetFaceLandmarks(templateImagePathAbs)

            UpdateAvatar(newPerson)


        annotation.person_pk = _newPerson_pk
        annotation.person_id = newPerson.personID
        annotation.imagePath = newImgPath
        annotation.fullName = newPerson.fullName
        annotation.fullName_ascii = newPerson.fullName_ascii
        annotation.group_pk = newPerson.group_pk
        annotation.groupName = newPerson.groupName
        annotation.userUpdate = jwt["email"]
        annotation.save()

        
        oldPerson.totalAnnotation -= 1
        oldPerson.save()

        newPerson.totalAnnotation += 1
        newPerson.save()

        AddActivity(jwt["email"], "Cập nhật lượt vào", oldPerson.personID + " => " + newPerson.personID)
        
        return SuccessResponse("Cập nhật thành công")
            
    except Exception as e:
        err = ""
        if(oldPerson != None): err = oldPerson.personID + " => "
        if(newPerson != None): err += newPerson.personID
        WriteLog("Cập nhật lượt vào thất bại", err + "\n" + str(e))
        return ErrorResponse(str(e))

####################################################################################################

@api_view(["POST"])           
def UpdateAnnotations(request):
    oldPerson = None
    newPerson = None
    try:
        _token = GetParam(request, "token")
        jwt = api.auth.decode(_token)


        _annotation_pks = RequireParamExist(request, "annotation_pks", "mã lượt vào")
        _annotation_pks = json.loads(_annotation_pks)
        _newPerson_pk = GetParam(request, "newPerson_pk")

        newPerson = Person.objects.get(pk=_newPerson_pk, isDeleted=False)
        MkDir(os.path.join(settings.MEDIA_ROOT, newPerson.owner, newPerson.personID))          
        MkDir(os.path.join(settings.MEDIA_ROOT, newPerson.owner, newPerson.personID, "annotation"))

        personsMerged = []

        for _annotation_pk in _annotation_pks:
            annotation = Annotation.objects.get(pk=_annotation_pk, isDeleted=False)
            if(annotation.person_pk == _newPerson_pk):
                continue #"Cùng 1 người"

            try:
                oldPerson = Person.objects.get(pk=annotation.person_pk, isDeleted=False)                
            except Person.MultipleObjectsReturned:
                return ErrorResponse("Trùng pk")
            except Person.DoesNotExist:
                return ErrorResponse("Không tìm thấy người")


            
            
            #move annotation image to new dir
            oldImgPath = annotation.imagePath
            oldImgPathAbs = os.path.join(settings.MEDIA_ROOT, oldImgPath)
            newImgPath = oldImgPath.replace(oldPerson.personID, newPerson.personID)
            newImgPathAbs = os.path.join(settings.MEDIA_ROOT, newImgPath)
        
            if(os.path.exists(oldImgPathAbs)):
                if(os.path.exists(newImgPathAbs)):
                    os.remove(oldImgPathAbs)
                else:
                    os.rename(oldImgPathAbs, newImgPathAbs)
            

            #copy image to make template image
            templateImagePath = newImgPath.replace("/annotation", "").replace("\\annotation", "")
            templateImagePathAbs = os.path.join(settings.MEDIA_ROOT, templateImagePath)
            if(not os.path.exists(templateImagePathAbs)):
                shutil.copy2(newImgPathAbs, templateImagePathAbs)
                landmarks = faceCore.GetFaceLandmarks(templateImagePathAbs)

                
            if(annotation.person_pk not in personsMerged):
                personsMerged.append(annotation.person_pk)

            annotation.person_pk = _newPerson_pk
            annotation.person_id = newPerson.personID
            annotation.imagePath = newImgPath
            annotation.fullName = newPerson.fullName
            annotation.fullName_ascii = newPerson.fullName_ascii
            annotation.group_pk = newPerson.group_pk
            annotation.groupName = newPerson.groupName
            annotation.userUpdate = jwt["email"]
            annotation.save()


            
            oldPerson.totalAnnotation -= 1
            oldPerson.save()

            newPerson.totalAnnotation += 1


        #save new person only one
        UpdateAvatar(newPerson)



        #shoud merge old person to new person if moved all annotations        
        for _oldPerson_pk in personsMerged:
            if(_oldPerson_pk != _newPerson_pk):
                annotations = Annotation.objects(person_pk=_oldPerson_pk, isDeleted=False)
                if(len(annotations) == 0):
                    MergePersonInternal(jwt, _oldPerson_pk, _newPerson_pk)

            

        msg = ""
        if(oldPerson != None): msg += oldPerson.personID + " => "
        if(newPerson != None): msg += newPerson.personID

        AddActivity(jwt["email"], "Cập nhật nhiều lượt vào", msg)        
        return SuccessResponse("Cập nhật thành công")
    except Exception as e:
        err = ""
        if(oldPerson != None): err = oldPerson.personID + " => "
        if(newPerson != None): err += newPerson.personID
        WriteLog("Cập nhật nhiều lượt vào thất bại", err + "\n" + str(e))
        return ErrorResponse(str(e))

####################################################################################################

@api_view(["POST"])           
def GetAnnotationList(request):
    try:
        jwt = None
        _token = GetParam(request, "token")
        if(_token == None or _token == ""):
            _secretkey = GetParam(request, "secretkey")
            jwt = GenerateLoginSession(_secretkey)
        else:
            jwt = api.auth.decode(_token)
             
        
        annotationList = QueryAnnotations(request, jwt)
        respond = Paging(request, annotationList)

        return ObjResponse(respond)
    except Exception as e:
        return ErrorResponse(str(e))

####################################################################################################

@api_view(["POST"])           
def MoveToNewPerson(request):
    try:
        _token = GetParam(request, "token")
        jwt = api.auth.decode(_token)

        _owner = GetParam(request, "owner")
        if(_owner == None or _owner == ""):
            _owner = jwt["owner"]

        _annotation_pk = GetParam(request, "annotation_pk")

        try:
            annotation = Annotation.objects.get(pk=_annotation_pk, isDeleted=False)
        except Annotation.MultipleObjectsReturned:
            return ErrorResponse("Trùng pk")
        except Annotation.DoesNotExist:
            ErrorResponse("Không tìm thấy lượt vào")

        oldPerson = None
        try:
            oldPerson = Person.objects.get(pk=annotation.person_pk, isDeleted=False)
            oldPerson.totalAnnotation = oldPerson.totalAnnotation - 1
            oldPerson.save()
        except Person.MultipleObjectsReturned:
            return ErrorResponse("Trùng pk")
        except Person.DoesNotExist:
            ErrorResponse("Không tìm thấy người")

        owner = User.objects.get(email=_owner, isDeleted=False)

        #create new person
        newPerson = Person(
            personID  = GeneratePersonID(owner),
            dateCreate = utcnow(),
            owner = _owner,
            totalAnnotation = 1
        )

        newPerson.dirName = GenerateDirname(newPerson)
        #move file to new dir
        oldImgPath = annotation.imagePath
        newImgPath = os.path.join(_owner, newPerson.personID, GetFileName(oldImgPath))

        MkDir( os.path.join(settings.MEDIA_ROOT, _owner, newPerson.personID))
        shutil.copy2(os.path.join(settings.MEDIA_ROOT, oldImgPath), os.path.join(settings.MEDIA_ROOT, newImgPath))
        
        
        newPerson.avatar = newImgPath
        newPerson.fullName = GetParam(request, "fullName")
        newPerson.fullName_ascii = unidecode(GetParam(request, "fullName"))
        newPerson.gender = GetParam(request, "gender")
        newPerson.phone = GetParam(request, "phone")
        newPerson.group_pk = GetParam(request, "group_pk")
        newPerson.groupName = GetParam(request, "groupName")
        _birthday = GetParam(request, "birthday")
        if(_birthday != None and _birthday != "" ):
            newPerson.birthday = _birthday
        newPerson.cmnd = GetParam(request, "cmnd")
        _issuedDate = GetParam(request, "issuedDate")
        if(_issuedDate != None and _issuedDate != ""):
            newPerson.issuedDate = _issuedDate
        newPerson.address = GetParam(request, "address")
        newPerson.note = GetParam(request, "note")
        newPerson.lastTimeAnnotation = oldPerson.lastTimeAnnotation
        newPerson.save()

        #delete old file encoding
        faceCore.RemoveLandmarkFile(oldImgPath)

        

        annotation.person_pk = str(newPerson.pk)
        annotation.person_id = newPerson.personID
        annotation.imagePath = newImgPath
        annotation.fullName = newPerson.fullName
        annotation.fullName_ascii = newPerson.fullName_ascii        
        annotation.save()
        
        AddActivity(jwt["email"], "Tạo khách mới từ lượt vào", oldPerson.personID + " => " + newPerson.personID)
        return SuccessResponse("Tạo khách hàng mới thành công")
            
    except Exception as e:
        return ErrorResponse(str(e))

####################################################################################################

@api_view(["POST"])           
def DeleteAnnotation(request):
    try:
        _token = GetParam(request, "token")
        jwt = api.auth.decode(_token)
            
        RequireLevel(jwt, ["Admin", "Root"])

        _annotation_pk = GetParam(request, "annotation_pk")
        
        try:
            annotation = Annotation.objects.get(pk=_annotation_pk, isDeleted=False)
        except Annotation.MultipleObjectsReturned:
            return ErrorResponse("Trùng annotation pk")
        except Annotation.DoesNotExist:
            return ErrorResponse("Lượt vào không tồn tại")

        person = Person.objects.get(pk=annotation.person_pk, isDeleted=False)
        person.totalAnnotation -= 1 
        person.save()
        UpdateAvatar(person)

        imagePathAbs = os.path.join(settings.MEDIA_ROOT, annotation.imagePath)
        RemoveFile(imagePathAbs)

        annotation.isDeleted = True
        annotation.save()

        AddActivity(jwt["email"], "Xóa lượt vào", "Annotation_pk: " + _annotation_pk)
        
        return SuccessResponse("Xóa lượt vào thành công")            
    except Exception as e:
        return ErrorResponse(str(e))

####################################################################################################

@api_view(["POST"])
def GetChartValue(request):
    try:
        _token = GetParam(request, "token")
        jwt = api.auth.decode(_token)        

        _owner = jwt["owner"]

        _fromDateStr = GetParam(request, "fromDate")
        _toDateStr = GetParam(request, "toDate")

        if(_fromDateStr == None or _fromDateStr == "" or
            _toDateStr == None or _toDateStr == ""):
            return ErrorResponse("Thiếu ngày ")
        _fromDate = parse(_fromDateStr) + datetime.timedelta(hours=-7) + datetime.timedelta(days=-1)
        _toDate = parse(_toDateStr) + datetime.timedelta(hours=-7)

        numDay = (_toDate - _fromDate).days


        arrayResult = []

        for i in range(numDay - 1):
            chartValue= None

            beginDay = _fromDate + timedelta(days=i + 1)
            endDay = _fromDate + timedelta(days=i + 2)

            try:
                strDate = beginDay.strftime("%d/%m/%Y")
                
                if(_owner == "root"):
                    chartValue = ChartValue.objects.get(dateRecord=strDate)
                else:
                    chartValue = ChartValue.objects.get(dateRecord=strDate, owner=_owner)
                already_existed = True
            except ChartValue.MultipleObjectsReturned:
                return ErrorResponse("Trùng dữ liệu chart ngày " + strDate)
            except ChartValue.DoesNotExist:
                already_existed = False

            if not already_existed or chartValue == None:
                chartValue = GenerateChartValue(_owner, beginDay, endDay)

            objDaySummary = {}
            objDaySummary["date"] = strDate
            objDaySummary["countOldAnnotation"] = chartValue.countOldAnnotation
            objDaySummary["countNewAnnotation"] = chartValue.countNewAnnotation

            arrayResult.append(objDaySummary)


        return ObjResponse(arrayResult)

    except Exception as e: 
        print(str(e))
        return ErrorResponse(str(e))

####################################################################################################

def GenerateChartValue(_owner, beginDay, endDay):
    try:
        beginDay = beginDay
        strDate = beginDay.strftime("%d/%m/%Y")

        if(_owner == "root"):
            oldAnnotations = Annotation.objects(timeAnnotation__gte=beginDay, timeAnnotation__lt=endDay, personExist=True, isDeleted=False)
            newAnnotations = Annotation.objects(timeAnnotation__gte=beginDay, timeAnnotation__lt=endDay, personExist=False, isDeleted=False)
        else:
            oldAnnotations = Annotation.objects(owner=_owner, timeAnnotation__gte=beginDay, timeAnnotation__lt=endDay, personExist=True, isDeleted=False)
            newAnnotations = Annotation.objects(owner=_owner, timeAnnotation__gte=beginDay, timeAnnotation__lt=endDay, personExist=False, isDeleted=False)

        try:
            chartValue = None
            if(_owner == "root"):
                chartValue = ChartValue.objects.get(dateSummary=strDate)
            else:
                chartValue = ChartValue.objects.get(owner=_owner, dateSummary=strDate)
            already_existed = True
        except ChartValue.MultipleObjectsReturned:
            already_existed = True
        except ChartValue.DoesNotExist:
            already_existed = False



        if not already_existed or chartValue == None:
            chartValue = ChartValue(
                owner = _owner,
                dateSummary = strDate,
                dateRecord = utcnow(),
                countOldAnnotation = len(oldAnnotations),
                countNewAnnotation = len(newAnnotations)
            )
            chartValue.save()

        return chartValue
    except Exception as e: 
        print(str(e))

####################################################################################################

@api_view(["POST"])           
def GetAnnotationSumup(request):
    try:
        _token = GetParam(request, "token")
        jwt = api.auth.decode(_token)

        _owner = GetParam(request, "owner")
        
        now = utcnow()
        _fromDate = datetime.datetime(now.year, now.month, now.day)        
        _toDate = datetime.datetime(now.year, now.month, now.day, hour=23, minute=59)        

        annotationList = Annotation.objects(timeAnnotation__gte=_fromDate, timeAnnotation__lt=_toDate, isDeleted=False)    

        if(_owner == None or _owner == ""):
            _owner = jwt["owner"]
        if(_owner != "all"):
            annotationList = annotationList(owner=_owner)

        countTotal =  annotationList.count()
        countGuest = annotationList.filter(Q(personType = 'Guest') |Q(personType = 'Khách')).count()
        obj = {
            "countStaff" : countTotal - countGuest,
            "countTotal" : countTotal,
            "countGuest" : countGuest
        }

        return ObjResponse(obj)
    except Exception as e:
        return ErrorResponse(str(e))

####################################################################################################

@api_view(["POST"])           
def UseAsSample(request):
    try:
        _token = GetParam(request, "token")
        jwt = api.auth.decode(_token)

        annotation_pk = RequireParamExist(request, "annotation_pk", "mã lượt vào")
        
        annotation = Annotation.objects.get(pk=annotation_pk, isDeleted=False)
        person = Person.objects.get(pk=annotation.person_pk, isDeleted=False)


        imagePathAbs = os.path.join(settings.MEDIA_ROOT, annotation.imagePath)
        #replace 2 times to run on Windows and Linux
        newPathAbs = imagePathAbs.replace("annotation/", "").replace("annotation\\", "")

        if(imagePathAbs == newPathAbs or os.path.exists(newPathAbs)):
            return ErrorResponse("Ảnh đang dùng làm ảnh mẫu rồi")

        shutil.copy2(imagePathAbs, newPathAbs)


        person.avatar = newPathAbs.replace(settings.MEDIA_ROOT, "")        
        person.save()
        
        AddActivity(jwt["owner"], "Dùng ảnh lượt vào làm ảnh mẫu", person.personID + " - " + person.fullName)

        return SuccessResponse("Dùng làm ảnh mẫu thành công")
    except Exception as e:
        return ErrorResponse(str(e))

####################################################################################################

@api_view(["POST"])
def ReportExcelAnnotation(request):
    try:
        _token = GetParam(request, "token")
        jwt = api.auth.decode(_token)
                                
        annotationList = QueryAnnotations(request, jwt)

        if(len(annotationList) == 0):
            return ErrorResponse("Không tìm thấy lượt ra vào")


        #excel part
        wb = Workbook()
        ws = wb.active
        fontTitle = Font(b=True, size=20)
        
        ws["A1"] ="DANH SÁCH LƯỢT RA VÀO"  
        
        border = Border()
        al = Alignment(horizontal="center", vertical="center")
        

        ws["B3"] = "Từ ngày"
        ws["B4"] = "Đến ngày"

        ws["C3"] = GetParam(request, "fromDate")
        ws["C4"] = GetParam(request, "toDate")

        style = NamedStyle(name="highlight")
        style_range(ws, "D3:D6", style)        

        column_list = ["STT", "MÃ SỐ", "HỌ TÊN", "PHÂN LOẠI", "SỐ ĐIỆN THOẠI",  "TRẠNG THÁI", "GIỜ VÀO", "GIỜ RA"]
        maxColumn = chr(ord('A') + len(column_list) - 1)
        style_range_merge(ws, "A1:" + maxColumn + "1", border=border, fill=None, font=fontTitle, alignment=al)
        
        ws.append(column_list)
        index = 1

        
        for annotation in annotationList:
            state = "Khách vào"
            if(annotation.personType in ["Staff", "Nhân viên"]):
                if(annotation.state == "Checked_in"):
                    state = "Nhân viên đi vào"
                else:
                    state = "Nhân viên ra về"

            row = []
            row.append(index)
            row.append("P" + str(annotation.person_id))
            row.append(annotation.fullName) 
            row.append("Nhân viên" if annotation.personType == "Staff" else "Khách")
            row.append(annotation.phone)
            row.append(state)
            row.append((annotation.timeAnnotation + timedelta(hours=7)).strftime("%d/%m/%Y %H:%M:%S"))
            if(annotation.timeCheckout != None):
                row.append((annotation.timeCheckout + timedelta(hours=7)).strftime("%d/%m/%Y %H:%M:%S"))
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



        table1_max_row = 7 + len(annotationList)
        create_table(ws, "Table1", "A7:" + maxColumn +"{}".format(table1_max_row))

        
        respond = createHttpRespond(wb)
        return respond
    except Exception as e: 
        return ErrorResponse(str(e))
        
# def variance_of_laplacian(frame_path):
#     # compute the Laplacian of the image and then return the focus
#     # measure, which is simply the variance of the Laplacian
#     frame = cv2.imread(frame_path)

#     [im_height, im_width] = frame.shape[:2]
#     if(im_width > 100):
#         newHeight = int(100 * im_height / im_width)
#         frame = cv2.resize(frame, (100, newHeight))

#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     return cv2.Laplacian(gray, cv2.CV_64F).var()


####################################################################################################

@api_view(["POST"])           
def GetAttendancesRealtime(request):
    try:
        jwt = None
        _token = GetParam(request, "token")
        if(_token == None or _token == ""):
            _secretkey = GetParam(request, "secretkey")
            jwt = GenerateLoginSession(_secretkey)
        else:
            jwt = api.auth.decode(_token)

        _fromDateStr = RequireParamExist(request, "fromDate", "ngày tháng")
        _toDateStr = RequireParamExist(request, "toDate", "ngày tháng")
        _fromDate = parse(_fromDateStr) + datetime.timedelta(hours=-7)
        _toDate = parse(_toDateStr) + datetime.timedelta(days=1) + datetime.timedelta(hours=-7)
        updated_person_list = []
        time_slots_list = []
        today = utcnow().date()
        now = (utcnow() + timedelta(hours=7)).strftime("%H:%M")
        
        personList = QueryPerson(request, jwt)
        for person in personList:
            annotationList = Annotation.objects(timeAnnotation__gte=_fromDate,person_pk = str(person.pk), timeAnnotation__lt=_toDate, isDeleted=False)
            inRelaxes = True
            lastCheckToday = ''
            if person.lastTimeAnnotation:
                lastCheckToday =  (person.lastTimeAnnotation + timedelta(hours=7)).strftime("%d/%m/%Y")
            lastCheck = ''
            if(lastCheckToday == today.strftime("%d/%m/%Y")):
                lastCheck = (person.lastTimeAnnotation + timedelta(hours=7)).strftime("%H:%M")
            ## kiểm tra trước giờ làm
            if person.startShift != None and person.startShift != '':
                if now < person.startShift:
                    if(lastCheck != '' and lastCheck != None and lastCheck < person.startShift):
                        setattr(person, 'realtime_color', 3)
                    else:
                        setattr(person, 'realtime_color', 1)
            else:
                setattr(person, 'realtime_color', 1)

            for slot in person.relaxes:
                start, end = slot.split(" - ")
                time_slots_list.append((start, end))
          
            for index, (start, end) in enumerate(time_slots_list):
                if start <= now <= end:
                    inRelaxes = True
                    break
                else:     
                    inRelaxes = False

            ##kiểm tra hiện tại nằm trong relax hay giờ làm
            if(inRelaxes):
                setattr(person, 'realtime_color', 1)
            else:
                if(lastCheck != '' and lastCheck != None):
                    if person.startShift != None and person.startShift != '':
                        hour, minute = map(int, person.startShift.split(":"))
                        minute += 5
                        if minute >= 60:
                            hour += 1
                            minute -= 60
                        new_time = f"{hour:02d}:{minute:02d}"
                        if lastCheck <= new_time:
                            setattr(person, 'realtime_color', 3)
                        else:
                            if annotationList.count() == 1:
                                setattr(person, 'realtime_color', 2)
                            elif annotationList.count() > 1:
                                check = False
                                for index, (start, end) in enumerate(time_slots_list):
                                    if start <= lastCheck <= end:
                                        check = True
                                        start_hour, start_minute = map(int, start.split(':'))
                                        lastCheck_hour, lastCheck_minute = map(int, lastCheck.split(':'))
                                        if start_minute == '0':
                                            if lastCheck_minute > 15:
                                                setattr(person, 'realtime_color', 3)
                                            else:
                                                setattr(person, 'realtime_color', 2)
                                        else:
                                            if lastCheck_minute > 45:
                                                setattr(person, 'realtime_color', 3)
                                            else:
                                                setattr(person, 'realtime_color', 2)
                                        break
                                    else:
                                        pass
                                if check == False:
                                    setattr(person, 'realtime_color', 2)
                    else:
                        setattr(person, 'realtime_color', 1)
                                        
                else:
                    setattr(person, 'realtime_color', 1)
            updated_person_data = {
                'id' : str(person.id),
                'fullName' : person.fullName,
                'personID' : person.personID,
                'realtime_color' : person.realtime_color,
            }
            updated_person_list.append(updated_person_data)
        return ObjResponse(updated_person_list)
    except Exception as e:
        printt(str(e))
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
