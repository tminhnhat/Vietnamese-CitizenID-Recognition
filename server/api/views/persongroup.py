from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json
import hashlib
import datetime
import api.auth
from api.models import PersonGroup, User, LoginSession
from api.apps import *
from api.views.loginsession import *


####################################################################################################

@api_view(["POST"])           
def GetPersonGroupList(request):
    try:
        _owner = GetParam(request, "owner")
        _token = GetParam(request, "token")

        if(_token == None or _token == ""):
            _secretkey = GetParam(request, "secretkey")            
            if(_owner == None or _owner == ""):
                owner = User.objects.get(secretkey=_secretkey, isDeleted=False)
                _owner = owner.email
        else:
            loginSession = api.auth.decode(_token)
            if(_owner == None or _owner == ""):
                _owner = loginSession["owner"]

        groupList = PersonGroup.objects(owner=_owner, isDeleted=False)

        return JsonResponse(groupList.to_json())
    except Exception as e:
        printt(str(e))
        return ErrorResponse(str(e))    

####################################################################################################

@api_view(["POST"])           
def GetPersonGroup(request):
    try:        
        _token = GetParam(request, "token")
        loginSession = api.auth.decode(_token)
        
        _groupID = GetParam(request, "group_id")
        if(_groupID == None or _groupID == ""):
            _group_id = loginSession.group_id

        group = PersonGroup.objects.get(groupID=_group_id, isDeleted=False)
           

        return JsonResponse(group.to_json())
    except Exception as e:
        return ErrorResponse(str(e))


####################################################################################################

@api_view(["POST"])           
def UpdatePersonGroup(request):
    try:
        _token = GetParam(request, "token")
        loginSession = api.auth.decode(_token)

        _group_pk = GetParam(request, "group_pk")
        _name = GetParam(request, "name")
        _bgColor = GetParam(request, "bgColor")
        _alert = GetParam(request, "alert") == "True"
        _ignore = GetParam(request, "ignore") == "True"

        group = None     
        if(_group_pk != None and len(_group_pk) == 24):
            try:                
                group = PersonGroup.objects.get(pk=_group_pk, isDeleted=False)                
            except PersonGroup.MultipleObjectsReturned:
                return ErrorResponse("Trùng group: " + _group_pk)
            except PersonGroup.DoesNotExist:
                pass

        if(group == None):
            group = PersonGroup(
                name = _name,
                alert =  _alert,
                owner=loginSession["email"]
            )

        group.name = _name
        group.bgColor = _bgColor
        group.alert = _alert
        group.ignore = _ignore
        group.timeUpdate = utcnow()
        group.userUpdate = loginSession["email"]
        group.save()

        return SuccessResponse("Cập nhật group thành công")
    except Exception as e:
        return ErrorResponse(str(e))

####################################################################################################

@api_view(["POST"])           
def RemovePersonGroup(request):
    try:
        _token = GetParam(request, "token")
        loginSession = api.auth.decode(_token)
            
        _group_pk = GetParam(request, "group_pk")    
        group = PersonGroup.objects.get(pk=_group_pk, isDeleted=False)
        
        group.isDeleted =  True
        group.timeUpdate = utcnow()
        group.save()

        return SuccessResponse("Xóa group thành công")
    except Exception as e:
        return ErrorResponse(str(e))