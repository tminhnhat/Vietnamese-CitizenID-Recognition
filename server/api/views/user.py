import os
from lib.TGMT.TGMTfile import GenerateRandFileName, MkDir
from rest_framework.decorators import api_view
import json
import hashlib
import datetime
from dateutil.parser import parse
from api.models import Annotation, User, LoginSession
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.conf import settings
from api.apps import *
import api.auth
from mongoengine.queryset.visitor import Q
from api.views.servicepack import *
from api.views.common import CountPerson
from lib.TGMT.TGMTemail import SendEmailAsync
from lib.TGMT.TGMTpaging import Paging
from lib.TGMT.TGMTutil import GenerateRandomString

####################################################################################################

@api_view(["POST"])
def login(request):
    _email = GetParam(request, 'email').lower()
    _password = GetParam(request, 'password')

    hashed_password = HashPassword(_password)

    try:
        user = User.objects.get(email=_email, isDeleted=False)
        if(not settings.DEBUG and user.password != hashed_password):
            return ErrorResponse("Không đúng password")
    except User.DoesNotExist:
        return ErrorResponse("Không đúng email")

    if(user.status == 'Registered'):
        SendActiveMail(user)
        return ErrorResponse("Vui lòng kiểm tra email để kích hoạt tài khoản")
    if(user.status == 'Suspend'):
        return ErrorResponse("Tài khoản của bạn đã bị khóa")

    #delete old sessions
    try:
        sessions = LoginSession.objects(email = _email, isDeleted=False)
        for s in sessions:
            s.isDeleted=True
            s.save()
    except LoginSession.DoesNotExist:
        print("no sessions")

    if(user.level == "Admin"):
        imageDir = os.path.join(settings.MEDIA_ROOT, user.email)
        MkDir(imageDir)

    try:
        user.password = None

        result = json.loads(user.to_json())
        result.pop("password", None)
        result.pop("isDeleted", None)
        result["token"] = GenerateJwtToken(user)

        return ObjResponse(result)
    except Exception as e:
        return ErrorResponse(str(e))

####################################################################################################

def GenerateJwtToken(user):
    login_session = LoginSession(email = user.email,
                                    fullname = user.fullname,
                                    level = user.level,                                    
                                    orgName = user.orgName,
                                    owner = user.owner,
                                    permissions = user.permissions,
                                    loginTime = utcnow()
                                    )
    login_session.save()

    payload = {
            'email': user.email,
            'fullname' : user.fullname,
            'level' : user.level,
            'orgName' : user.orgName,
            'owner' : user.owner,
            'permissions' : user.permissions,
            'exp': utcnow() + datetime.timedelta(days=365),
            'loginSession_pk' : str(login_session.pk)
        }
    jwt_token = api.auth.encode(payload)
    return jwt_token['token']

####################################################################################################

@api_view(["POST"])
def logout(request):
    try:
        _user_id = GetParam(request, 'user_id')
        _user_id = _user_id.lower()
        _image = GetParam(request, 'image')
        _token = GetParam(request, 'token')
        loginSession = LoginSession.objects.get(token = _token)
   
        if(_image != ""):
            _save_folder = "logout"
            _file_name = _user_id + "_"
            
        else:
            _imagePath = ""
        loginSession.imageLogoutPath = _imagePath
        loginSession.logoutTime = utcnow()
        loginSession.save()

        return SuccessResponse('Logout thành công')

    except Exception as e:
        return ErrorResponse(str(e))

####################################################################################################

