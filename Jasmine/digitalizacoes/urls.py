from django.conf.urls import url

from Jasmine.digitalizacoes import views

urlpatterns = [
    url(r'^escaneados/(?P<u_printer>.+)/(?P<u_filename>.+)/(?P<u_action>.+)/$', views.digitalizacoes, name='digitalizacoes'),
    url(r'^convert/(?P<u_printer>.+)/(?P<u_filename>.+)$', views.ocr, name='digitalizacoes_ocr'),
    url(r'^verificarocr/(?P<u_printer>.+)/(?P<u_filename>.+)$', views.verificarocr, name='verificar_ocr'),
    url(r'^compress/(?P<u_printer>.+)/(?P<u_filename>.+)$', views.compress, name='digitalizacoes_compress'),
]