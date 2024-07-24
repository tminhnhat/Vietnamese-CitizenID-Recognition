from rest_framework.decorators import api_view
import json
import hashlib
import datetime
import api.auth
from api.model_helper import IsPrimaryKey
from api.models import Building, User
from api.apps import *

####################################################################################################

@api_view(["POST"])           
def UpdateBuilding(request):
    try:
        _token = request.POST.get("token")
        loginSession = api.auth.decode(_token)
        RequireLevel(loginSession, ["Root", "anhvietlienket@gmail.com"])

        _building_pk = request.POST.get("building_pk")
        _name = RequireParamExist(request, "name") 
        _address = request.POST.get("address")


        building = None
        try:
            if(IsPrimaryKey(_building_pk) ):
                building = Building.objects.get(pk=_building_pk, isDeleted=False)
            else:
                building = Building.objects.get(name=_name, isDeleted=False)
        except Building.MultipleObjectsReturned:
            return ErrorResponse("Có nhiều cửa hàng: " + building.name)
        except Building.DoesNotExist:
            pass


        if(building == None):
            building = Building(
                name =  _name,
                address = _address,
                timeUpdate = utcnow())
        else:
            building.name =  _name
            building.address = _address
            building.timeUpdate = utcnow()

        building.save()

        return SuccessResponse("Cập nhật thành công")            
    except Exception as e: 
        return ErrorResponse(str(e))

####################################################################################################

@api_view(["POST"])           
def GetBuildingList(request):
    try:
        _token = request.POST.get("token")
        loginSession = api.auth.decode(_token)                    

        buildings = Building.objects(isDeleted=False) 
        return JsonResponse(buildings.to_json())
    except Exception as e: 
        return ErrorResponse(str(e))

####################################################################################################

@api_view(["POST"])           
def DeleteBuilding(request):
    try:
        _token = request.POST.get("token")
        loginSession = api.auth.decode(_token)
        RequireLevel(loginSession, ["Root"])


        _building_pk = request.POST.get("building_pk")

        building = Building.objects.get(pk=_building_pk, isDeleted=False)
        building.isDeleted = True
        building.timeUpdate = utcnow()
        building.save()
        return SuccessResponse("Xóa cửa hàng thành công")
    except Exception as e: 
        return ErrorResponse(str(e))