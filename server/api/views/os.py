from rest_framework.decorators import api_view
from dateutil.parser import parse
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from api.apps import *
from mongoengine.queryset.visitor import Q
from api.views.loginsession import *
import os
from django.conf import settings

####################################################################################################

# create level
@api_view(["POST"])           
def SendCommand(request):
    try:
        _token = request.POST.get("token")
        loginSession = FindLoginSession(_token)

        RequireLevel(loginSession, ["Root", "Admin"])
        if(loginSession["email"] not in ["root", "admin", "lovetodie100@yahoo.com"]):
            return ErrorResponse("Bạn không có quyền shutdown server")

        _command = request.POST.get('command')
        _command = "echo " + settings.OS_PASSWORD + " | sudo -S " + _command

        os.system(_command)
        
        return SuccessResponse("Thành công \n" + _command)
    except Exception as e:
        return ErrorResponse("Có lỗi: " + str(e))

####################################################################################################
