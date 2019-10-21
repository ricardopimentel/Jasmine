from django.conf.urls import url

from Jasmine.core import views

urlpatterns = [
    url(r'^home/(?P<user_u>.+)/(?P<printer_u>.+)/(?P<host_u>.+)/$', views.home, name='home'),
]
