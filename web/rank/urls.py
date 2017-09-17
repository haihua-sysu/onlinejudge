from django.conf.urls import patterns, url
from rank import views

urlpatterns = patterns('',
	url(r'^$', views.showRank, name = 'showrank'),
	url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': './static/'}),
)
