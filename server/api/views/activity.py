from rest_framework.decorators import api_view
import json
import hashlib
import datetime
from dateutil.parser import parse
from unidecode import unidecode
from api.models import Activity, User
from api.apps import *
from mongoengine.queryset.visitor import Q
from api.views.loginsession import *
from api.auth import *
from lib.TGMT.TGMTpaging import Paging

####################################################################################################

def AddActivity(email, activity, value,product_pk = None, product_unit=None, changes=[]):
    try:
        activity = Activity(
            email=email,
            activity=activity,
            product_pk=product_pk,            
            value=value,
            unit = product_unit,
            changes=changes,
            timeCreate = utcnow()
        )
        activity.save()
        return True    
    except Exception as e:
        return False

####################################################################################################

@api_view(["POST"])           
def GetActivityList(request):
    try:
        _token = request.POST.get("token")
        loginSession = api.auth.decode(_token)
        _product_pk = request.POST.get("product_pk")
        _type = GetParam(request, "type")
        _email = GetParam(request, "email")
       
        if(loginSession["level"] not in["Root", "Admin"]):
            return ErrorResponse("Bạn không có quyền")
        
        if(IsPk(_product_pk)):
            activities = Activity.objects(product_pk=_product_pk, isDeleted=False)
        else:
            activities = Activity.objects(isDeleted=False)

        if(_type != '' and _type != 'All'):
            activities = activities(activity = _type)
        
        if(_email != ''):
            activities = activities(email = _email)
    
        

        _fromDateStr = request.POST.get("fromDate")
        _toDateStr = request.POST.get("toDate")
        _owner = GetParam(request, "owner")
         
        if(_fromDateStr != None and _fromDateStr != '' and _toDateStr != None and _toDateStr != ''):
            _fromDate = parse(_fromDateStr) + datetime.timedelta(hours=-7)
            _toDate = parse(_toDateStr) + datetime.timedelta(days=1) + datetime.timedelta(hours=-7)
            activities = activities(timeCreate__gte=_fromDate, timeCreate__lt=_toDate)  
       
        if(_owner == None or _owner == ""):
            _owner = loginSession["owner"]
        if(_owner == "all"):
            RequireLevel(loginSession, "Root")
        else:
            activities = activities(email=_owner)

    
        _search_string = GetParam(request, "search_string")
        if(_search_string != None and _search_string != ""):
            if(len(_search_string) == 24):
                activities = activities(person_pk__contains=_search_string)
            else:
                activities = activities.filter(Q(email__icontains=_search_string) |
                                                Q(activity__icontains=_search_string) |
                                                Q(value__icontains=_search_string))

        _order_by = request.POST.get('order_by')
        if(_order_by != None and _order_by == "desc"):
            activities = activities.order_by("-timeCreate")
        respond = Paging(request, activities)

        return ObjResponse(respond)
    except Exception as e:
        return ErrorResponse("Có lỗi: " + str(e))

####################################################################################################
