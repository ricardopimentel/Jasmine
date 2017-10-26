import os
import shutil
import threading

import pypdfocr.pypdfocr.pypdfocr as OCR
import sys
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, resolve_url as r, redirect
from Jasmine.core.models import config


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
        if os.path.isdir(raiz):
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
            err = 'Caminho das digitalizações cadastrado não foi encontrado'
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
    raiz = (config.objects.get(id=1)).pasta_dig

    t = threading.Thread(target=gerarpdf, args=(request, u_printer, u_filename, raiz), kwargs={})
    t.setDaemon(True)
    t.start()

    return render(request, 'digitalizacoes/digitalizacoes.html', {
        'title': 'Documentos Escaneados',
        'converter': 'converter',
        'printer': u_printer,
        'arquivo': u_filename,
        'raiz': raiz,
    })


def compress(request, u_printer, u_filename):
    raiz = (config.objects.get(id=1)).pasta_dig

    t = threading.Thread(target=comprimir, args=(request, u_printer, u_filename, raiz), kwargs={})
    t.setDaemon(True)
    t.start()

    return render(request, 'digitalizacoes/digitalizacoes.html', {
        'title': 'Documentos Escaneados',
        'comprimir': 'comprimir',
        'printer': u_printer,
        'arquivo': u_filename,
        'raiz': raiz,
    })


def gerarpdf(request, u_printer, u_filename, raiz):
    '''Extrai texto das imagem do pdf e as adiciona em uma camada trasparente sobre a imagem original'''

    try:
        # passa o local do arquivo que será convertido pegando a raiz do banco de dados e concatenando com a impressora e nome do arquivo
        arquivo_original = os.path.join(raiz + '/' + u_printer, u_filename)
        arquivo_destino = os.path.join(raiz + '/temp/' + u_filename)
        pasta_temp = os.path.join(raiz + '/temp/')

        # copiando arquivo para pasta temporária
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

        print('\nTerminado\n')
    except:
        messages.error(request, sys.exc_info())
        return redirect(r('digitalizacoes', u_printer=u_printer, u_filename='*file*', u_action='*action*'))


def verificarocr(request, u_printer, u_filename):
    raiz = (config.objects.get(id=1)).pasta_dig
    pasta_temp = os.path.join(raiz + '/temp/')
    arquivo = u_filename.replace(".pdf", "_ocr.pdf")
    path_arquivo = pasta_temp + arquivo

    if os.path.isfile(path_arquivo):
        return redirect(r('digitalizacoes_compress', u_printer=u_printer, u_filename=u_filename))
    else:
        return render(request, 'digitalizacoes/digitalizacoes.html', {
            'title': 'Documentos Escaneados',
            'converter': 'converter',
            'printer': u_printer,
            'arquivo': u_filename,
            'raiz': raiz,
        })


def verificarcompress(request, u_printer, u_filename):
    raiz = (config.objects.get(id=1)).pasta_dig
    arquivo = "compacto-"+ u_filename.replace(".pdf", "_ocr.pdf")
    path_arquivo = raiz+ '/'+ u_printer+ '/'+ arquivo

    if os.path.isfile(path_arquivo):
        return redirect(r('digitalizacoes', u_printer=u_printer, u_filename='*file*', u_action='*action*'))
    else:
        return render(request, 'digitalizacoes/digitalizacoes.html', {
            'title': 'Documentos Escaneados',
            'comprimir': 'comprimir',
            'printer': u_printer,
            'arquivo': u_filename,
            'raiz': raiz,
        })


def comprimir(request, u_printer, u_filename, raiz):
    u_filename = u_filename.replace(".pdf", "_ocr.pdf")
    pasta_original = os.path.join(raiz + '/' + u_printer)
    pasta_temp = os.path.join(raiz + '/temp/')
    output = pasta_temp + "compacto-" + u_filename
    path_arquivo = pasta_temp + u_filename
    msg = ''

    msg = os.system(
        "gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/ebook -dNOPAUSE -dQUIET -dBATCH -sOutputFile=%s %s" % (
        output, path_arquivo))

    if msg:
        messages.error(request, "Erro ao compactar o arquivo")
    else:
        # copiando arquivo criado para a pasta original
        shutil.copy2(output, pasta_original)
        messages.success(request, 'Arquivo "compacto-' + u_filename + '" Gerado com sucesso')

    os.remove(path_arquivo[0:-8] + '.pdf')
    os.remove(path_arquivo)
    os.remove(output)

    print('\nFinalizada a compressão\n')