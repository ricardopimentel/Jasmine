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
from Jasmine.impressoes.forms import LoginForm, DigiForm, AdForm, CriarTutoForm
from Jasmine.impressoes.models import config, tutoriais, logs
import pdfkit
import shutil
import pypdfocr.pypdfocr as OCR

# Create your views here.
def home(request):
    cursor = connection.cursor()
    cursor.execute("SELECT user, SUM(pages) as total FROM impressoes_jobs_log GROUP BY user HAVING total >= 0 ORDER BY total DESC LIMIT 5")
    top_users = cursor.fetchall()
    cursor.execute("SELECT printer, SUM(pages) as total FROM impressoes_jobs_log GROUP BY printer HAVING total >= 0 ORDER BY total DESC LIMIT 5")
    top_printers = cursor.fetchall()
    cursor.execute("SELECT host, SUM(pages) as total FROM impressoes_jobs_log GROUP BY host HAVING total >= 0 ORDER BY total DESC LIMIT 5")
    top_hosts = cursor.fetchall()
    
    # Preparando cores dos gráficos
    cores_primarias = ['#F7464A', '#46BFBD', '#FDB45C', '#512DA8', '#C2185B']
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
    cursor.execute("SELECT user FROM impressoes_jobs_log where user != '' GROUP BY user")
    top_users = cursor.fetchall()
    cursor.execute("SELECT printer FROM impressoes_jobs_log where printer != '' GROUP BY printer")
    top_printers = cursor.fetchall()
    cursor.execute("SELECT host FROM impressoes_jobs_log where host != '' GROUP BY host")
    top_hosts = cursor.fetchall()
    cursor.execute("SELECT date, user, printer, host, title, pages FROM `impressoes_jobs_log` WHERE user like '%"+user_u+"%' and printer like '%"+printer_u+"%' and host like '%"+host_u+"%' and (date BETWEEN '"+str(data_inicial)+" 00:00:00' and '"+str(data_final)+" 23:59:59' )")
    resultado = cursor.fetchall()
    cursor.execute("SELECT SUM(pages) as total FROM `impressoes_jobs_log` WHERE user like '%"+user_u+"%' and printer like '%"+printer_u+"%' and host like '%"+host_u+"%' and (date BETWEEN '"+str(data_inicial)+" 00:00:00' and '"+str(data_final)+" 23:59:59' )")
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
    cursor.execute("SELECT date, user, printer, host, title, pages FROM `impressoes_jobs_log` WHERE user like '%"+user_u+"%' and printer like '%"+printer_u+"%' and host like '%"+host_u+"%' and (date BETWEEN '"+str(data_inicial)+" 00:00:00' and '"+str(data_final)+" 23:59:59' )")
    resultado = cursor.fetchall()
    cursor.execute("SELECT SUM(pages) as total FROM `impressoes_jobs_log` WHERE user like '%"+user_u+"%' and printer like '%"+printer_u+"%' and host like '%"+host_u+"%' and (date BETWEEN '"+str(data_inicial)+" 00:00:00' and '"+str(data_final)+" 23:59:59' )")
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


