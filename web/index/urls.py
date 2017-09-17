from django.conf.urls import patterns, url
from index import views

urlpatterns = patterns('',
	url(r'^$', views.index, name = 'index'),
	url( r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': './static/'}),
)
