from web.views.views import CheckToken, GetLoginSession
from django.shortcuts import redirect
from api.models import Product, Building, Group, User, ProfitAlert
import json

def products(request): 
    args = {
        "profits" : []
    }    
    pk = request.GET.get('pk')
    if(pk != None and len(pk) == 24 and " " not in pk):
        product = Product.objects.get(pk=pk, isDeleted=False)
        args["product"] = product.to_json()

    groups = Group.objects(isDeleted=False)
    args["groups"] = groups.to_json()

    buildings = Building.objects(isDeleted = False).values_list("name")
    args["buildings"] = buildings.to_json()

    profits = ProfitAlert.objects(isDeleted=False).order_by("price")
    args["profits"] = profits.to_json() 

    permissions = ["Root", "Mod", "Cashier", "Stocker", "Staff", "anhvietlienket@gmail.com"]
    return CheckToken(request, 'products.html', permissions, args)

def compareproduct(request):
    permissions = ["Root", "anhvietlienket@gmail.com"]
    return CheckToken(request, 'compareproduct.html', permissions)

def compareprice(request):
    permissions = ["Root", "anhvietlienket@gmail.com"]
    return CheckToken(request, 'compareprice.html', permissions)

def inventory(request):
    permissions = ["Root", "anhvietlienket@gmail.com"]
    return CheckToken(request, 'inventory.html', permissions)

def check_cashier(request):
    permissions = ["Root", "anhvietlienket@gmail.com"]
    return CheckToken(request, 'check_cashier.html', permissions)

def setupprofit(request):
    permissions = ["Root", "anhvietlienket@gmail.com"]
    return CheckToken(request, 'setupprofit.html', permissions)

def stock(request):
    args = {}   
    buildings = Building.objects(isDeleted = False).values_list("name")
    args["buildings"] = buildings.to_json()

    permissions = ["Root", "Stocker", "anhvietlienket@gmail.com"]
    return CheckToken(request, 'stock.html', permissions, args)