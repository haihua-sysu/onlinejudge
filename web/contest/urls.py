from django.conf.urls import patterns, url
from contest import views

urlpatterns = patterns('',
    url(r'^(?P<cid>\d+)$', views.showContest, name = 'showContest'),
    url(r'^(?P<cid>\d+)/(?P<pid>\d+)$', views.showContestProblem, name = 'showContestProblem'),
    url(r'^(?P<cid>\d+)/submission$', views.showSubmission, name = 'showSubmission'),
    url(r'^(?P<cid>\d+)/standing$', views.showOIStanding, name = 'showStanding'),
    url(r'^(?P<cid>\d+)/(?P<pid>\d+)/status$', views.showProblemSubmission, name = 'showProblemSubmission'),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': './static/'}),
)
