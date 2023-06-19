from django.urls import re_path

from Jasmine.core import views

urlpatterns = [
    re_path(r'^home/(?P<user_u>.+)/(?P<printer_u>.+)/(?P<host_u>.+)/$', views.home, name='home'),
    re_path(r'^$', views.redi, name='redirect'),
]