def get_scan(request, printer, arquivo, action): # Se for URL padrão (mostrar pastas)
    # Pega a pasta raiz do banco de dados
    raiz = (config.objects.get(id=1)).pasta_dig
    #Verificar se a URL é a URL padrão ( Mostrar a raiz)
    if(printer == '*printer*' and arquivo == '*file*' and action == '*action*'):
        nomes_folders = []
        try:
            # Seta diretório
            os.chdir(raiz)
            nomes_folders = glob.glob('*/')
            nomes_folders = sorted(nomes_folders) # Ordenando por nome
        except:
            messages.error(request, str(sys.exc_info()[1]))
        return render(request, 'escaneados.html', {
             'title': 'Documentos Escaneados',
             'nomes_folders': nomes_folders,
             })
    else:# Se vieram comandos pela url mostrar arquivos
        # pegar endereço IP do cliente
        #Ip = GetIp().get_client_ip(request)        
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            Ip = x_forwarded_for.split(',')[-1].strip()
        else:
            Ip = request.META.get('REMOTE_ADDR')
        
        os.chdir(raiz+ '/'+printer)
        nomes_arquivos_jpg = glob.glob('*jpg') # Arquivos jpg
        nomes_arquivos_jpg.sort(key=os.path.getmtime, reverse=True) # Ordenando por data reversa
        nomes_arquivos_pdf = glob.glob('*pdf') # Arquivos pdf
        nomes_arquivos_pdf.sort(key=os.path.getmtime, reverse=True) # Ordenando por data reversa                                                                                                                                                                                                                                                                                                                                                                                                                                                        
        #Verificar se há arquivos sendo construidos
        nomes_arquivos_load = glob.glob('*')
        load = []
        
        for fili in nomes_arquivos_load:
            if(not(fili[-3::] == 'pdf')and not(fili[-3::] == 'png') and not(fili[-3::] == 'jpg')and not(fili[-3::] == 'tif')and not(fili[-3::] == 'wps')and not(fili[-2::] == 'db')):
                load.append(fili)
        #concatenando arquivos
        nomes_arquivos = load + nomes_arquivos_pdf + nomes_arquivos_jpg
        lista = []
        for fff in nomes_arquivos:
            lista.append(fff)#.decode("latin-1"))<-No python3 isto não funciona
        nomes_arquivos = lista
        # Acentos não funcionam fazer algo para solucionar isso
        
        #Abrindo Arquivo
        url = raiz+ '/'+ printer+ '/'+ arquivo
        if(not (arquivo == '*file*')):
            with open(url, 'rb') as pdf:
                if(action == 'dow'): # Forçar Download
                    try:
                        # Tenta ler arquivo
                        response = HttpResponse(pdf.read(), content_type = 'application/force-download')
                        response['Content-Disposition'] = 'inline;filename='+arquivo
                        pdf.closed
                        # Salva log
                        log = logs(data = datetime.datetime.now(), action = 'Down', item = 'Digitalizacoes/%s/%s' % (str(printer), arquivo), resumo = 'Digitalizacoes/%s/%s foi baixado por %s' % (str(printer), arquivo, str(request.session['userl'])), user = request.session['userl'], ip = Ip)
                        log.save()
                        
                        return response
                    except:
                        pdf.closed
                        return render(request, 'escaneados.html', {
                                 'title': 'Documentos Escaneados',
                                 'nomes_arquivos': nomes_arquivos,
                                 'msg': sys.exc_info(),
                                 'printer': printer,
                                 })
                elif(action == 'ope'): # Abrir Arquivo
                    try:
                        # Tenta ler arquivo
                        if (arquivo[-3::] == 'pdf'):
                            response = HttpResponse(pdf.read(), content_type = 'application/pdf')
                        elif(arquivo[-3::] == 'jpg'):
                            response = HttpResponse(pdf.read(), content_type = 'open')
                        response['Content-Disposition'] = 'inline;filename='+arquivo
                        pdf.closed
                        # Salva log
                        log = logs(data = datetime.datetime.now(), action = 'Vis', item = 'Digitalizacoes/%s/%s' % (str(printer), arquivo), resumo = 'Digitalizacoes/%s/%s foi visualizado por %s' % (str(printer), arquivo, str(request.session['userl'])), user = request.session['userl'], ip = Ip)
                        log.save()
                        
                        return response
                    except:
                        return render(request, 'escaneados.html', {
                                 'title': 'Documentos Escaneados',
                                 'nomes_arquivos': nomes_arquivos,
                                 'msg': sys.exc_info(),
                                 'printer': printer,
                                 })
                elif(action == 'del'): # Excluir arquivo
                    try:
                        # Remover arquivo
                        pdf.closed
                        os.remove(url)
                        nomes_arquivos.remove(arquivo)
                        
                        # Salva log
                        log = logs(data = datetime.datetime.now(), action = 'Exc', item = 'Digitalizacoes/%s/%s' % (str(printer), arquivo), resumo = 'Digitalizacoes/%s/%s foi excluido por %s' % (str(printer), arquivo, str(request.session['userl'])), user = request.session['userl'], ip = Ip)
                        log.save()
                        
                        #Recarrega página com mensagem de suesso
                        return render(request, 'escaneados.html', {
                                 'title': 'Documentos Escaneados',
                                 'nomes_arquivos': nomes_arquivos,
                                 'msg': 'Excluído com sucesso!',
                                 'image_snack': "excluir.png",
                                 'printer': printer,
                                 })
                    except WindowsError:
                        pdf.closed

                        messages.error(request, str(sys.exc_info()[1]))
                            
                        # Salva log erro windows
                        log = logs(data = datetime.datetime.now(), action = 'Err', item = 'Digitalizacoes/%s/%s' % (str(printer), arquivo), resumo = 'Arquivo não foi removido, err: %s' % (str(sys.exc_info()[1])), user = request.session['userl'], ip = Ip)
                        log.save()
                        
                        #return redirect('/jasmine/escaneados/'+printer+'/*file*/*action*/', kwargs={'action': err})
                        return render(request, 'escaneados.html', {
                                 'title': 'Documentos Escaneados',
                                 'nomes_arquivos': nomes_arquivos,
                                 'printer': printer,
                        })
                    except:
                        pdf.closed

                        messages.error(request, str(sys.exc_info()[1]))

                        #return redirect('/jasmine/escaneados/'+printer+'/*file*/*action*/', kwargs={'action': err})
                        return render(request, 'escaneados.html', {
                                 'title': 'Documentos Escaneados',
                                 'nomes_arquivos': nomes_arquivos,
                                 'printer': printer,
                                 })

        return render(request, 'escaneados.html', {
             'title': 'Documentos Escaneados',
             'nomes_arquivos': nomes_arquivos,
             'printer': printer,
             'itemselec': 'DIGITALIZAÇÕES',
             })


