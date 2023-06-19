
from django.urls import re_path

from Jasmine.relatorios import views

urlpatterns = [
    re_path(r'^relatorio/(?P<user_u>.+)/(?P<printer_u>.+)/(?P<host_u>.+)/$', views.relatorios, name='relatorios_impressoes'),
    re_path(r'^print/$', views.imprimir, name='relatorios_impressoes_pdf'),
]