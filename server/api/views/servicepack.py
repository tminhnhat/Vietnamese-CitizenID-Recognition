from dateutil.parser import parse
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from api.apps import *
from mongoengine.queryset.visitor import Q

####################################################################################################

def GetNumGateAccount(servicePack):
    if(servicePack == "Free"):
        return 1
    if(servicePack == "Basic"):
        return 3
    if(servicePack == "Premium"):
        return 50
    if(servicePack == "Subscription"):
        return 1
    return 0

####################################################################################################

def GetNumPerson(servicePack):
    if(servicePack == "Free"):
        return 5
    if(servicePack == "Basic"):
        return 30
    if(servicePack == "Premium"):
        return 50
    if(servicePack == "Subscription"):
        return 1
    return 0