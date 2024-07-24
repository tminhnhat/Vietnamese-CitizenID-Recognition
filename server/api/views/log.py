from rest_framework.decorators import api_view
import datetime
from dateutil.parser import parse
from api.models import Log, User
from api.apps import *
from mongoengine.queryset.visitor import Q
from api.views.loginsession import *
from api.auth import *
from lib.TGMT.TGMTpaging import Paging

####################################################################################################

def WriteLog(activity, exception):
    try:
        log = Log(
            activity=activity,
            exception=exception,
            timeCreate = utcnow()
        )
        log.save()
        return True    
    except Exception as e:
        return False

####################################################################################################

@api_view(["POST"])           
def GetLogList(request):
    try:
        _token = request.POST.get("token")
        jwt = decode(_token)

        if(jwt["level"] not in["Root", "Admin"]):
            return ErrorResponse("Bạn không có quyền")

        _fromDateStr = request.POST.get("fromDate")
        _toDateStr = request.POST.get("toDate")

        _fromDate = parse(_fromDateStr) + datetime.timedelta(hours=-7)
        _toDate = parse(_toDateStr) + datetime.timedelta(days=1) + datetime.timedelta(hours=-7)

        logs = Log.objects(timeCreate__gte=_fromDate, timeCreate__lt=_toDate, isDeleted=False)

        _search_string = GetParam(request, "search_string")
        if(_search_string != None and _search_string != ""):
            if(len(_search_string) == 24):
                logs = logs(person_pk__contains=_search_string)
            else:
                if(_search_string[0] == 'P'):
                    _search_string = _search_string[1:]

                logs = logs.filter(Q(activity__icontains=_search_string) |
                                    Q(activity__icontains=_search_string))

        _order_by = request.POST.get('order_by')
        if(_order_by != None and _order_by == "desc"):
            logs = logs.order_by("-timeCreate")
        respond = Paging(request, logs)

        return ObjResponse(respond)
    except Exception as e:
        return ErrorResponse("Có lỗi: " + str(e))

####################################################################################################
