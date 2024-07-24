from rest_framework.decorators import api_view
import json
from api.models import Building, Route
import api.auth
import datetime
from api.apps import *
from api.model_helper import IsPrimaryKey

####################################################################################################

#route manager screen
@api_view(["POST"])
def UpdateRoute(request):
    try:
        _token = GetParam(request, "token")
        loginSession = api.auth.decode(_token)
        RequireLevel(loginSession, ["Root", "Admin"])



        _route_pk = GetParam(request, 'route_pk')
        _name = GetParam(request, 'name')
        _nfcList = RequireParamExist(request, 'nfcList', "danh sách điểm tuần tra")
        _nfcNameList = RequireParamExist(request, 'nfcNameList', "danh sách điểm tuần tra")
        _building_pk = RequireParamExist(request, 'building_pk', "cửa hàng")
        
        building = Building.objects.get(pk=_building_pk, isDeleted=False)


        route = None

        try:
            if(IsPrimaryKey(_route_pk)):
                route = Route.objects.get(pk=_route_pk, isDeleted=False)
        except Route.DoesNotExist:
            pass

        if(route == None):
            route = Route(name = _name)

        route.name = _name
        route.NFClist = _nfcList
        route.NFCnames = _nfcNameList
        route.building_pk = _building_pk
        route.buildingName = building.name

        route.save()

        return SuccessResponse("Thêm tuyến tuần tra " + _name + " thành công")
    except Exception as e: 
        return ErrorResponse(str(e))

####################################################################################################

@api_view(["POST"])
def DeleteRoute(request):
    try:
        _token = GetParam(request, "token")
        loginSession = api.auth.decode(_token)
        RequireLevel(loginSession, ["Root", "Admin"])

        _pk = GetParam(request, 'pk')

        route = Route.objects.get(pk=_pk, isDeleted=False)
        route.isDeleted=True
        route.save()

        return SuccessResponse("Hủy tuyến tuần tra thành công")
    except Exception as e: 
        return ErrorResponse("Có lỗi: " + str(e))

####################################################################################################
    
@api_view(["POST"])
def GetRoute(request):
    try:
        _token = GetParam(request, "token")
        loginSession = api.auth.decode(_token)        

        _route_pk = GetParam(request, 'route_pk')

        route = Route.objects.get(pk=_route_pk, isDeleted=False)
        return JsonResponse(route.to_json())
    except Exception as e: 
        return ErrorResponse(str(e))

####################################################################################################

@api_view(["POST"])
def GetRouteList(request):
    try:
        _token = GetParam(request, "token")
        loginSession = api.auth.decode(_token)


        _building_pk = GetParam(request, 'building_pk')
        _includeDeleted = GetParam(request, 'includeDeleted') == "True"

        if(_includeDeleted):
            routes = Route.objects()
        else:
            routes = Route.objects(isDeleted=False)

        if(_building_pk != None and _building_pk != ""):
            routes = routes(building_pk=_building_pk)

        return JsonResponse(routes.to_json())
    except Exception as e: 
        return ErrorResponse(str(e))
        