from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json
import hashlib
import datetime
from api.models import LoginSession, Label
from mongoengine.queryset.visitor import Q
from dateutil.parser import parse
from api.apps import *
from django.conf import settings
import time
from django.core.files.storage import FileSystemStorage
from PIL import Image
from django.core.paginator import Paginator
from lib.TGMT.TGMTfile import *
from lib.TGMT.TGMTimage import *
from api.views.loginsession import *

####################################################################################################

@api_view(["POST"])           
def UpdateLabel(request):
    try:
        _token = GetParam(request, "token")
        loginSession = api.auth.decode(_token)

        _labelIndex = GetParam(request, "labelIndex")
        _labelName = GetParam(request, "labelName")

        try:
            label = Label.objects.get(labelIndex=_labelIndex, isDeleted=False)
            exist = True
        except Label.MultipleObjectsReturned:
            return ErrorResponse("Duplicate label: " + str(_labelIndex))
        except Label.DoesNotExist:
            exist = False

        if(exist):
            label.labelName = _labelName
            label.dateModify = utcnow()
        else:
            label = Label(
                labelIndex = _labelIndex,
                labelName = _labelName,
                dateModify = utcnow(),
            )
        
        label.save()

        return SuccessResponse("Cài đặt thành công")
    except Exception as e:
        return ErrorResponse(str(e))

####################################################################################################

@api_view(["POST"])           
def GetLabelList(request):
    try:
        #_token = GetParam(request, "token")
        #loginSession = api.auth.decode(_token)

        labels = Label.objects.filter(isDeleted=False).order_by("labelIndex")

        return JsonResponse(labels.to_json())
    except Exception as e:
        return ErrorResponse(str(e))

####################################################################################################

@api_view(["POST"])           
def DeleteLabel(request):
    try:
        _token = GetParam(request, "token")
        loginSession = api.auth.decode(_token)

        _labelIndex = GetParam(request, "labelIndex")
        label = Label.objects.get(labelIndex=_labelIndex, isDeleted=False)
        label.isDeleted = True
        label.save()

        return SuccessResponse("Delete label success")
    except Exception as e:
        return ErrorResponse(str(e))