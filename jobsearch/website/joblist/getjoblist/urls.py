from django.conf.urls import url

from getjoblist import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^dicelist/(?P<pageNumber>[0-9]+)?$', views.dicelist, name='dicelist')
]