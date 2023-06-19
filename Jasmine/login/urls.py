from django.urls import re_path

from Jasmine.login import views

urlpatterns = [
    re_path(r'^login/$', views.login, name='login'),
    re_path(r'^logout/$', views.logout, name='logout'),
    re_path(r'^primeiroacesso/$', views.primeiroacesso, name='primeiro_acesso'),
]