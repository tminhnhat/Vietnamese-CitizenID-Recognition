from rest_framework.decorators import api_view
import json
import hashlib
import datetime
from api.models import SearchOption
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from api.apps import *
from mongoengine.queryset.visitor import Q
from api.views.loginsession import *

####################################################################################################

@api_view(["POST"])           
def CreateSearchOption(request):
    _optionID = GetParam(request, 'optionID')
    _optionName = GetParam(request, 'optionName')

    try:
        option =  SearchOption.objects.get(optionID=_optionID) 
        already_existed = True
    except SearchOption.MultipleObjectsReturned:
        already_existed = True
    except SearchOption.DoesNotExist:
        already_existed = False

    if already_existed:
        return ErrorResponse("Option đã tồn tại")

    try:
        option = SearchOption(
            optionID = _optionID,
            optionName = _optionName
        )

        option.save()

        return SuccessResponse("Thêm option thành công")
    except Exception as e:
            return ErrorResponse(str(e))

####################################################################################################

# edit level
@api_view(["POST"])           
def UpdateSearchOption(request):
    try:
        _optionID = GetParam(request, 'optionID') 
        _smod       =  GetParam(request, 'smod') 
        _mod        =  GetParam(request, 'mod') 
        _staff      =  GetParam(request, 'staff') 
        _partner    =  GetParam(request, 'partner') 
        _guest      =  GetParam(request, 'guest') 

        _option =  SearchOption.objects.get(optionID=_optionID)

        verify_bool = lambda bool_arg : True if bool_arg  != None and bool_arg == "True" else False
        
        _option.smod = verify_bool(_smod)
        _option.mod = verify_bool(_mod)
        _option.staff = verify_bool(_staff)
        _option.partner = verify_bool(_partner)
        _option.guest = verify_bool(_guest)

        _option.save()

        return SuccessResponse("Cập nhật option thành công")
    except Exception as e:        
        return ErrorResponse(str(e))

####################################################################################################

@api_view(["POST"])           
def GetSearchOption(request):
    try:
        level = SearchOption.objects()
        return JsonResponse(level.to_json())
    except Exception as e:
        return ErrorResponse(str(e))

####################################################################################################
    
@api_view(["POST"])           
def GetSearchOptionList(request):
    try:
        _options = SearchOption.objects()
        return JsonResponse(_options.to_json())
    except Exception as e:
        return ErrorResponse(str(e))