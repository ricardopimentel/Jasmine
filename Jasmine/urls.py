from django.conf.urls import url, include

from Jasmine.core import views as core
from Jasmine.digitalizacoes import views as digitalizacoes
from Jasmine.administracao import views as administracao
from django.contrib import admin


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^jasmine/$', core.home),
    url(r'^jasmine/relatorio/(?P<user_u>.+)/(?P<printer_u>.+)/(?P<host_u>.+)/$', core.relatorios),
    url(r'^jasmine/viewlogs/(?P<user_u>.+)/(?P<action_u>.+)/(?P<host_u>.+)/$', administracao.viewlogs),
    url(r'^jasmine/print/$', core.imprimir),
    url(r'^jasmine/ajuda/(?P<topc>.+)$', core.ajuda),
    url(r'^jasmine/login/$', core.login),
    url(r'^jasmine/logout/$', core.logout),
    url(r'^jasmine/escaneados/(?P<printer>.+)/(?P<arquivo>.+)/(?P<action>.+)/$', digitalizacoes.digitalizacoes, name='DocumentosDigitalizados'),
    url(r'^jasmine/convert/(?P<printer>.+)/(?P<arquivo>.+)$', digitalizacoes.ocr),
    url(r'^jasmine/compress/(?P<printer>.+)/(?P<arquivo>.+)$', digitalizacoes.compress),
    url(r'^jasmine/admin/$', administracao.admin),
    url(r'^jasmine/admin/ad/$', administracao.dados_ad),
    url(r'^jasmine/admin/digi/$', administracao.pasta_digi),
    url(r'^jasmine/admin/tutoriais/add/$', administracao.add_tutorial),
    url(r'^jasmine/admin/tutoriais/(?P<Action>.+)/(?P<Id>.+)$', administracao.view_tutorial),
]
