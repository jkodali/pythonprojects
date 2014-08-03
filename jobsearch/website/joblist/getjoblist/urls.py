from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from getjoblist import views
from rest_framework import viewsets, routers

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^api/v1/lastsearchtime$', views.LastSearchTimeList.as_view()),
    url(r'^api/v1/(?P<jobsite>\w+)/(?P<city>\w+)/(?P<searchstring>[\w\+]+)$', views.JobListAPI.as_view()),
    url(r'^savedjobs$', views.savedjobs, name='savedjobs'),
    url(r'^(?P<jobsite>\w+)/(?P<city>\w+)/(?P<searchstring>[\w\+]+)$', views.joblist, name='joblist')
]

urlpatterns = format_suffix_patterns(urlpatterns)