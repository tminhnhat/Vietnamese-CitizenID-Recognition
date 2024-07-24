from rest_framework.decorators import api_view
import json
import datetime
from dateutil.parser import parse
from api.models import Option
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from api.apps import *
from mongoengine.queryset.visitor import Q
from api.views.loginsession import *

####################################################################################################

@api_view(["POST"])           
def UpdateOption(request):
    try:
        _token = GetParam(request, 'token')
        loginSession = api.auth.decode(_token)

        _key = GetParam(request, 'key') 
        _value = GetParam(request, 'value')
        _note = GetParam(request, 'note')

        try:
            option =  Option.objects.get(key=_key, isDeleted=False)
        except Exception as e:
            option = Option(
                key=_key,
                
            )
        
        option.timeUpdate = utcnow()
        option.value=_value
        option.note=_note
        option.save()

        return SuccessResponse("Cập nhật option thành công")
    except Exception as e:        
        return ErrorResponse(str(e))

####################################################################################################

@api_view(["POST"])           
def GetOption(request):
    try:
        _key  =  GetParam(request, 'key')
        option =  Option.objects.get(key=_key, isDeleted=False)
        return JsonResponse(option.to_json())
    except Exception as e:
        return ErrorResponse(str(e))

####################################################################################################
    
@api_view(["POST"])           
def GetOptionList(request):
    try:
        _options = Option.objects(isDeleted=False)
        return JsonResponse(_options.to_json())
    except Exception as e:
            return ErrorResponse(str(e))

####################################################################################################

def IsAllowWrongShift():
    try:
        option =  Option.objects.get(key="allow_wrong_shift", isDeleted=False)        
        return option.value == "1" or option.value.lower() == "true"
    except Exception as e:
        return False
    