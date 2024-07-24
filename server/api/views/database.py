from rest_framework.decorators import api_view
import datetime
from api.models import Phase, Building, Product
from mongoengine.queryset.visitor import Q
from dateutil.parser import parse
from api.apps import *
from django.conf import settings
import time
from api.auth import *

####################################################################################################

@api_view(["POST"])           
def UpdateDatabase(request):
    try:        
        _token = request.POST.get("token")        
        jwt = decode(_token)
        RequireLevel(jwt, ["Root"])

        if(request.POST.get("deletePhase") == "True"): 
            DeletePhase()
        if(request.POST.get("deleteOldField") == "True"): 
            DeleteOldField()

        return SuccessResponse("Cập nhật dữ liệu thành công")
    except Exception as e:
        return ErrorResponse("Có lỗi: " + str(e))

####################################################################################################

def UpdateHistoryField():
    products = Product.objects(isDeleted = False)
   
    count = 0
    for product in products:
        for cost in product.costs:
            found = False
            for i, history in enumerate(product.histories):
                if(history["dateUpload"] == cost["dateUpload"]):
                    found = True
                    break
            if(found):
                product.histories[i]["cost"] = cost["cost"]
            else:
                product.histories.append(cost)

        for price in product.prices:
            found = False
            for i, history in enumerate(product.histories):
                if(history["dateUpload"] == price["dateUpload"]):
                    found = True
                    break
            if(found):
                product.histories[i]["price"] = price["price"]
            else:
                product.histories.append(price)

        
        for inAmount in product.inAmounts:
            found = False
            for i, history in enumerate(product.histories):
                if(history["dateUpload"] == inAmount["dateUpload"]):
                    found = True
                    break
            if(found):
                product.histories[i]["inAmount"] = inAmount["amount"]
            else:
                product.histories.append({
                    "phase_pk" : inAmount["phase_pk"],
                    "dateUpload" : inAmount["dateUpload"],
                    "inAmount" : inAmount["amount"],
                })

        
        for outAmount in product.outAmounts:
            found = False
            for i, history in enumerate(product.histories):
                if(history["dateUpload"] == outAmount["dateUpload"]):
                    found = True
                    break
            if(found):
                product.histories[i]["outAmount"] = outAmount["amount"]
            else:
                product.histories.append({
                    "phase_pk" : outAmount["phase_pk"],
                    "dateUpload" : outAmount["dateUpload"],
                    "outAmount" : outAmount["amount"],
                })

        product.histories = sorted(product.histories, key=lambda x: x["dateUpload"])
        product.save()
        count +=1

####################################################################################################

def DeletePhase():
    phases = Phase.objects(buildingName="Phước Trung", isDeleted=False)
    for phase in phases:
        if(phase.type == "InAmount"):
            phase.isDeleted=True
            phase.save()

####################################################################################################

def DeleteOldField():
    products = Product.objects(isDeleted=False)
   
    for product in products:
        product.costs = None
        product.prices = None
        product.amounts = None
        product.inAmounts = None
        product.outAmounts = None
        product.save()