def pasta_digi(request):
    try:
        model = (config.objects.get(id=1))
    except:
        model = ''
        messages.error(request, sys.exc_info())
    # Vefirica se veio aolgo pelo POST
    if request.method == 'POST':
        # cria uma instancia do formulário e passa a ele os dados do post:
        form = DigiForm(request.POST)
        # verifica se os dados são válidos:
        if form.is_valid():
            # pegar endereço IP do cliente
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                Ip = x_forwarded_for.split(',')[-1].strip()
            else:
                Ip = request.META.get('REMOTE_ADDR')
            
            # Salva endereço anterior em variavel para passar ao log
            pasta_old = model.pasta_dig
            # Altera endereço da pasta no banco de dados
            model.pasta_dig = request.POST['pasta_dig']
            # Salva endereço pasta nova em variavel para passar ao log
            pasta_new = request.POST['pasta_dig']
            # comit
            model.save()
            
            # salvar log
            resumo = 'Administracao/Config Digitalizacoes/ foi alterado por: '+ request.session['userl']+ '\nO campo Endereco pasta digitalizacoes tinha o valor: \n    '+pasta_old+'\nFoi Alterado para: \n    '+pasta_new+'\n'
            log = logs(
                data = datetime.datetime.now(),
                action = 'Alt', 
                item = 'Administração/Config AD', 
                resumo = resumo,
                user = request.session['userl'], 
                ip = Ip)
            log.save()
            
            messages.success(request, 'Configurações salvas com sucesso!')
        return render(request, 'pasta_digi.html', {
            'form': form,
            'itemselec': 'ADMINISTRAÇÃO',
        })
    # Se não veio algo do POST cria instancia vazia dos formulários com os dados vindos do banco de dados
    else:
        form = DigiForm(initial={'pasta_dig': model.pasta_dig})
        return render(request, 'pasta_digi.html', {
            'form': form,
            'itemselec': 'ADMINISTRAÇÃO',
        })


def dados_ad(request):
    try:
        model = (config.objects.get(id=1))
    except:
        model = ''
        messages.error(request, sys.exc_info())
    # Vefirica se veio aolgo pelo POST
    if request.method == 'POST':
        # cria uma instancia do formulario de preenchimento dos dados do AD com os dados vindos do request POST:
        form = AdForm(request, data=request.POST)
        # Checa se os dados são válidos:
        if form.is_valid():
            # Chama a página novamente
            messages.success(request, 'Configurações salvas com sucesso!')
        return render(request, 'dados_ad.html', {'form': form})
    # Se não veio algo do POST cria instancia vazia dos formulários com os dados vindos do banco de dados
    else:
        form = AdForm(request, initial={'dominio': model.dominio, 'endservidor': model.endservidor, 'gadmin': model.gadmin, 'ou': model.ou})
        return render(request, 'dados_ad.html', {
            'form': form,
            'itemselec': 'ADMINISTRAÇÃO',
        })


