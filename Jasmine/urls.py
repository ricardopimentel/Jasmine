from django.conf.urls import url, include

from Jasmine.core import views as core
from Jasmine.digitalizacoes import views as digitalizacoes
from Jasmine.administracao import views as administracao
from Jasmine.relatorios import views as relatorios
from Jasmine.login import views as login
from django.contrib import admin


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^jasmine/$', core.home),
    url(r'^jasmine/relatorio/(?P<user_u>.+)/(?P<printer_u>.+)/(?P<host_u>.+)/$', relatorios.relatorios),
    url(r'^jasmine/print/$', relatorios.imprimir),
    url(r'^jasmine/ajuda/(?P<topc>.+)$', administracao.ajuda),
    url(r'^jasmine/login/$', login.login),
    url(r'^jasmine/logout/$', login.logout),
    url(r'^jasmine/escaneados/(?P<u_printer>.+)/(?P<u_filename>.+)/(?P<u_action>.+)/$', digitalizacoes.digitalizacoes, name='DocumentosDigitalizados'),
    url(r'^jasmine/convert/(?P<u_printer>.+)/(?P<u_filename>.+)$', digitalizacoes.ocr),
    url(r'^jasmine/compress/(?P<u_printer>.+)/(?P<u_filename>.+)$', digitalizacoes.compress),
    url(r'^jasmine/admin/$', administracao.admin),
    url(r'^jasmine/admin/ad/$', administracao.dados_ad),
    url(r'^jasmine/admin/digi/$', administracao.pasta_digi),
    url(r'^jasmine/admin/tutoriais/add/$', administracao.add_tutorial),
    url(r'^jasmine/admin/tutoriais/(?P<Action>.+)/(?P<Id>.+)$', administracao.view_tutorial),
]
