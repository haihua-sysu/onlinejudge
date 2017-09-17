from django.conf.urls import patterns, url
from course import views

urlpatterns = patterns('',
    url(r'^$', views.showCourseList),
    url(r'^course/(?P<courseid>\d+)$', views.showCourse),
    url(r'^course/(?P<courseid>\d+)/register/$', views.registerCourse),
    url(r'^course/(?P<courseid>\d+)/registerlist/$', views.viewRegisterList),
    url(r'^course/(?P<courseid>\d+)/regmanager/$', views.regManager),
)
