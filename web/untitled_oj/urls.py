from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'untitled_oj.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^handle/', include('handle.urls')),
    url(r'^problemset/', include('problemset.urls')),
    url(r'^submission/', include('submission.urls')),
    url(r'^administrate/', include('administrate.urls')),
    url(r'^courselist/', include('course.urls')),
    url(r'^contest/', include('contest.urls')),
    url(r'^rank/', include('rank.urls')),
    url(r'^utility/', include('ojutility.urls')),
    url(r'^$', include('index.urls')),
)