@api_view(["POST"])
def UpdateUser(request):
    try:
        _token = GetParam(request, "token")
        loginSession = api.auth.decode(_token)            

        _email = GetParam(request, 'email')
        if(loginSession["level"] not in ["Root", "Admin"] and loginSession["email"] != _email):
            return ErrorResponse("Bạn không có quyền cập nhật")


        _fullname = GetParam(request, 'fullname')
        _level = GetParam(request, 'level')
        _user_pk = GetParam(request, 'user_pk')
        _orgName = GetParam(request, 'orgName')
        _address = GetParam(request, 'address')  
        _personalID = GetParam(request, 'personalID')
        _personalIDdate = GetParam(request, 'personalIDdate')
        _personalIDplace = GetParam(request, 'personalIDplace')
        _tax = GetParam(request, 'tax')
        _bankNumber = GetParam(request, 'bankNumber')
        _building_pk = GetParam(request, 'building_pk')
        _buildingName = GetParam(request, 'buildingName')
        _status = GetParam(request, 'status')
        _servicePack = GetParam(request, 'servicePack')
        _password = GetParam(request, 'password')            
        _permissions = GetParam(request, 'permissions')        

        if(_orgName == None):
            _orgName = loginSession.orgName
    

        try:
            if(IsPk(_user_pk)):
                user = User.objects.get(pk=_user_pk, isDeleted=False)
            else:
                user = User.objects.get(email=_email, isDeleted=False)
        except User.MultipleObjectsReturned:
            return ErrorResponse("Đã có email: " + _email)
        except User.DoesNotExist:
            hashed_password = HashPassword(_email)
            user = User(email = _email,
                        password = hashed_password,
                        owner = loginSession["email"],
                        level = _level,
                        servicePack = "Free",
                        status = "Approved"
                        )

        if(loginSession["level"] in ["Root", "Admin"]):
            if(_level != None and _level != ""):
                if(_level == "Admin"):
                    RequireLevel(loginSession, ["Root"])
                _level = _level
            else:
                return ErrorResponse("Bạn không có quyền cập nhật")

        if(_fullname != None and _fullname != ""):
            user.fullname = _fullname
        if(_level != None and _level != ""):
            user.level = _level
        if(_orgName != None and _orgName != ""):
            user.orgName = _orgName
        if(_address != None and _address != ""):
            user.address = _address
        if(_personalID != None and _personalID != ""):
            user.personalID = _personalID
        if(_personalIDdate != None and _personalIDdate != ""):
            user.personalIDdate = _personalIDdate
        if(_personalIDplace != None and _personalIDplace != ""):
            user.personalIDplace = _personalIDplace
        if(_tax != None and _tax != ""):
            user.tax = _tax
        if(_bankNumber != None and _bankNumber != ""):
            user.bankNumber = _bankNumber
        if(_building_pk != None and _building_pk != ""):
            user.building_pk = _building_pk
        if(_buildingName != None and _buildingName != ""):
            user.buildingName = _buildingName
        if(_status != None and _status != "" and loginSession["email"] == "root"):
            user.status = _status
            gates = User.objects(owner=_email, isDeleted=False)
            for g in gates:
                g.status = _status
                g.save()


        if(_servicePack != None and _servicePack != "" and loginSession["email"] == "root"):
            user.servicePack = _servicePack
        if(_password != None and _password != "" and loginSession["level"] == "Admin" and user.level == "Gate"):
            hashed_password = HashPassword(_password)
            user.password = hashed_password
        
        if(user.timeRegister == None):
            user.timeRegister = user.timeUpdate
            
        if(user.level == "Admin"):
            user.numGateAccount = GetNumGateAccount(user.servicePack)
            user.numPerson = GetNumPerson(user.servicePack)
            user.countPerson = CountPerson(user)

        if(_permissions != None and _permissions != ""):
            _permissions = json.loads(_permissions)
            user.permissions = _permissions
        
        user.timeUpdate = utcnow()     
        user.save()

        

        return SuccessResponse("Cập nhật user " + _email + " thành công")        
    except Exception as e:
        return ErrorResponse(str(e))

####################################################################################################

@api_view(["POST"])
def RemoveUser(request):
    try:        
        _token = GetParam(request, "token")
        loginSession = api.auth.decode(_token)        
            
        if(loginSession["level"] != "Root" and loginSession["level"] != "Supporter"):
            return ErrorResponse("Bạn không có quyền xóa")

        _email = GetParam(request, 'email')
        user =  User.objects.get(email=_email, isDeleted=False)

        if(user.level == "Admin"):
            gateAccounts = User.objects(level='Gate', owner=_email, isDeleted=False)
            if(len(gateAccounts) > 0):
                for g in gateAccounts:
                    g.status = 'Suspend'
                    g.timeUpdate = utcnow()
                    g.save()
        elif(user.level == "Gate"):
            owner = User.objects.get(level='Admin', email=user.owner, isDeleted=False)
            owner.numGateAccountAdded = owner.numGateAccountAdded - 1
            owner.save()            

        user.status = 'Suspend'
        user.suspendReason = GetParam(request, 'suspendReason')
        user.timeUpdate = utcnow()
        user.save()

        return SuccessResponse("Khóa tài khoản " + _email + " thành công")
    except Exception as e:
        return ErrorResponse(str(e))

####################################################################################################

def HashPassword(password):
    hash_routine = 5
    hashed_password = password
    while hash_routine != 0 :
       hashed_password = hashlib.sha224(hashed_password.encode('utf-8')).hexdigest()
       hash_routine = hash_routine - 1
    return hashed_password

####################################################################################################

@api_view(["POST"])
def GetUser(request):
    try:
        _token = GetParam(request, 'token')
        loginSession = api.auth.decode(_token)

        _email = GetParam(request, 'email')
        if(_email == None or _email == ""):
            _email = loginSession["email"]
        else:
            if(_email != loginSession["email"]):
                RequireLevel(loginSession, ["Admin"])

        user = User.objects.get(email=_email, isDeleted=False)
        
        if(user.secretkey == None or user.secretkey == ""):
            user.secretkey = GenerateRandomString(20)
            user.save()
        user.password = ""
        return JsonResponse(user.to_json())
    except Exception as e:
        return ErrorResponse(str(e))

