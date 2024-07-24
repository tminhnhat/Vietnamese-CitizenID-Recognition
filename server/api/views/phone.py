from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json
from api.models import Phone
from api.apps import *
import datetime

####################################################################################################

@api_view(["GET", "POST"])           
def SendPhoneInfo(request):
    printt("----------------app start----------------")
    try:
        _phoneUDID = GetParam(request, "phoneUDID")
        _phoneName = GetParam(request, "phoneName")


        #send app info
        _appVersion = GetParam(request, "appVersion")        
        _user_id = GetParam(request, "user_id")
        _features = GetParam(request, "features")
        _infos= GetParam(request, "infos")
        
        phone = None
        try:
            phone = Phone.objects.get(phoneUDID=_phoneUDID, isDeleted=False)        
        except Phone.MultipleObjectsReturned:
            return ErrorResponse("Phone bị trùng UDID: " + _phoneUDID)
        except Phone.DoesNotExist:
            pass

        if(phone == None):
            phone = Phone(phoneUDID =_phoneUDID,
                        name = _phoneName,      
                        timeCreate = utcnow(),
                        )

        phone.userUsing = _user_id
        phone.lastRequestDate = utcnow()
        phone.appVersion = _appVersion
        phone.save()

        return JsonResponse(phone.to_json())

    except Exception as e:
        printt(str(e))
        return ErrorResponse("Có lỗi: " + str(e))

####################################################################################################

@api_view(["GET", "POST"])           
def GetPhoneList(request):
    try:
        _token = GetParam(request, "token")
        loginSession = api.auth.decode(_token)
            
        _building_id = GetParam(request, "building_id")
        _phoneID = GetParam(request, "phoneID") #last 6 chars of IMEI
        

        phones = Phone.objects(isDeleted = False)

        if(_phoneID != None and _phoneID != "" and _phoneID != " "):
            phones = phones(phoneUDID__endswith=_phoneID)

        return JsonResponse(phones.to_json())
    except Exception as e: 
        printt(str(e))
        return ErrorResponse("Có lỗi: " + str(e))

####################################################################################################

@api_view(["GET", "POST"])           
def UpdatePhone(request):
    try:
        _token = GetParam(request, "token")
        loginSession = api.auth.decode(_token)
            
        _phone_pk = GetParam(request, "phone_pk")
        _status = GetParam(request, "status")


        phone = Phone.objects.get(pk=_phone_pk, isDeleted = False)
        phone.status = _status
        phone.timeUpdate = utcnow()
        phone.userUpdate = loginSession["email"]
        phone.save()

        return JsonResponse(phone.to_json())
    except Exception as e: 
        printt(str(e))
        return ErrorResponse("Có lỗi: " + str(e))
