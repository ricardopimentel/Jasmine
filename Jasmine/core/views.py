# -*- coding: utf-8 -*-

import datetime
from os.path import join

from django.contrib import messages
from django.db import connection
from django.http.response import HttpResponse
from django.shortcuts import render_to_response, render, redirect
from django.template import Context
from django.template.context import RequestContext
from django.template.loader import get_template 
from django.views.decorators.csrf import csrf_exempt
import os
import glob
import sys
import platform

from Jasmine.administracao.forms import AdForm
from Jasmine.core.forms import LoginForm
from Jasmine.core.models import config, tutoriais, logs
import pdfkit
import shutil
import pypdfocr.pypdfocr as OCR

# Create your views here.
def home(request):
    cursor = connection.cursor()
    cursor.execute("SELECT user, SUM(pages) as total FROM core_jobs_log GROUP BY user HAVING total >= 0 ORDER BY total DESC LIMIT 5")
    top_users = cursor.fetchall()
    cursor.execute("SELECT printer, SUM(pages) as total FROM core_jobs_log GROUP BY printer HAVING total >= 0 ORDER BY total DESC LIMIT 5")
    top_printers = cursor.fetchall()
    cursor.execute("SELECT host, SUM(pages) as total FROM core_jobs_log GROUP BY host HAVING total >= 0 ORDER BY total DESC LIMIT 5")
    top_hosts = cursor.fetchall()
    
    # Preparando cores dos gráficos
    cores_primarias = ['#F746A', '#46BFBD', '#FDB45C', '#512DA8', '#C2185B']
    cores_secundarias = ['#FF5A5E', '#5AD3D1', '#FFC870', '#673AB7', '#E91E63']
    
    return render(request, 'index.html', {
                           'title': 'Home',
                           'top_users': top_users,
                           'top_printers': top_printers,
                           'top_hosts': top_hosts,
                           'cores_primarias': cores_primarias,
                           'cores_secundarias': cores_secundarias,
                           'itemselec': 'HOME',
                         })


