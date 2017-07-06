import os
import shutil
import pypdfocr.pypdfocr as OCR
import sys
import glob

import datetime
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, resolve_url as r, redirect
from Jasmine.core.models import config, logs


def digitalizacoes(request, u_printer, u_filename, u_action):
    '''Faz o controle das digitalizações, exibe os arquivos digitalizados separados por pasta'''
    list_folders = []
    list_files = []
    if u_printer == '*printer*':
        u_printer = ''
    if u_filename == '*file*':
        u_filename = ''
    if u_action == '*action*':
        u_action = ''
    err = ''
    raiz = (config.objects.get(id=1)).pasta_dig

    if raiz:
        for root, dirs, files in os.walk(os.path.join(raiz, u_printer)):# faz varredura nos arquivos e diretórios da raiz
            if not u_printer:# URL padrão não vem printer especificada, mostrar lista de pastas
                dirs.sort(reverse=True)
                for dirName in dirs:
                    if not dirName == 'temp':
                        list_folders.append(dirName)
                break# Quebra para não executar recursividade
            else:# Se entrar aqui, está dentro de uma pasta, exibir arquivos
                files.sort(key=lambda x: os.path.getmtime(os.path.join(root, x)), reverse=True)# Ordenar por data reversa, ultimos na frente
                for fileName in files:
                    list_files.append(fileName)
                break# Quebra para não executar recursividade

        # Verificar tipo de ação a ser realizada com o arquivo
        if u_action:
            if u_action == 'ope':
                return abrir_arquivo(request, u_filename, u_printer, raiz)
            elif u_action == 'dow':
                return baixar_arquivo(request, u_filename, u_printer, raiz)
            elif u_action == 'del':
                remover_arquivo(request, u_filename, u_printer, raiz, list_files)
                return redirect(
                    r('digitalizacoes', u_printer=u_printer, u_filename='*file*', u_action='*action*'))
    else:
        err = 'Caminho das digitalizações não está cadastrado'

    return render(request, 'digitalizacoes/digitalizacoes.html', {
        'title': 'Documentos Escaneados',
        'list_folders': list_folders,
        'list_files': list_files,
        'printer': u_printer,
        'err': err,
    })


def abrir_arquivo(request, filename, printer, raiz):
    url = raiz + '/' + printer + '/' + filename
    try:
        with open(url, 'rb') as file:
            if (filename[-3::] == 'pdf'):
                response = HttpResponse(file.read(), content_type='application/pdf')
            elif (filename[-3::] == 'jpg'):
                response = HttpResponse(file.read(), content_type='open')
            response['Content-Disposition'] = 'inline;filename=' + filename
        file.close()
    except:
        messages.error(request, "Erro ao abrir o arquivo: " + str(sys.exc_info()[1]))
    return response


def baixar_arquivo(request, filename, printer, raiz):
    url = raiz + '/' + printer + '/' + filename
    try:
        with open(url, 'rb') as file:
            response = HttpResponse(file.read(), content_type='application/force-download')
            response['Content-Disposition'] = 'inline;filename=' + filename
        file.close()
    except:
        messages.error(request, "Erro ao baixar o arquivo: " + str(sys.exc_info()[1]))
    return response


def remover_arquivo(request, filename, printer, raiz, list_files):
    url = raiz + '/' + printer + '/' + filename
    try:
        os.remove(url)
        list_files.remove(filename)
        messages.success(request, 'Arquivo "'+ filename+ '" excluído com sucesso!')
    except:
        messages.error(request, "Erro ao excluir o arquivo: "+ str(sys.exc_info()[1]))


def ocr(request, u_printer, u_filename):
    '''Extrai texto das imagem do pdf e as adiciona em uma camada trasparente sobre a imagem original'''
    raiz = (config.objects.get(id=1)).pasta_dig
    if raiz:
        try:
            # passa o local do arquivo que será convertido pegando a raiz do banco de dados e concatenando com a impressora e nome do arquivo
            arquivo_original = os.path.join(raiz + '/' + u_printer, u_filename)
            arquivo_destino = os.path.join(raiz + '/temp/' + u_filename)
            pasta_temp = os.path.join(raiz + '/temp/')

            #copiando arquivo para pasta temporária
            shutil.copy2(arquivo_original, pasta_temp)

            # Iniciando classe OCR
            ocr = OCR.PyPDFOCR()

            # adiciona um sufixo ao nome do arquivo
            out_filename = arquivo_destino.replace(".pdf", "_ocr.pdf")

            # caso já exista um arquivo com o nome do que será gerado, ele é excluido antes da conversão
            if os.path.exists(out_filename):
                os.remove(out_filename)  # removendo arquivo

            opts = [str(arquivo_destino), '-l por']

            # convertendo
            ocr.go(opts)
            msg = "Arquivo '" + u_filename.replace(".pdf", "_ocr.pdf") + "' gerado com sucesso!"

        except:
            msg = 'Erro ao converter arquivo/n' + str(sys.exc_info())
            raise

    return render(request, 'digitalizacoes/digitalizacoes.html', {
        'title': 'Documentos Escaneados',
        'redirect': msg,
        'printer': u_printer,
        'comprimir': 'comprimir',
        'arquivo': u_filename.replace(".pdf", "_ocr.pdf"),
    })


def compress(request, u_printer, u_filename):
    try:
        raiz = (config.objects.get(id=1)).pasta_dig
        pasta_original = os.path.join(raiz + '/' + u_printer)
        pasta_temp = os.path.join(raiz + '/temp/')
        output = pasta_temp + "compacto-"+u_filename
        path_arquivo = pasta_temp + u_filename
        msg = ''

        msg = os.system("gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/ebook -dNOPAUSE -dQUIET -dBATCH -sOutputFile=%s %s" % (output, path_arquivo))
        os.remove(path_arquivo)

        if msg:
            messages.error(request, "Erro ao compactar o arquivo")
        else:
            # copiando arquivo criado para a pasta original
            shutil.copy2(output, pasta_original)
            messages.success(request, 'Arquivo "compacto-' + u_filename + '" Gerado com sucesso')
    except:
        model = ''
        messages.error(request, sys.exc_info())

    return redirect(r('digitalizacoes', u_printer=u_printer, u_filename='*file*', u_action='*action*'))
