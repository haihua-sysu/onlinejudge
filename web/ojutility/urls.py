from django.conf.urls import patterns, url
from ojutility import views

urlpatterns = patterns('',
    url(r'^printError/(?P<errormsg>.+)$', views._printError),
    url(r'^printMessage/(?P<message>.+)$', views._printMessage),
)
