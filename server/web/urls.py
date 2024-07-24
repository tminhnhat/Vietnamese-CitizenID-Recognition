from django.conf.urls import url

from . import views
from django.contrib.sitemaps.views import sitemap
from idcard.sitemaps import StaticViewSitemap

sitemaps = {
    'static': StaticViewSitemap
}

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^404/$', views.notfound, name='notfound'),
    url(r'^download/(?P<filepath>[-\w./]+)/$', views.download),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^user/$', views.user, name='create_user'), 
    url(r'^diag/compare/$', views.compare),
    url(r'^diag/drawlandmark/$', views.draw_landmark),
    url(r'^diag/checkmedia/$', views.checkmedia),
    url(r'^diag/face_direction/$', views.face_direction),
    url(r'^diag/brightness/$', views.brightness),    
    url(r'^changepassword/$', views.changepassword, name='changepassword_manage'),   
    url(r'^terms/$', views.terms, name='terms'),
    url(r'^setupprofit/$', views.setupprofit),
    url(r'^faq/$', views.faq, name='faq'),
    url(r'^notification/$', views.notification, name='notification'),
    url(r'^userguide/$', views.userguide, name='userguide'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^config/$', views.config, name='config'),
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^log/$', views.log),
    url(r'^welcome/$', views.welcome, name='welcome'),
    url(r'^redirect/$', views.Redirect, name='Redirect'),    
    url(r'^sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    url(r'^systeminfo/$', views.systeminfo, name='systeminfo'),
    url(r'^stream_systeminfo/$', views.stream_systeminfo),
    url(r'^idcard/$', views.idcard),
    
]
handler404 = views.notfound
