from django.apps import AppConfig
from rest_framework.response import Response
import json
import datetime
from django.conf import settings
import api.auth
from api.models import Log, User

ERROR_CODE = 399
SUCCESS_CODE = 200

####################################################################################################

class ApiConfig(AppConfig):
    name = 'api'

####################################################################################################

class ErrorResponse(Response):
    def __init__(self, message):
        printt(message)
        WriteLog("Exception", message)
        Response.__init__(self,
            {'Error': message},
            status=ERROR_CODE, content_type="application/json")

####################################################################################################

class SuccessResponse(Response):
    def __init__(self, message):
        Response.__init__(self,
            {'Success': message},
            status=SUCCESS_CODE, content_type="application/json")

####################################################################################################

class JsonResponse(Response):
    def __init__(self, jsonString):
        Response.__init__(self,
            json.loads(jsonString),
            status=SUCCESS_CODE, content_type="application/json")

####################################################################################################

class ObjResponse(Response):
    def __init__(self, jsonObj):
        Response.__init__(self,
            jsonObj,
            status=SUCCESS_CODE, content_type="application/json")

####################################################################################################

def utcnow():
    return datetime.datetime.utcnow()

def GetVNtime():
    return datetime.datetime.utcnow() + datetime.timedelta(hours=7) 

####################################################################################################

def RequireParamExist(request, param, paramName=None):
    if(paramName == None): paramName = param
    value = GetParam(request, param)
    if(value == None or value == ""):
        raise Exception("Thiếu tham số " + paramName)
    return value

####################################################################################################

def IsParamExist(request, param):
    value = GetParam(request, param)
    if(value == None or value == ""):
        return False
    return True

####################################################################################################

def RequireLevel(jwt, levels):
    if(jwt["level"] not in levels and jwt["email"] not in levels):
        raise Exception("Bạn phải đăng nhập để có thể thao tác")
    return True

####################################################################################################


def RequirePermissions(loginSession, permission):
    if(loginSession["level"] in ["Root", "Admin"]):
        return True
    user = User.objects.get(email=loginSession["email"], isDeleted=False)
    if(user.permissions == None or len(user.permissions) ==0 or permission not in user.permissions):
        raise Exception("Bạn không có quyền thực hiện chức năng này")
    return True
    
####################################################################################################

def GetParam(request, param, defaultValue=""):
    params = request.POST
    if(len(params) == 0):
        params = request.data    
    if(param not in params):
        return defaultValue
    if(params[param] == None):
        return defaultValue
    return params[param]


####################################################################################################

def printt(msg):
    if(settings.DEBUG):
        print(">>>>" + str(msg))

####################################################################################################

def IsValid(val):
    return val != None and val != ""

####################################################################################################

def IsPk(_pk):
    if(_pk == None or _pk == "" or len(_pk) != 24 or " " in _pk):
        return False
    return True

####################################################################################################

def WriteLog(_activity, _exception):
    try:
        log = Log(
            activity=_activity,
            exception=_exception,
            timeCreate = utcnow()
        )
        log.save()
        return True    
    except Exception as e:
        return False