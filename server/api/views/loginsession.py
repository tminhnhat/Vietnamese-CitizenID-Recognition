from rest_framework.decorators import api_view
import json
import datetime
from dateutil.parser import parse
from api.models import User, LoginSession
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from api.apps import *
from mongoengine.queryset.visitor import Q
from lib.TGMT.TGMTemail import SendEmailAsync
from lib.TGMT.TGMTfile import *
from api.views.servicepack import GetNumGateAccount, GetNumPerson
from api.views.user import GenerateJwtToken
import api.auth
from django.conf import settings

####################################################################################################

@api_view(["POST"])
def GetLoginSession(request):
    try:
        _user_id = GetParam(request, 'user_id') 
        _userID = GetParam(request, 'userID')
        _building_id = GetParam(request, 'building_id')
        _fromDateStr = GetParam(request, "fromDate")
        _toDateStr = GetParam(request, "toDate")

        if(_fromDateStr == None or _fromDateStr == "" or
            _toDateStr == None or _toDateStr == "" or
            _building_id == None or _building_id == "" or
            _userID == None or _userID == ""):
            return ErrorResponse("Thiếu tham số")

        _fromDate = parse(_fromDateStr)
        _toDate = parse(_toDateStr) +  datetime.timedelta(days=1)

        if(_fromDate == None or _toDate == None):
            return ErrorResponse("Thiếu ngày")

        if(_building_id == "all"):
            histories = GetLoginSession.objects(loginTime__gte=_fromDate, loginTime__lt=_toDate)
        else:
            histories = GetLoginSession.objects(building_id = _building_id, loginTime__gte=_fromDate, loginTime__lt=_toDate)

        if(_userID != "all"):
            histories = histories(user_id=_userID)


        return JsonResponse(histories.to_json())
    except Exception as e:
        return ErrorResponse(str(e))

####################################################################################################

#demo how to verify token
@api_view(["POST"])
def verifyToken(request):
    try:
        _token = GetParam(request, 'token')
        loginSession = api.auth.decode(_token)
        return JsonResponse(loginSession.to_json())
    except Exception as e:        
        return ErrorResponse(str(e))

####################################################################################################

#demo how to verify token
@api_view(["POST"])
def Redirect(request):
    try:
        _token = GetParam(request, 'token')
        if _token == None or _token == "":
            return ErrorResponse("missing value")

        loginSession = LoginSession.objects.get(pk = _token, isDeleted=False)
        if(loginSession.purpose == "ConfirmEmail"):
            user = User.objects.get(email=loginSession["email"], isDeleted=False)
            message = "Xác nhận email thành công, chúng tôi sẽ chuyển bạn đến trang chủ"

            MkDir(os.path.join(settings.MEDIA_ROOT, user.owner))

            if(user.servicePack == "Free"):
                user.status = "Verified"
                user.numPerson = GetNumPerson(user.servicePack)
                user.numGateAccount = GetNumGateAccount(user.servicePack)
                user.save()
            else:
                message = "Vui lòng chờ phê duyệt gói dịch vụ " + user.servicePack
                SendEmailAsync("Có user đăng ký checkinwebcam.com",
                    "<!DOCTYPE html>" +
                    "<html><head></head><body>" +
                    
                    "<p> Có khách hàng " + loginSession["email"] + " vừa đăng ký gói " + user.servicePack + "</p>" +
                    "<p>https://checkinwebcam.com/user" +"</p>" +
                    "</body></html>",
                    "noreply@vohungvi.com"
                )

            result = {
                "redirectlink" : "/login",
                "Success" : message,
                "token" : GenerateJwtToken(user)
            }

            loginSession.isDeleted = True
            loginSession.save()

            if(user.references != None):
                try:
                    references =  User.objects.get(email=user.references, isDeleted=False)
                    references.numPerson = references.numPerson + 1
                    references.save()

                    SendEmailAsync(user.email + " đăng ký ID Card Reader thành công",
                        "<!DOCTYPE html>" +
                        "<html><head></head><body>" +
                        
                        "<p> Cảm ơn bạn đã giới thiệu " + user.email + "  đăng ký tài khoản.\
                            Số lượng khuôn mặt tối đa hiện tại là " + str(references.numPerson) + " khuôn mặt.</p>" +
                        "<p>Trân trọng</p>"
                        "</body></html>",
                        references.email
                    )
                    already_existed = True
                except User.MultipleObjectsReturned:
                    already_existed = True
                except User.DoesNotExist:
                    already_existed = False                

            
            return ObjResponse(result)
    except Exception as e:        
        return ErrorResponse(str(e))

####################################################################################################

def FindLoginSession(token):
    jwtDecoded = api.auth.decode(token)
    return jwtDecoded