@csrf_exempt
def relatorios(request, user_u, printer_u, host_u):
    #preparação dos parametros iniciais
    data_final = datetime.datetime.today()
    data_inicial = datetime.datetime.fromordinal(data_final.toordinal()-30)
    titulo = "Impressões dos Ultimos 30 dias"
    user_U = user_u
    printer_U = printer_u
    host_U = host_u
    err = ''
    
    #Verificar dados salvos na sessão
    try:
        #Se tiver data salva na sessão
        if(request.session['data_inicial']):
            data_inicial = request.session['data_inicial'] # Pega data da sessão
            titulo = 'Impressões no periodo de '+ datetime.datetime.strptime(str(data_inicial), '%Y-%m-%d').strftime('%d/%m/%Y') #atualiza titulo
        if(request.session['data_final']):
            data_final = request.session['data_final'] # Pega data da sessão
            titulo = titulo+ ' a '+ datetime.datetime.strptime(str(data_final), '%Y-%m-%d').strftime('%d/%m/%Y') #atualiza titulo
        if(request.session['user']):
            user_u = request.session['user'] # Pega usuário da sessão
        if(request.session['printer']):
            printer_u = request.session['printer'] # Pega impressora da sessão
        if(request.session['host']):
            host_u = request.session['host'] # Pega host da sessão
    except:
        pass
    
    #Parametros por URL
    #substituir espaços na url por vazio
    if(user_U == ' '):
        user_u = ''
        request.session['user'] = user_u
    elif(not user_U == 'user'):
        request.session['user'] = user_U
        user_u = user_U
    if(printer_U == ' '):
        printer_u = ''
        request.session['printer'] = printer_u
    elif(not printer_U == 'printer'):
        request.session['printer'] = printer_U
        printer_u = printer_U
    if(host_U == ' '):
        host_u = ''
        request.session['host'] = host_u
    elif(not host_U == 'host'):
        request.session['host'] = host_U
        host_u = host_U
        
    #verificar se URL é http://localhost:8000/relatorio/*user*/*printer*/*host*/ essa url é o inicio padrão da página relatório
    if(user_U == '*user*' and printer_U == '*printer*' and host_U == '*host*'):
        titulo = 'Relatório de Impresões'
    
    # Parametros pelo método POST
    #Verificar se veio algum parametro pelo post
    if(request.POST): # caso tenha vindo
        #verifica se veio usuário pelo post
        if(request.POST['user-r']):
            user_u = request.POST['user-r']
            if(user_u == ' '):
                user_u = ''
            # Salvar a user na sessão
            request.session['user'] = user_u
        #verifica se veio impressora pelo post
        if(request.POST['printer-r']):
            printer_u = request.POST['printer-r']
            if(printer_u == ' '):
                printer_u = ''
            # Salvar a printer na sessão
            request.session['printer'] = printer_u
        #verifica se veio host pelo post
        if(request.POST['host-r']):
            host_u = request.POST['host-r']
            if(host_u == ' '):
                host_u = ''
            # Salvar a host na sessão
            request.session['host'] = host_u
        #verifica se veio data inicial pelo post
        if(request.POST['data-inicial']):
            data_inicial = request.POST['data-inicial']
            # Salvar a data inicial na sessão
            request.session['data_inicial'] = data_inicial
            titulo = 'Impressões no período de '+ datetime.datetime.strptime(str(data_inicial), '%Y-%m-%d').strftime('%d/%m/%Y') #atualiza titulo
        #verifica se veio data final pelo post
        if(request.POST['data-final']):
            data_final = request.POST['data-final']
            # Salvar a data final na sessão
            request.session['data_final'] = data_final
            titulo = titulo+ ' a '+ datetime.datetime.strptime(str(data_final), '%Y-%m-%d').strftime('%d/%m/%Y') #atualiza titulo
        #Verifica se há erros no formulario
        if(data_inicial > data_final):
            err = "Erro no intervalo da data"
            titulo = 'Relótorio de Impressões'
            
    #preparando consultas ao banco de dados
    cursor = connection.cursor()
    cursor.execute("SELECT user FROM core_jobs_log where user != '' GROUP BY user")
    top_users = cursor.fetchall()
    cursor.execute("SELECT printer FROM core_jobs_log where printer != '' GROUP BY printer")
    top_printers = cursor.fetchall()
    cursor.execute("SELECT host FROM core_jobs_log where host != '' GROUP BY host")
    top_hosts = cursor.fetchall()
    cursor.execute("SELECT date, user, printer, host, title, pages FROM `core_jobs_log` WHERE user like '%"+user_u+"%' and printer like '%"+printer_u+"%' and host like '%"+host_u+"%' and (date BETWEEN '"+str(data_inicial)+" 00:00:00' and '"+str(data_final)+" 23:59:59' )")
    resultado = cursor.fetchall()
    cursor.execute("SELECT SUM(pages) as total FROM `core_jobs_log` WHERE user like '%"+user_u+"%' and printer like '%"+printer_u+"%' and host like '%"+host_u+"%' and (date BETWEEN '"+str(data_inicial)+" 00:00:00' and '"+str(data_final)+" 23:59:59' )")
    soma = cursor.fetchall()
    
    # Finalizando renderização da página
    return render(request, 'relatorio.html', {
                             'title': 'Relatório',
                             'top_users': top_users,
                             'top_printers': top_printers,
                             'top_hosts': top_hosts,
                             'resultado': resultado,
                             'titulo_relat': titulo,
                             'inicial': str(data_inicial),
                             'final': str(data_final),
                             'user': user_u,
                             'printer': printer_u,
                             'host': host_u,
                             'soma': soma,
                             'err': err,
                             'itemselec': 'RELATÓRIOS',
                             })