def add_tutorial(request):
    # Vefirica se veio aolgo pelo POST
    if request.method == 'POST':
        # cria uma instancia do formulario de preenchimento dos dados do AD com os dados vindos do request POST:
        form = CriarTutoForm(request, data=request.POST)
        # Checa se os dados são válidos:
        if form.is_valid():
            # Salva
            form.save()
            # Chama a página novamente
            messages.success(request, 'Tutorial salvo com sucesso!')
            # Cria uma instancia Vazia do form
            form = CriarTutoForm(request, initial={'data': datetime.datetime.today(), 'user': request.session['nome']})
        return render(request, 'criar_tutorial.html', {'form': form})
    # Se não veio algo do POST cria instancia vazia dos formulários com os dados vindos do banco de dados
    else:
        # Cria uma instancia Vazia do form
        form = CriarTutoForm(request, initial={'data': datetime.datetime.today(), 'user': request.session['nome']})
        return render(request, 'criar_tutorial.html', {
            'form': form,
            'itemselec': 'ADMINISTRAÇÃO',
        })


def admin(request):
    msg = ''
    # Vefirica se veio aolgo pelo POST
    # Cria uma instancia Vazia do form
    return render(request, 'admin.html', {
        'itemselec': 'ADMINISTRAÇÃO',
        'msg': msg,
    })


def view_tutorial(request, Action, Id):
    # pegar endereço IP do cliente
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        Ip = x_forwarded_for.split(',')[-1].strip()
    else:
        Ip = request.META.get('REMOTE_ADDR')
    
    # Vefirica se veio algo pelo POST
    if request.method == 'POST':
        # cria uma instancia do formulario de preenchimento com os dados vindos do request POST:
        form = CriarTutoForm(request, data=request.POST)
        # Checa se os dados são válidos:
        if form.is_valid():
            # Inicializa variaveis com os dados digitados no formulario
            try:
                # Gera instancia do item a ser utilizado
                model = tutoriais.objects.get(id = Id)
                
                # Salva itens antigos em variaves para gerar log
                titulo_old = model.titulo
                texto_old = model.texto
                
                # Salva os itens novos (digitados pelo usuário)
                model.titulo = request.POST['titulo']
                model.texto = request.POST['texto']
                titulo_new = request.POST['titulo']
                texto_new = request.POST['texto']
                model.save() # Salva no bd
                
                # Resumo do que foi feito
                resumo = 'Um tutorial foi alterado por: '+ request.session['userl']
                resumo_item = ''
                if not titulo_old == titulo_new:
                    resumo_item += '\nO Titulo foi alterado de:\n    '+ titulo_old+ '\npara:\n    '+titulo_new
                if not texto_old == texto_new:
                    resumo_item += '\nO Texto foi alterado de:\n'+ texto_old+ '\npara:\n'+texto_new
                resumo += resumo_item
                
                # Salvar log
                log = logs(
                    data = datetime.datetime.now(),
                    action = 'Alt', 
                    item = 'Administração/Tutorial',
                    resumo = resumo,
                    user = request.session['userl'],
                    ip = Ip)
                log.save()
            except:
                raise sys.exc_info()[1]
                # Salvar log
                log = logs(
                    data = datetime.datetime.now(),
                    action = 'Err', 
                    item = 'Administração/Tutorial',
                    resumo = sys.exc_info(),
                    user = request.session['userl'],
                    ip = Ip)
                log.save()
            # Chama a página novamente
            messages.success(request, 'Tutorial salvo com sucesso!')
            # Cria uma instancia Vazia do form
            # Gera form de criar tutorial
            form = CriarTutoForm(request, initial={'data': datetime.datetime.today(), 'user': request.session['nome']})
        # Depois de salvar a edição, redireciona para o criar tutorial
        return render_to_response('criar_tutorial.html', {'form': form}, context_instance=RequestContext(request))
    # Se não veio algo do POST cria instancia vazia dos formulários com os dados vindos do banco de dados
    else:
        # Verifica no banco de dados se o id passado equivale a algum tutorial salvo
        bd = []
        try: #tenta conexao e buscar id do tutorial
            bd = tutoriais.objects.get(id = Id)
        except:
            # Salvar log
            log = logs(
                data = datetime.datetime.now(),
                action = 'Err', 
                item = 'Administração/Tutorial',
                resumo = sys.exc_info(),
                user = request.session['userl'],
                ip = Ip)
            log.save()
        if bd: # se houver retorno no bd
            if Action == 'delete':
                # Guarda informações antes de excluir
                titulo = bd.titulo
                texto = bd.texto
                
                # Apaga tutorial com o id informado
                bd.delete()
                
                # Resumo do que foi feito
                resumo = 'Um tutorial foi excluido por: '+ request.session['userl']
                resumo += '\nO Titulo era:\n    '+ titulo+ '\nO Texto era:\n    '+texto
                
                # Salvar log
                log = logs(
                    data = datetime.datetime.now(),
                    action = 'Exc', 
                    item = 'Administração/Tutorial',
                    resumo = resumo,
                    user = request.session['userl'],
                    ip = Ip)
                log.save()
                
                # Renderizar a pagina principal de ajuda, com msg de excusão bem sucedida ou não
                tutos = tutoriais.objects.all()
                lasttutos = tutoriais.objects.all().order_by('-id')[:3]
                messages.success(request, "Tutorial Excluído com Sucesso!")
                return render(request, 'ajuda.html', {
                         'title': 'Ajuda',
                         'tutos': tutos,
                         'last': lasttutos,
                         'itemselec': 'AJUDA',
                     })
            else:
                # Cria uma instancia preenchida do editar tutorial form
                form = CriarTutoForm(request, initial={'data': bd.data, 'titulo': bd.titulo, 'texto': bd.texto, 'user': bd.user})
                return render(request, 'editar_tutorial.html', {
                    'form': form,
                    'itemselec': 'ADMINISTRAÇÃO',
                    'id': Id,
                })
        else:
            # Cria uma instancia Vazia do form para criar um tutorial novo
            form = CriarTutoForm(request, initial={'data': datetime.datetime.today(), 'user': request.session['nome']})
            messages.error(request, "Tutorial desejado não existe, você pode criar um novo!")
            return render(request, 'criar_tutorial.html', {
                'form': form,
                'itemselec': 'ADMINISTRAÇÃO',
                'id': Id,
            })


