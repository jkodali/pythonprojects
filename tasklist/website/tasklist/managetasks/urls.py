from django.conf.urls import patterns, include, url
from managetasks import views
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'tasklist.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^register/$', views.register, name='register'), 
)
