from django.urls import re_path

from Jasmine.administracao import views

urlpatterns = [
    re_path(r'^admin/$', views.admin, name='administracao'),
    re_path(r'^ajuda/(?P<topc>.+)$', views.ajuda, name='administracao_ajuda'),
    re_path(r'^admin/ad/$', views.dados_ad, name='administracao_ad'),
    re_path(r'^admin/digi/$', views.pasta_digi, name='administracao_digitalizacoes'),
    re_path(r'^admin/tutoriais/add/$', views.add_tutorial, name='administracao_tutoriais_add'),
    re_path(r'^admin/tutoriais/(?P<Action>.+)/(?P<Id>.+)$', views.view_tutorial, name='administracao_tutoriais'),
    re_path(r'^admin/logs/view/$', views.logs_view, name='administracao_logs_view'),
]