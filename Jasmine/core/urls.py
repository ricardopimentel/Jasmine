from django.conf.urls import url

from Jasmine.core import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
]