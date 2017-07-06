from django.conf.urls import url

from Jasmine.administracao import views

urlpatterns = [
    url(r'^admin/$', views.admin, name='administracao'),
    url(r'^ajuda/(?P<topc>.+)$', views.ajuda, name='administracao_ajuda'),
    url(r'^admin/ad/$', views.dados_ad, name='administracao_ad'),
    url(r'^admin/digi/$', views.pasta_digi, name='administracao_digitalizacoes'),
    url(r'^admin/tutoriais/add/$', views.add_tutorial, name='administracao_tutoriais_add'),
    url(r'^admin/tutoriais/(?P<Action>.+)/(?P<Id>.+)$', views.view_tutorial, name='administracao_tutoriais'),
]