from django.conf.urls import url, include

urlpatterns = [
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^jasmine/', include('Jasmine.core.urls')),
    url(r'^jasmine/', include('Jasmine.digitalizacoes.urls')),
    url(r'^jasmine/', include('Jasmine.administracao.urls')),
    url(r'^jasmine/', include('Jasmine.login.urls')),
    url(r'^jasmine/', include('Jasmine.relatorios.urls')),
]
