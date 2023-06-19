from django.urls import re_path

from Jasmine.digitalizacoes import views

urlpatterns = [
    re_path(r'^escaneados/(?P<u_printer>.+)/(?P<u_filename>.+)/(?P<u_action>.+)/$', views.digitalizacoes, name='digitalizacoes'),
    re_path(r'^convert/(?P<u_printer>.+)/(?P<u_filename>.+)$', views.ocr, name='digitalizacoes_ocr'),
    re_path(r'^verificarocr/(?P<u_printer>.+)/(?P<u_filename>.+)$', views.verificarocr, name='verificar_ocr'),
    re_path(r'^verificarcompress/(?P<u_printer>.+)/(?P<u_filename>.+)$', views.verificarcompress, name='verificar_compress'),
    re_path(r'^compress/(?P<u_printer>.+)/(?P<u_filename>.+)$', views.compress, name='digitalizacoes_compress'),
]