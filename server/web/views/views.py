import mimetypes
from django.shortcuts import render, redirect
from django.http import HttpResponse
from rest_framework.decorators import api_view
from api.models import Building, LoginSession, PersonGroup, User
import datetime, time
from django.conf import settings
from api.views.loginsession import *
from api.auth import *
from api.views.systeminfo import GetSystemInfo, GetRealtimeInfo

def changepassword(request):
    permissions = ["all"]
    return CheckToken(request, 'changepassword.html', permissions)

def dashboard(request):
    permissions = ["Root", "Admin", "Manager", "Gate", "Staff", "Stocker"]
    return CheckToken(request, 'idcard.html', permissions)

def download(request, filepath):
    loginSession = GetLoginSession(request)
    if(loginSession == None):
        return render(request, "404.html")
    if(loginSession["email"] not in ["admin", "root"]):
        return render(request, "404.html")
    
    try:
        fileName = GetFileName(filepath)
        filepathAbs = os.path.join(settings.MEDIA_ROOT.replace("media", "download"), filepath)
        fsock = open(filepathAbs, "rb")
        mime_type_guess = mimetypes.guess_type(filepath)
        if mime_type_guess is not None:
            response = HttpResponse(fsock, content_type=mime_type_guess[0])
        response['Content-Disposition'] = 'attachment; filename=' + fileName
        return response
    except Exception as e:
        printt(str(e))
        return render(request, "404.html")
    
def database(request):
    permissions = ["Root"]
    return CheckToken(request, 'database.html', permissions)

def duplicate(request):
    permissions = ["Root", "anhvietlienket@gmail.com"]
    return CheckToken(request, 'duplicate.html', permissions)

def notification(request):
    permissions = ["Root", "Admin", "Gate", "Partner"]
    return CheckToken(request, 'notification.html', permissions)

def option(request):
    permissions = ["Root"]
    return CheckToken(request, "option.html", permissions)

@api_view(["POST", "GET"])
def login(request):
    permissions = ["Root", "Admin", "Gate", "Supporter"]
    return CheckToken(request, 'dashboard.html', permissions)

def logout(request):
    try:        
        _token = request.COOKIES.get('token')
        loginSession = LoginSession.objects.get(token=_token, isDeleted = False)
        loginSession.isDeleted = True
        loginSession.save()        
    except Exception as e:
        print(str(e))

    res = redirect('/login')
    res.delete_cookie("token")
    return res

def index(request):
    # _token = request.COOKIES.get('token')
    # if(_token == None or _token == ""):
    #     args = {'authorized': False}
    #     return render(request, 'index.html', args)        
    # else:
        if(IsValidToken(request)):
            return redirect("/dashboard")
        else:
            return redirect("/login")        
        

def register(request):
    _token = request.COOKIES.get('token')
    if(_token == None or _token == ""):
        args = {'authorized': False}
        return render(request, 'register.html', args)
    else:
        return redirect("/dashboard")

def profile(request):
    permissions = ["Root", "Admin", "Gate"]
    return CheckToken(request, 'profile.html', permissions)

def user(request):
    args = {}
    buildings = Building.objects(isDeleted=False).values_list('name')
    args["buildings"] = buildings.to_json()
    permissions = ["Root", "Admin"]
    return CheckToken(request, 'user.html', permissions, args)

def client(request):
    permissions = ["Root", "Admin"]
    return CheckToken(request, 'client.html', permissions)

def config(request):
    permissions = ["Root", "Admin"]
    return CheckToken(request, 'config.html', permissions)

def log(request):
    args = {'host' : settings.HOST}
    permissions = ["Root"]
    return CheckToken(request, 'log.html', permissions, args)

def phase(request):
    buildings = Building.objects(isDeleted = False).values_list("name")
    args = {}
    args["buildings"] = buildings.to_json()
    permissions = ["Root", "anhvietlienket@gmail.com"]
    return CheckToken(request, 'phase.html', permissions, args)

def GoogleSearchConsole(request):
    return render(request, 'google982c83694c1bf97e.html')

def systeminfo(request):
    args = GetSystemInfo()
    permissions = ["Root"]
    return CheckToken(request, 'systeminfo.html', permissions, args)


def idcard(request):
    permissions = ["Root", "Admin"]
    return CheckToken(request, 'idcard.html', permissions)
    
def Redirect(request):
        args = {
            'authorized': False,
            'version' : settings.VERSION,
            }
        return render(request, 'redirect.html' , args)
    
def CheckToken(request, redirect_page, permissions, args=None):
    isValidToken = False
    
    if(args == None):
        args = {}

    args['debug'] = settings.DEBUG
    args['authorized'] = False
    args['version'] = settings.VERSION
    args['numGateAccountAdded'] = 0
    args["permissions"] = "[]"

    if(not isValidToken):
        loginSession = GetLoginSession(request)
        if loginSession != None:
            args['email'] = loginSession["email"]
            args['level'] = loginSession["level"]
            args['owner'] = loginSession["owner"]

            for p in permissions:
                if(p == loginSession["level"]):
                    isValidToken = True
                    break

            if(not isValidToken):
                if(loginSession["email"] in permissions):
                    isValidToken = True

            if(not isValidToken):
                for permission in loginSession["permissions"]:
                    if(permission in permissions):
                        isValidToken = True
                        break

            printt(loginSession["email"])
            myProfile = User.objects.get(email=loginSession["email"], isDeleted=False)
            if (myProfile.permissions != None):
                args["permissions"] = json.dumps(myProfile.permissions) 

    if("all" in permissions or "Guest" in permissions):
        isValidToken = True
        
    if(isValidToken):
        args['authorized'] = True
        if("fullscreen" not in args):
            args['fullscreen'] = False
        return render(request, redirect_page , args)
    else:        
        args['fullscreen'] = True
        response = render(request, 'login.html', args)
        return response


def IsValidToken(request):
    try:
        _token = request.COOKIES.get('token')
        if(_token == None or _token == ""):
            _token = request.GET.get('token')
        if(_token == None or _token == ""):
            return False

        api.auth.decode(_token)
        return True
    except Exception as e:
        print(str(e))

        return False



def GetLoginSession(request):
    try:
        _token = request.COOKIES.get('token')
        if(_token == None or _token == ""):
            _token = request.GET.get('token')
        if(_token == None or _token == ""):
            return None

        loginSession = api.auth.decode(_token)
        return loginSession
    except Exception as e:
        printt(str(e))

    return None


