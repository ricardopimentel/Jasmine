import sys
from django.contrib import messages
from django.db import connection
from django.shortcuts import render, resolve_url as r, redirect
from django.template import Context
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt
import os
import platform
import datetime
from django.http.response import HttpResponse
import pdfkit

@csrf_exempt
def relatorios(request, user_u, printer_u, host_u):
    # preparação dos parametros iniciais
    data_final = datetime.datetime.today()
    data_inicial = datetime.datetime.fromordinal(data_final.toordinal() - 30)
    titulo = "Impressões dos Ultimos 30 dias"
    user_U = user_u
    printer_U = printer_u
    host_U = host_u
    err = ''

    # Verificar dados salvos na sessão
    try:
        # Se tiver data salva na sessão
        if (request.session['data_inicial']):
            data_inicial = request.session['data_inicial']  # Pega data da sessão
            titulo = 'Impressões no periodo de ' + datetime.datetime.strptime(str(data_inicial), '%Y-%m-%d').strftime(
                '%d/%m/%Y')  # atualiza titulo
        if (request.session['data_final']):
            data_final = request.session['data_final']  # Pega data da sessão
            titulo = titulo + ' a ' + datetime.datetime.strptime(str(data_final), '%Y-%m-%d').strftime(
                '%d/%m/%Y')  # atualiza titulo
        if (request.session['user']):
            user_u = request.session['user']  # Pega usuário da sessão
        if (request.session['printer']):
            printer_u = request.session['printer']  # Pega impressora da sessão
        if (request.session['host']):
            host_u = request.session['host']  # Pega host da sessão
    except:
        pass

    # Parametros por URL
    # substituir espaços na url por vazio
    if (user_U == ' '):
        user_u = ''
        request.session['user'] = user_u
    elif (not user_U == 'user'):
        request.session['user'] = user_U
        user_u = user_U
    if (printer_U == ' '):
        printer_u = ''
        request.session['printer'] = printer_u
    elif (not printer_U == 'printer'):
        request.session['printer'] = printer_U
        printer_u = printer_U
    if (host_U == ' '):
        host_u = ''
        request.session['host'] = host_u
    elif (not host_U == 'host'):
        request.session['host'] = host_U
        host_u = host_U

    # verificar se URL é http://localhost:8000/relatorio/*user*/*printer*/*host*/ essa url é o inicio padrão da página relatório
    if (user_U == '*user*' and printer_U == '*printer*' and host_U == '*host*'):
        titulo = 'Relatório de Impresões'

    # Parametros pelo método POST
    # Verificar se veio algum parametro pelo post
    if (request.POST):  # caso tenha vindo
        # verifica se veio usuário pelo post
        if (request.POST['user-r']):
            user_u = request.POST['user-r']
            if (user_u == ' '):
                user_u = ''
            # Salvar a user na sessão
            request.session['user'] = user_u
        # verifica se veio impressora pelo post
        if (request.POST['printer-r']):
            printer_u = request.POST['printer-r']
            if (printer_u == ' '):
                printer_u = ''
            # Salvar a printer na sessão
            request.session['printer'] = printer_u
        # verifica se veio host pelo post
        if (request.POST['host-r']):
            host_u = request.POST['host-r']
            if (host_u == ' '):
                host_u = ''
            # Salvar a host na sessão
            request.session['host'] = host_u
        # verifica se veio data inicial pelo post
        if (request.POST['data-inicial']):
            data_inicial = request.POST['data-inicial']
            # Salvar a data inicial na sessão
            request.session['data_inicial'] = data_inicial
            titulo = 'Impressões no período de ' + datetime.datetime.strptime(str(data_inicial), '%Y-%m-%d').strftime(
                '%d/%m/%Y')  # atualiza titulo
        # verifica se veio data final pelo post
        if (request.POST['data-final']):
            data_final = request.POST['data-final']
            # Salvar a data final na sessão
            request.session['data_final'] = data_final
            titulo = titulo + ' a ' + datetime.datetime.strptime(str(data_final), '%Y-%m-%d').strftime(
                '%d/%m/%Y')  # atualiza titulo
        # Verifica se há erros no formulario
        if (data_inicial > data_final):
            err = "Erro no intervalo da data"
            titulo = 'Relótorio de Impressões'

    # preparando consultas ao banco de dados
    cursor = connection.cursor()
    cursor.execute("SELECT user FROM core_jobs_log where user != '' GROUP BY user")
    top_users = cursor.fetchall()
    cursor.execute("SELECT printer FROM core_jobs_log where printer != '' GROUP BY printer")
    top_printers = cursor.fetchall()
    cursor.execute("SELECT host FROM core_jobs_log where host != '' GROUP BY host")
    top_hosts = cursor.fetchall()
    cursor.execute(
        "SELECT date, user, printer, host, title, pages FROM `core_jobs_log` WHERE user like '%" + user_u + "%' and printer like '%" + printer_u + "%' and host like '%" + host_u + "%' and (date BETWEEN '" + str(
            data_inicial) + " 00:00:00' and '" + str(data_final) + " 23:59:59' )")
    resultado = cursor.fetchall()
    cursor.execute(
        "SELECT SUM(pages) as total FROM `core_jobs_log` WHERE user like '%" + user_u + "%' and printer like '%" + printer_u + "%' and host like '%" + host_u + "%' and (date BETWEEN '" + str(
            data_inicial) + " 00:00:00' and '" + str(data_final) + " 23:59:59' )")
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

    # preparação dos parametros iniciais
    data_final = datetime.datetime.today()
    data_inicial = datetime.datetime.fromordinal(data_final.toordinal() - 30)
    user_u = ''
    printer_u = ''
    host_u = ''

    # Verificar dados salvos na sessão
    try:
        # Se tiver data salva na sessão
        if (request.session['data_inicial']):
            data_inicial = request.session['data_inicial']  # Pega data da sessão
            titulo = 'Impressões no periodo de ' + datetime.datetime.strptime(str(data_inicial), '%Y-%m-%d').strftime(
                '%d/%m/%Y')  # atualiza titulo
        if (request.session['data_final']):
            data_final = request.session['data_final']  # Pega data da sessão
            titulo = titulo + ' a ' + datetime.datetime.strptime(str(data_final), '%Y-%m-%d').strftime(
                '%d/%m/%Y')  # atualiza titulo
        if (request.session['user']):
            user_u = request.session['user']  # Pega usuário da sessão
        if (request.session['printer']):
            printer_u = request.session['printer']  # Pega impressora da sessão
        if (request.session['host']):
            host_u = request.session['host']  # Pega host da sessão
    except:
        pass

    cursor = connection.cursor()
    cursor.execute(
        "SELECT date, user, printer, host, title, pages FROM `core_jobs_log` WHERE user like '%" + user_u + "%' and printer like '%" + printer_u + "%' and host like '%" + host_u + "%' and (date BETWEEN '" + str(
            data_inicial) + " 00:00:00' and '" + str(data_final) + " 23:59:59' )")
    resultado = cursor.fetchall()
    cursor.execute(
        "SELECT SUM(pages) as total FROM `core_jobs_log` WHERE user like '%" + user_u + "%' and printer like '%" + printer_u + "%' and host like '%" + host_u + "%' and (date BETWEEN '" + str(
            data_inicial) + " 00:00:00' and '" + str(data_final) + " 23:59:59' )")
    soma = cursor.fetchall()
    template = get_template("relat2print.html")

    context = Context({
        'title': 'Relatório PDF',
        'pagesize': 'A4',
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

    # Verificar se o sistema é windows
    if platform.system() == 'Windows':
        path_wkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    else:
        path_wkthmltopdf = '/app/storage/wkhtmltopdf/wkhtmltopdf'

    try:
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
    except OSError:
        messages.error(request, 'wkhtmltopdf não está instalado, instale e tente novamente'+str(sys.exc_info()))
        return redirect(r('home', user_u='30', printer_u='30', host_u='30'))
    except:
        messages.error(request, sys.exc_info())
        return redirect(r('home', user_u='30', printer_u='30', host_u='30'))