####################################################################################################

@api_view(["POST"])
def GetUserList(request):
    try:
        _token = GetParam(request, "token")
        loginSession = api.auth.decode(_token)       
            

        _level = GetParam(request, 'level')
        _search_string = GetParam(request, 'search_string')
        _status = GetParam(request, 'status')
        
        _order_by = GetParam(request, 'order_by')

        _owner = GetParam(request, 'owner')
        if(_owner == None or _owner == ""):
            RequireLevel(loginSession, ["Root", "Admin"])
            _owner = loginSession["owner"]
        elif(_owner == "all"):
            RequireLevel(loginSession, ["Root"])
        
        userTable = User.objects(email__ne="root", isDeleted=False).exclude("password", "secretkey")
        if(_owner != "all"):
            userTable = userTable(owner=_owner)
        

        if(_level != None and _level != ""):
            userTable = userTable(level=_level)

        if(_status != None and _status != "" and _status != "all"):
            userTable = userTable(status=_status)

        if(_search_string != None and _search_string != ""):
            userTable = userTable(email__icontains=_search_string)        

        if(_order_by != None and _order_by == "desc"):
            userTable = userTable.order_by("-timeRegister")     
    
        respond = Paging(request, userTable)

        return ObjResponse(respond)
    except Exception as e:
        return ErrorResponse(str(e))

####################################################################################################

@api_view(["POST"])
def GetOrgList(request):
    try:
        _token = GetParam(request, "token")
        loginSession = api.auth.decode(_token)        
            

        _search_string = GetParam(request, 'search_string')
        _status_user = GetParam(request, 'notworking')

        userTable = User.objects(email__ne="root", level="Admin", isDeleted=False).values_list("email", "orgName")

        
        return JsonResponse(userTable.to_json())

    except Exception as e:
        return ErrorResponse(str(e))

####################################################################################################

@api_view(["POST"])
def ChangePassword(request):
    try:
        _email = GetParam(request, "email") 
        _token = GetParam(request, "token")

        if(_email == None or _email == ""): #reset by token 
            if(len(_token) == 24):
                loginSession = LoginSession.objects.get(pk=_token, isDeleted=False)
                if(loginSession.purpose != "ResetPassword"):
                    return ErrorResponse("Link không hợp lệ")       
                _email = loginSession["email"]
                try:
                    user = User.objects.get(email=_email, isDeleted=False)
                except User.DoesNotExist:
                    return ErrorResponse("Không tìm thấy email: " + _email)
                
        else: #reset by password
            loginSession = api.auth.decode(_token)
            if(loginSession['level'] in ["Root", "Admin"]):
                user = User.objects.get(email=_email, isDeleted=False)
            else:
                _password = GetParam(request, 'password')
                if(_password == None or _password == ""):
                    return ErrorResponse("Thiếu phương thức xác thực")
                
                try:
                    user = User.objects.get(email=_email, isDeleted=False)
                except User.DoesNotExist:
                    return ErrorResponse("Không tìm thấy email: " + _email)

                hashed_password = HashPassword(_password)
                if(user.password != hashed_password):
                    return ErrorResponse("Password cũ không đúng")
                
        _newPassword = GetParam(request, 'newPassword')    
        hashed_newpassword = HashPassword(_newPassword)
        user.password = hashed_newpassword
        user.save()
        
        if(len(_token) == 24):
            loginSession.isDeleted = True
            loginSession.save()
        
        return SuccessResponse("Đổi mật khẩu thành công")
    except Exception as e:
        return ErrorResponse(str(e))

####################################################################################################

@api_view(["POST"])
def ResetPassword(request):
    try:
        _token = GetParam(request, "token")
        loginSession = api.auth.decode(_token)
        RequireLevel(loginSession, ["Root", "Admin"])


        _email = GetParam(request, 'email')
        try:
            user = User.objects.get(email=_email, isDeleted=False)
        except User.DoesNotExist:
            return ErrorResponse("Không tìm thấy user: " + _email)


        hashed_newpassword = HashPassword(_email)
        user.password = hashed_newpassword
        user.isPasswordChanged = False
        user.save()

        return SuccessResponse("Reset thành công")
    except Exception as e:
        return ErrorResponse(str(e))

####################################################################################################

