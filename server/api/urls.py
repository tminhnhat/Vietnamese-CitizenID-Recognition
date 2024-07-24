from django.conf.urls import url
from . import views
from api.main import OnReady

OnReady()

urlpatterns = [
    url(r'^database/update$', views.UpdateDatabase),
    url(r'^diag/compare$', views.Compare),
    url(r'^diag/drawlandmark$', views.DrawLandmark),
    url(r'^diag/FindDirNotExistInDB$', views.FindDirNotExistInDB),
    url(r'^diag/FaceDirection$', views.FaceDirection),
    url(r'^diag/brightness$', views.CheckBrightness),    
    url(r'^loginsession/get$', views.GetLoginSession),
    url(r'^loginsession/verifyToken$', views.verifyToken),
    url(r'^loginsession/redirect$', views.Redirect),
    url(r'^log/getList$', views.GetLogList),
    url(r'^org/getList$', views.GetOrgList),
    url(r'^os/sendcommand$', views.SendCommand),    
    url(r'^label/update$', views.UpdateLabel),
    url(r'^label/getList$', views.GetLabelList),
    url(r'^label/delete$', views.DeleteLabel),
    url(r'^systeminfo/get$', views.GetSystemInfo),
    url(r'^systeminfo/backupdb$', views.BackupDB),
    url(r'^searchoption/create$', views.CreateSearchOption),
    url(r'^searchoption/get$', views.GetSearchOption),
    url(r'^searchoption/getList$', views.GetSearchOptionList),
    url(r'^searchoption/update$', views.UpdateSearchOption),
    url(r'^test/dlib$', views.TestDlib),
    url(r'^user/login$', views.login),
    url(r'^user/logout$', views.logout),    
    url(r'^user/update$', views.UpdateUser),
    url(r'^user/changepassword$', views.ChangePassword),
    url(r'^user/removeUser$', views.RemoveUser),
    url(r'^user/resetpassword$', views.ResetPassword),
    url(r'^user/SendEmailResetPassword$', views.SendEmailResetPassword),
    url(r'^user/get$', views.GetUser),
    url(r'^user/getList$', views.GetUserList),
    url(r'^user/register$', views.Register),    
    url(r'^systeminfo/isserverrunning$', views.IsServerRunning),
    url(r'^idcard$', views.ExtractIDCard),
]