def imprimir(request):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    #preparação dos parametros iniciais
    data_final = datetime.datetime.today()
    data_inicial = datetime.datetime.fromordinal(data_final.toordinal()-30)
    user_u = ''
    printer_u = ''
    host_u = ''

    #Verificar dados salvos na sessão
    try:
        #Se tiver data salva na sessão
        if(request.session['data_inicial']):
            data_inicial = request.session['data_inicial'] # Pega data da sessão
            titulo = 'Impressões no periodo de '+ datetime.datetime.strptime(str(data_inicial), '%Y-%m-%d').strftime('%d/%m/%Y') #atualiza titulo
        if(request.session['data_final']):
            data_final = request.session['data_final'] # Pega data da sessão
            titulo = titulo+ ' a '+ datetime.datetime.strptime(str(data_final), '%Y-%m-%d').strftime('%d/%m/%Y') #atualiza titulo
        if(request.session['user']):
            user_u = request.session['user'] # Pega usuário da sessão
        if(request.session['printer']):
            printer_u = request.session['printer'] # Pega impressora da sessão
        if(request.session['host']):
            host_u = request.session['host'] # Pega host da sessão
    except:
        pass
    
    cursor = connection.cursor()
    cursor.execute("SELECT date, user, printer, host, title, pages FROM `core_jobs_log` WHERE user like '%"+user_u+"%' and printer like '%"+printer_u+"%' and host like '%"+host_u+"%' and (date BETWEEN '"+str(data_inicial)+" 00:00:00' and '"+str(data_final)+" 23:59:59' )")
    resultado = cursor.fetchall()
    cursor.execute("SELECT SUM(pages) as total FROM `core_jobs_log` WHERE user like '%"+user_u+"%' and printer like '%"+printer_u+"%' and host like '%"+host_u+"%' and (date BETWEEN '"+str(data_inicial)+" 00:00:00' and '"+str(data_final)+" 23:59:59' )")
    soma = cursor.fetchall()
    template = get_template("relat2print.html")
    
    context = Context({
                       'title': 'Relatório PDF',
                       'pagesize':'A4',
                       'resultado': resultado,
                       'inicial': datetime.datetime.strptime(str(data_inicial), '%Y-%m-%d').strftime('%d/%m/%Y'),
                       'final': datetime.datetime.strptime(str(data_final), '%Y-%m-%d').strftime('%d/%m/%Y'),
                       'soma': soma,
                       'user': user_u,
                       'printer': printer_u,
                       'host': host_u,
                       'base_dir': BASE_DIR,
                    })
    html = template.render(context)

    #Verificar se o sistema é windows
    if platform.system() == 'Windows':
        path_wkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    else:
        path_wkthmltopdf = '/usr/bin/wkhtmltopdf'

    config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
    options = {
        'encoding': 'utf-8',
        'footer-left': 'IFTO - Campus de Paraiso do Tocantins [date]',
        'footer-right': 'Pag. [page] de [topage]',
    }
    
    # Use False instead of output path to save pdf to a variable
    pdf = pdfkit.from_string(html, False, configuration=config, options=options)
    response = HttpResponse(pdf, content_type='application/pdf')

    return response
    #pdf = pisa.pisaDocument(StringIO.StringIO(html.encode('utf-8')), dest=result)
    #if not pdf.err: 
    #    return HttpResponse(result.getvalue(), content_type='application/pdf')
    #else:
    #    return HttpResponse('Errors')


def ajuda(request, topc):
    tutos = tutoriais.objects.all()
    lasttutos = tutoriais.objects.all().order_by('-id')[:3]
    if topc == '**topc**': # Se for a url padrão, rederiza a página inicial
        # Finalizando renderização da página
        return render(request, 'ajuda.html', {
                                     'title': 'Ajuda',
                                     'tutos': tutos,
                                     'itemselec': 'AJUDA',
                                     'last': lasttutos,
                                 })
    else:
        # Pega o post pelo id
        try:
            post = tutoriais.objects.get(id=topc)
        except:
            post = ''
            messages.error(request, 'O tutorial informado não existe, você pode criar um novo tutorial')
        # Finalizando renderização da página
        return render(request, 'ajuda.html', {
                                     'title': 'Ajuda',
                                     'tutos': tutos,
                                     'itemselec': 'AJUDA',
                                     'last': lasttutos,
                                     'post': post,
                                 })


def login(request):
    # Preparando o Menu
    request.session['menu'] = ['HOME']
    request.session['url'] = ['jasmine/login/']
    request.session['img'] = ['home24.png']
    
    dominio = None
    try:
        conf = config.objects.get(id=1)
        dominio = conf.dominio
    except:
        dominio = None
        
    if dominio: # Dominio existe no banco de dados
        # Se vier algo pelo post significa que houve requisição
        if request.method == 'POST':
            # cria uma instancia do formulario com os dados vindos do request POST:
            form = LoginForm(request, data=request.POST)
            # Checa se os dados são válidos:
            if form.is_valid():
                # Chama a página novamente
                return render(request, 'login.html', {'form': form, 'err': ''})
        else:# se não veio nada no post cria uma instancia vazia
            form = LoginForm(request)

        return render(request, 'login.html', {
                             'title': 'Home',
                             'form': form,
                             'itemselec': 'HOME',
                             })
    else:# Dominio não existe no banco de dados
        # Se vier algo pelo post significa que houve requisição
        if request.method == 'POST':
            # cria uma instancia do formulario de preenchimento dos dados do AD com os dados vindos do request POST:
            form = AdForm(request, data=request.POST)
            # Checa se os dados são válidos:
            if form.is_valid():
                # Cria uma instancia vazia do formulário de Login
                form = LoginForm(request)
                # Chama a página novamente
                return render(request, 'login.html', {'form': form, 'err': ''})
            else:
                print('formulario não é válido - Fazer algo aqui posteriormente')
        else:# se não veio nada no post cria uma instancia vazia
            form = AdForm(request)
        return render(request, 'configAdInit.html', {
                             'title': 'Home',
                             'form': form,
                             'itemselec': 'HOME',
                             })


def logout(request):
    try:
        del request.session['nome']
        del request.session['userl']
        del request.session['menu']
        del request.session['url']
    except KeyError:
        print(sys.exc_info())
    return render(request, 'index.html')