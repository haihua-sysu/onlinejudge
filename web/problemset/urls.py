from django.conf.urls import patterns, url
from problemset import views

urlpatterns = patterns('',
    url(r'^$', views.index, name = 'index'),
    url(r'^problem/(?P<pid>\d+)$', views.show_problem, name = 'show_problem'),
    url(r'^tag/(?P<tag>(.*))$', views.show_tagproblem, name = 'show_tagproblem'),
    url(r'^star/(?P<pid>\d+)$', views.star_problem, name = 'star_problem'),
    url(r'^note/(?P<pid>\d+)$', views.note, name = 'problem note'),
    url(r'^showstar$', views.show_star, name = 'show star problem'),
    url(r'^(.*)$', views.show_problemset, name = 'show_problemset'),
    url( r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': './static/'}),
)
