from django.conf.urls import patterns, url
from submission import views

urlpatterns = patterns('',
    url(r'^viewsource/(?P<sid>\d+)$', views.viewsource, name = 'viewsource'),
    url(r'^viewdetail/(?P<sid>\d+)$', views.viewdetail, name = 'viewdetail'),
    url(r'^status/(?P<pid>\d+)$', views.problemSolvedSubmission, name = 'view solved problem submission'),
    url(r'^submit/$', views.submitcode, name = 'submit_code'),
    url(r'^userstatus/(?P<pid>\d+)$', views.userSubmission, name = 'view user problem submission'),
    url(r'^(.*)$', views.submission, name = 'submission'),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': './static/'}),
)
