from django.conf.urls import patterns, url
from handle import views

urlpatterns = patterns('',
    url(r'^register/$', views.register, name = 'register'),
    url(r'^login/$', views.login, name = 'login'),
    url(r'^logout/$', views.logout, name = 'logout'),
    url(r'^profile/(.*)$', views.profile_view, name = 'view person profile'),
    url(r'^editprofile/$', views.editProfile, name = 'edit person profile'),
    url( r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': './static/'}),
)
