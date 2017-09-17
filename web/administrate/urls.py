from django.conf.urls import patterns, url
from administrate import views

urlpatterns = patterns('',
    url(r'^addproblem/$', views.addProblem, name = 'add new problem'),
    url(r'^addcontest/$', views.addContest, name = 'addcontest'),
    url(r'^addcourse/$', views.addCourse, name = 'add new course'),
    url(r'^viewproblemlist/(.*)$', views.viewProblemlist, name = 'views problemlist'),
    url(r'^viewuserlist/$', views.viewUserlist, name = 'views userlist'),
    url(r'^changestatus/(.*)$', views.changeStatus, name = 'change problem status'),
    url(r'^changeuserstatus/(.*)$', views.changeUserStatus, name = 'change user status'),
    url(r'^edit/(?P<pid>\d+)$', views.editProblem, name = 'edit problem'),
    url( r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': './static/'}),
)