@csrf_exempt
def viewlogs(request, user_u, action_u, host_u):
    #preparação dos parametros iniciais
    data_final = datetime.datetime.today()
    data_inicial = datetime.datetime.fromordinal(data_final.toordinal()-30)
    titulo = "Registros de Logs dos ultimos 30 dias"
    user_U = user_u
    action_U = action_u
    host_U = host_u
    err = ''
    
    #Verificar dados salvos na sessão
    try:
        #Se tiver data salva na sessão
        if(request.session['data_iniciall']):
            data_inicial = request.session['data_iniciall'] # Pega data da sessão
            titulo = 'Registros no periodo de '+ datetime.datetime.strptime(str(data_inicial), '%Y-%m-%d').strftime('%d/%m/%Y') #atualiza titulo
        if(request.session['data_finall']):
            data_final = request.session['data_finall'] # Pega data da sessão
            titulo = titulo+ ' a '+ datetime.datetime.strptime(str(data_final), '%Y-%m-%d').strftime('%d/%m/%Y') #atualiza titulo
        if(request.session['user']):
            user_u = request.session['user'] # Pega usuário da sessão
        if(request.session['action']):
            action_u = request.session['action'] # Pega impressora da sessão
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
    if(action_U == ' '):
        action_u = ''
        request.session['action'] = action_u
    elif(not action_U == 'action'):
        request.session['action'] = action_U
        action_u = action_U
    if(host_U == ' '):
        host_u = ''
        request.session['host'] = host_u
    elif(not host_U == 'host'):
        request.session['host'] = host_U
        host_u = host_U
        
    #verificar se URL é http://localhost:8000/relatorio/*user*/*action*/*host*/ essa url é o inicio padrão da página relatório
    if(user_U == '*user*' and action_U == '*action*' and host_U == '*host*'):
        titulo = 'Registros de Logs do Sistema'
    
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
        #verifica se veio ação pelo post
        if(request.POST['action-r']):
            action_u = request.POST['action-r']
            if(action_u == ' '):
                action_u = ''
            # Salvar a printer na sessão
            request.session['action'] = action_u
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
            request.session['data_iniciall'] = data_inicial
            titulo = 'Registros de Logs no periodo de '+ datetime.datetime.strptime(str(data_inicial), '%Y-%m-%d').strftime('%d/%m/%Y') #atualiza titulo
        #verifica se veio data final pelo post
        if(request.POST['data-final']):
            data_final = request.POST['data-final']
            # Salvar a data final na sessão
            request.session['data_finall'] = data_final
            titulo = titulo+ ' a '+ datetime.datetime.strptime(str(data_final), '%Y-%m-%d').strftime('%d/%m/%Y') #atualiza titulo
        #Verifica se há erros no formulario
        if(data_inicial > data_final):
            err = "Erro no intervalo da data"
            titulo = 'Registros de Logs do Sistema'
            
    #preparando consultas ao banco de dados
    cursor = connection.cursor()
    cursor.execute("SELECT user FROM impressoes_logs where user != '' GROUP BY user")
    top_users = cursor.fetchall()
    cursor.execute("SELECT action FROM impressoes_logs where action != '' GROUP BY action")
    top_actions = cursor.fetchall()
    cursor.execute("SELECT ip FROM impressoes_logs where ip != '' GROUP BY ip")
    top_hosts = cursor.fetchall()
    cursor.execute("SELECT data, action, user, ip, item, resumo FROM `impressoes_logs` WHERE user like '%"+user_u+"%' and action like '%"+action_u+"%' and ip like '%"+host_u+"%' and (data BETWEEN '"+str(data_inicial)+" 00:00:00' and '"+str(data_final)+" 23:59:59' )")
    resultado = cursor.fetchall()
    # Finalizando renderização da página
    return render(request, 'viewlogs.html', {
         'title': 'Relatório',
         'top_users': top_users,
         'top_actions': top_actions,
         'top_hosts': top_hosts,
         'resultado': resultado,
         'titulo_relat': titulo,
         'inicial': str(data_inicial),
         'final': str(data_final),
         'user': user_u,
         'action': action_u,
         'host': host_u,
         'err': err,
         'itemselec': 'RELATÓRIOS',
        })


