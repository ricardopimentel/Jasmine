from django.conf.urls import include
from django.urls import re_path

urlpatterns = [
    re_path(r'^tinymce/', include('tinymce.urls')),
    re_path(r'^jasmine/', include('Jasmine.core.urls')),
    re_path(r'^jasmine/', include('Jasmine.digitalizacoes.urls')),
    re_path(r'^jasmine/', include('Jasmine.administracao.urls')),
    re_path(r'^jasmine/', include('Jasmine.login.urls')),
    re_path(r'^jasmine/', include('Jasmine.relatorios.urls')),
]
