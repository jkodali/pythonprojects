from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'joblist.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

	url(r'^getjoblist/', include('getjoblist.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
