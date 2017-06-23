# encoding: utf-8
# encoding: iso-8859-1
# encoding: win-1252

from django.conf.urls import url, include

from Jasmine.core import views as core
from Jasmine.digitalizacoes import views as digitalizacoes
from django.contrib import admin


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^jasmine/$', core.home),
    url(r'^jasmine/relatorio/(?P<user_u>.+)/(?P<printer_u>.+)/(?P<host_u>.+)/$', core.relatorios),
    url(r'^jasmine/viewlogs/(?P<user_u>.+)/(?P<action_u>.+)/(?P<host_u>.+)/$', core.viewlogs),
    url(r'^jasmine/print/$', core.imprimir),
    url(r'^jasmine/ajuda/(?P<topc>.+)$', core.ajuda),
    url(r'^jasmine/login/$', core.login),
    url(r'^jasmine/logout/$', core.logout),
    url(r'^jasmine/escaneados/(?P<printer>.+)/(?P<arquivo>.+)/(?P<action>.+)/$', digitalizacoes.digitalizacoes, name='DocumentosDigitalizados'),
    url(r'^jasmine/convert/(?P<printer>.+)/(?P<arquivo>.+)$', digitalizacoes.ocr),
    url(r'^jasmine/compress/(?P<printer>.+)/(?P<arquivo>.+)$', digitalizacoes.compress),
    url(r'^jasmine/admin/$', core.admin),
    url(r'^jasmine/admin/ad/$', core.dados_ad),
    url(r'^jasmine/admin/digi/$', core.pasta_digi),
    url(r'^jasmine/admin/tutoriais/add/$', core.add_tutorial),
    url(r'^jasmine/admin/tutoriais/(?P<Action>.+)/(?P<Id>.+)$', core.view_tutorial),
]
