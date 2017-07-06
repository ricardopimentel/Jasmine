from django.conf.urls import url, include

from Jasmine.relatorios import views

urlpatterns = [
    url(r'^relatorio/(?P<user_u>.+)/(?P<printer_u>.+)/(?P<host_u>.+)/$', views.relatorios, name='relatorios_impressoes'),
    url(r'^print/$', views.imprimir, name='relatorios_impressoes_pdf'),
]