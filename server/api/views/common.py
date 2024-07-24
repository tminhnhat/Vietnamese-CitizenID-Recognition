import datetime
import os
from django.conf import settings
from unidecode import unidecode
from api.apps import GetParam, RequireParamExist, printt
from api.models import Annotation, History
from lib.TGMT.TGMTfile import FindFileInDir
from dateutil.parser import parse
from datetime import timedelta
from mongoengine.queryset.visitor import Q

####################################################################################################


def CountPerson(owner):
    countDirHasImage = 0
    onwerDirAbs = os.path.join(settings.MEDIA_ROOT, owner.email)
    for fullpathDir, subdirs, files in os.walk(onwerDirAbs):
        if(fullpathDir == onwerDirAbs):
            for subdir in subdirs:
                subdirAbs = os.path.join(fullpathDir, subdir)
                filePaths = FindFileInDir(subdirAbs, "*.*", False, True)                
                if(len(filePaths) > 0):
                    countDirHasImage += 1

    return countDirHasImage

####################################################################################################

def QueryHistorys(request, loginSession):    
    _search_string = GetParam(request, "search_string")
    _fromDateStr = RequireParamExist(request, "fromDate", "ngày tháng")
    _toDateStr = RequireParamExist(request, "toDate", "ngày tháng")
    _owner = GetParam(request, "owner")
    _order_by = GetParam(request, 'order_by')
    _minPercent = GetParam(request, 'minPercent')
    _showKnownPersonOnly = GetParam(request, 'showKnownPersonOnly')
    _group_pk = GetParam(request, 'group_pk')
    _groupName = GetParam(request, 'groupName')

    _fromDate = parse(_fromDateStr) + timedelta(hours=-7)
    _toDate = parse(_toDateStr) + timedelta(days=1) + timedelta(hours=-7)

    historyList = History.objects(timeCreate__gte=_fromDate, timeCreate__lt=_toDate, isDeleted=False)
    # if(_minPercent != None and _minPercent != ""):
    #     _minPercent = int(_minPercent)
    #     historyList = historyList(percent__gte=_minPercent)


    
    # if(_showKnownPersonOnly != None and _showKnownPersonOnly == "True"):
    #     historyList = historyList(fullName__ne="Khách mới")

    # if(_groupName != None and _groupName != "" and _groupName != "all"):
    #     historyList = historyList(groupName=_groupName)

    if(_search_string != None and _search_string != ""):
        if(len(_search_string) == 24):
            historyList = historyList(person_pk__contains=_search_string)
        else:
            if(_search_string[0] == 'P'):
                _search_string = _search_string[1:]

            _search_string_ascii = unidecode(_search_string)
            historyList = historyList.filter(Q(fullName__icontains=_search_string) |
                                            Q(person_id__icontains=_search_string) |
                                            Q(fullName_ascii__icontains=_search_string_ascii))
    
    # if(_order_by != None and _order_by == "desc"):
    #     historyList = historyList.order_by("-timeHistory")

    return historyList

####################################################################################################

def QueryAnnotations(request, loginSession):    
    _search_string = GetParam(request, "search_string")
    _fromDateStr = RequireParamExist(request, "fromDate", "ngày tháng")
    _toDateStr = RequireParamExist(request, "toDate", "ngày tháng")
    _owner = GetParam(request, "owner")
    _order_by = GetParam(request, 'order_by')
    _minPercent = GetParam(request, 'minPercent')
    _showKnownPersonOnly = GetParam(request, 'showKnownPersonOnly')
    _group_pk = GetParam(request, 'group_pk')
    _groupName = GetParam(request, 'groupName')

    _fromDate = parse(_fromDateStr) + timedelta(hours=-7)
    _toDate = parse(_toDateStr) + timedelta(days=1) + timedelta(hours=-7)

    annotationList = Annotation.objects(timeCreate__gte=_fromDate, timeCreate__lt=_toDate, isDeleted=False)
    # if(_minPercent != None and _minPercent != ""):
    #     _minPercent = int(_minPercent)
    #     historyList = historyList(percent__gte=_minPercent)


    
    # if(_showKnownPersonOnly != None and _showKnownPersonOnly == "True"):
    #     historyList = historyList(fullName__ne="Khách mới")

    # if(_groupName != None and _groupName != "" and _groupName != "all"):
    #     historyList = historyList(groupName=_groupName)

    if(_search_string != None and _search_string != ""):
        if(len(_search_string) == 24):
            annotationList = annotationList(person_pk__contains=_search_string)
        else:
            if(_search_string[0] == 'P'):
                _search_string = _search_string[1:]

            _search_string_ascii = unidecode(_search_string)
            annotationList = annotationList.filter(Q(fullName__icontains=_search_string) |
                                            Q(person_id__icontains=_search_string) |
                                            Q(fullName_ascii__icontains=_search_string_ascii))
    
    # if(_order_by != None and _order_by == "desc"):
    #     historyList = historyList.order_by("-timeHistory")

    return annotationList