# encoding: utf-8
# encoding: iso-8859-1
# encoding: win-1252

from django.conf.urls import url, include

from impressoes import views
from django.contrib import admin


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^jasmine/$', views.home),
    url(r'^jasmine/relatorio/(?P<user_u>.+)/(?P<printer_u>.+)/(?P<host_u>.+)/$', views.relatorios),
    url(r'^jasmine/viewlogs/(?P<user_u>.+)/(?P<action_u>.+)/(?P<host_u>.+)/$', views.viewlogs),
    url(r'^jasmine/print/$', views.imprimir),
    url(r'^jasmine/ajuda/(?P<topc>.+)$', views.ajuda),
    url(r'^jasmine/login/$', views.login),
    url(r'^jasmine/logout/$', views.logout),
    url(r'^jasmine/escaneados/(?P<printer>.+)/(?P<arquivo>.+)/(?P<action>.+)/$', views.get_scan, name='DocumentosDigitalizados'),
    url(r'^jasmine/convert/(?P<printer>.+)/(?P<arquivo>.+)$', views.ocr),
    url(r'^jasmine/admin/$', views.admin),
    url(r'^jasmine/admin/ad/$', views.dados_ad),
    url(r'^jasmine/admin/digi/$', views.pasta_digi),
    url(r'^jasmine/admin/tutoriais/add/$', views.add_tutorial),
    url(r'^jasmine/admin/tutoriais/(?P<Action>.+)/(?P<Id>.+)$', views.view_tutorial),
]
