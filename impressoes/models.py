# -*- coding: utf-8 -*- 

from __future__ import unicode_literals
from django.db import models
from tinymce import models as tinymce_models


# Create your models here.
class jobs_log (models.Model):
    date = models.DateTimeField()
    job_id = models.CharField(max_length = 50)
    printer = models.CharField(max_length = 50)
    user = models.CharField(max_length = 50)
    server = models.CharField(max_length = 50)
    title = models.CharField(max_length = 400)
    copies = models.IntegerField()
    pages = models.IntegerField()
    options = models.CharField(max_length = 400)
    doc = models.CharField(max_length = 200)
    host = models.CharField(max_length = 50)
    
    def __str__(self):
        return self.job_id
    
class config(models.Model):
    pasta_dig = models.CharField(max_length = 200)
    dominio = models.CharField(max_length = 200)
    endservidor = models.CharField(max_length = 200)
    gadmin = models.CharField(max_length = 200)
    ou = models.CharField(max_length = 200)
    
class logs(models.Model):
    data = models.DateTimeField()
    action = models.CharField(max_length = 50) # Alt, Exc, Vis, Down
    item = models.CharField(max_length = 100) # Arquivo, Campo
    resumo = models.CharField(max_length = 300) # Exclusão do arquivo ***, Alteração do campo *** de *** para ***
    user = models.CharField(max_length = 50)
    ip = models.CharField(max_length = 50)
    
class tutoriais(models.Model):
    data = models.DateTimeField()
    titulo = models.CharField(max_length = 50) 
    texto = tinymce_models.HTMLField(max_length = 10000)
    user = models.CharField(max_length = 50)