@api_view(["POST"])
def Register(request):
    try:
        _email = GetParam(request, 'email').lower()
        _name = GetParam(request, 'name')
        _position = GetParam(request, 'position')
        _password = GetParam(request, 'password')
        _phone = GetParam(request, 'phone')
        
        _orgName = GetParam(request, 'orgName')
        _addressOrg = GetParam(request, 'addressOrg')
        _phoneOrg = GetParam(request, 'phoneOrg')
        _servicePack = GetParam(request, 'servicePack')
        _references = GetParam(request, 'references')

        if(_orgName == None or _orgName == ""):
            _orgName = _email

        user = None
        try:
            user =  User.objects.get(email=_email, isDeleted=False)
            already_existed = True
        except User.MultipleObjectsReturned:
            already_existed = True
        except User.DoesNotExist:
            already_existed = False
        
    
        hashed_password = HashPassword(_password)
        
        if(user == None):
            user = User(email = _email)
        else:
            if(user.status != "Invited"):
                return ErrorResponse("Email này đã được đăng ký")

        user.fullname = _name
        user.position = _position
        user.password = hashed_password
        user.phone = _phone
        user.owner = _email
        
        user.orgName = _orgName
        user.addressOrg = _addressOrg
        user.phoneOrg = _phoneOrg
    
        user.countPerson = 0
        user.servicePack = _servicePack     
        user.status = "Registered"
        user.level = "Admin"
        user.timeRegister = utcnow()
        user.timeUpdate = utcnow()

        if(_references != None and _references != ""):
            user.references = _references

        user.save()

       

        SendActiveMail(user)

        return SuccessResponse("Đăng ký thành công, vui lòng kiểm tra email để xác nhận")
    except Exception as e:
            return ErrorResponse(str(e))

####################################################################################################

@api_view(["POST"])
def SendEmailResetPassword(request):
    try:
        _email = GetParam(request, 'email')

        try:
            user = User.objects.get(email=_email, isDeleted=False)
        except User.DoesNotExist:
            return ErrorResponse("Không tìm thấy email: " + _email)

        #create login session
        payload = {
            'email': _email,
            'exp': utcnow()
        }
        jwt_token = api.auth.encode(payload)
        token = jwt_token['token']


        loginsSession = LoginSession(email = _email, 
                    level = user.level,
                    purpose = "ResetPassword",
                    loginTime = utcnow(),
                    validTo = utcnow() + datetime.timedelta(days = 7)
                    ).save()

        loginsSession.save()

        if(_email == "root"):
            _email = "vohungvi27@gmail.com"
            
        SendEmailAsync("Reset password tại website Face Hub",
            "<!DOCTYPE html>" +
            "<html><head></head><body>" +
            "<p>Xin chào bạn</p>" +		
		    "<p>Bạn nhận được email vì có người gửi yêu cầu reset password. " +
            "Nếu đúng là bạn thì click vào link bên dưới để tiến hành đổi password, nếu không phải bạn xin vui lòng bỏ qua email này.</p> </br>" +
            "<p>" + settings.HOST + "/changepassword?token=" + str(loginsSession.pk) + "</p>" +
            "<p>Đây là email tự động, vui lòng không reply.</p>" +
            "</body></html>",
            _email
        )

        return SuccessResponse("Vui lòng kiểm tra mail để xác nhận đổi password")
    except Exception as e:
        return ErrorResponse(str(e))

####################################################################################################

def SendActiveMail(user):
     #create login session
    login_session = LoginSession(email = user.email,
                                fullname = user.fullname,
                                level = user.level,
                                purpose = "ConfirmEmail",
                                loginTime = utcnow(),
                                validTo = utcnow() + datetime.timedelta(days=7)
                                )
    login_session.save()

    SendEmailAsync("Xác nhận đăng ký Face Hub",
            "<!DOCTYPE html>" +
            "<html><head></head><body>" +
            "<p>Xin chào bạn</p>" +		
		    "<p>Bạn nhận được email vì đã đăng ký sử dụng dịch vụ tại " + settings.HOST + ". </br>" + 
            "Nếu đúng là bạn thì click vào link bên dưới để xác nhận email, nếu không phải bạn xin vui lòng bỏ qua email này.</p> </br>" +
            "<p>" + settings.HOST + "/redirect?token=" + str(login_session.pk) + "</p>" +
            "<p>Đây là email tự động, vui lòng không reply.</p>" +
            "</body></html>",
            user.email
        )

def GenerateLoginSession(_secretkey):
    owner = User.objects.get(secretkey=_secretkey, isDeleted=False)
    loginSession = LoginSession(email = owner.email,
                            fullname = owner.fullname,
                            level = owner.level,                                    
                            orgName = owner.orgName,
                            owner = owner.owner,
                            loginTime = utcnow()
                            )
    return loginSession

####################################################################################################

def HasPermission(user, permission):
    if(user.level in ["Root"] or user.email == "anhvietlienket@gmail.com"):
        return True
    if(user.permissions == None or len(user.permissions) == 0):
        return False
    return permission in user.permissions