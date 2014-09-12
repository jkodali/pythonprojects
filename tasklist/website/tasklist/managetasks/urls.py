from django.conf.urls import patterns, include, url
from managetasks import views
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'tasklist.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^register/$', views.register, name='register'), 
    url(r'^login/$', views.user_login, name='user_login'),
    url(r'^$', views.index, name='index'),
    url(r'^logout/$', views.user_logout, name='logout'),
)
