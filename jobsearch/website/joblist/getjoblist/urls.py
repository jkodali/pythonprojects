from django.conf.urls import url

from getjoblist import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<jobsite>\w+)/(?P<city>\w+)/(?P<searchstring>[\w\+]+)$', views.joblist, name='joblist')
]