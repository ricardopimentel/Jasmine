# -*- coding: utf-8 -*-

from django import template
import os
import datetime
from Jasmine.impressoes.models import config


register = template.Library()

@register.filter
def get_at_index(list, index):
    return list[index]

@register.filter
def convert_datetime(data):
    return data.strftime("%d/%m/%Y %H:%M:%S")

@register.filter
def cut_string(texto, tamanho_max):
    tamanho = len(texto)
    if(tamanho > tamanho_max):
        texto = texto[tamanho - tamanho_max:]
    return texto

@register.filter
def split1000(s, sep='.'):
    s = str(s)
    return s if len(s) <= 3 else split1000(s[:-3], sep) + sep + s[-3:]

@register.filter
def data_arquivo(arquivo, printer):
    # Pega a pasta raiz do banco de dados
    raiz = (config.objects.get(id=1)).pasta_dig
    os.chdir(raiz+ '/'+ printer+ '/')
    return datetime.datetime.fromtimestamp(os.path.getmtime(arquivo))

@register.filter
def tam_arquivo(arquivo, printer):
    # Pega a pasta raiz do banco de dados
    raiz = (config.objects.get(id=1)).pasta_dig
    os.chdir(raiz+ '/'+ printer+ '/')
    num = os.path.getsize(arquivo)
    for x in ['bytes','KB','MB','GB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0
    return "%3.1f%s" % (num, 'TB')

@register.filter
def extensao_arquivo(arquivo):
    if arquivo[-3::] == 'pdf':
        return 'pdf'
    elif arquivo[-3::] == 'jpg':
        return 'jpg'
    elif arquivo[-3::] == 'tif':
        return 'tif'
    elif arquivo[-3::] == 'wps':
        return 'wps'
    else:
        return 'nada'

@register.filter
def codec(texto):
    return texto.decode("latin-1")