def ocr(request, printer, arquivo):
    msg = ''
    # Tenta conexão com bd
    try:
        model = (config.objects.get(id=1))  # pegando configurações
    except:
        model = ''
        msg = sys.exc_info()
    try:
        # passa o local do arquivo que será convertido pegando a raiz do banco de dados e concatenando com a impressora e nome do arquivo
        arquivo_original = os.path.join(model.pasta_dig + '/' + printer, arquivo)
        arquivo_destino = os.path.join(model.pasta_dig + '/temp/' + arquivo)
        pasta_temp = os.path.join(model.pasta_dig + '/temp/')

        print("copiando arquivo para pasta temporária")
        shutil.copy2(arquivo_original, pasta_temp)

        # Iniciando classe OCR
        ocr = OCR.PyPDFOCR()

        # adiciona um sufixo ao nome do arquivo
        out_filename = arquivo_destino.replace(".pdf", "_ocr.pdf")
        # caso já exista um arquivo com o nome do que será jerado, ele é excluido antes da conversão
        if os.path.exists(out_filename):
            os.remove(out_filename)  # removendo arquivo

        print("Current directory: %s" % os.getcwd())

        opts = [str(arquivo_destino), '-l por']# .encode('utf-8')] <- #Python 3 não permite
        # convertendo
        ocr.go(opts)
        msg = "Arquivo '" + arquivo.replace(".pdf", "_ocr.pdf") + "' gerado com sucesso!"

    except:
        msg = 'Erro ao converter arquivo/n' + str(sys.exc_info())
        raise

    return render(request, 'escaneados.html', {
        'title': 'Documentos Escaneados',
        'redirect': msg,
        'printer': printer,
        'comprimir': 'comprimir',
        'arquivo': arquivo.replace(".pdf", "_ocr.pdf"),
    })


def compress(request, printer, arquivo):
    # Tenta conexão com bd
    try:
        model = (config.objects.get(id=1))  # pegando configurações
        pasta_original = os.path.join(model.pasta_dig + '/' + printer)
        pasta_temp = os.path.join(model.pasta_dig + '/temp/')
        output = pasta_temp + "compacto-"+arquivo
        path_arquivo = pasta_temp + arquivo
        msg = ''

        msg = os.system("gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/ebook -dNOPAUSE -dQUIET -dBATCH -sOutputFile=%s %s" % (output, path_arquivo))
        os.remove(path_arquivo)

        if msg:
            messages.error(request, "Erro ao compactar o arquivo")
        else:
            print("copiando arquivo criado para a pasta original")
            shutil.copy2(output, pasta_original)
            messages.success(request, 'Arquivo "compacto-' + arquivo + '" Gerado com sucesso')
    except:
        model = ''
        messages.error(request, sys.exc_info())

    return redirect('/jasmine/escaneados/'+ printer+ '/*file*/*action*/')