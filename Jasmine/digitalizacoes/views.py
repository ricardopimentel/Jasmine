import os
import shutil
import pypdfocr.pypdfocr as OCR
import sys
import glob

import datetime
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from Jasmine.core.models import config, logs


def digitalizacoes(request, printer, arquivo, action):  # Se for URL padrão (mostrar pastas)
    err = ''
    # Pega a pasta raiz do banco de dados
    raiz = (config.objects.get(id=1)).pasta_dig
    # Verificar se a URL é a URL padrão ( Mostrar a raiz)
    if (printer == '*printer*' and arquivo == '*file*' and action == '*action*'):
        nomes_folders = []
        try:
            # Seta diretório
            os.chdir(raiz)
            nomes_folders = glob.glob('*/')
            nomes_folders = sorted(nomes_folders)  # Ordenando por nome
        except:
            messages.error(request, str(sys.exc_info()[1]))
            err = str(sys.exc_info()[1])
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.chdir(BASE_DIR)
        return render(request, 'digitalizacoes/digitalizacoes.html', {
            'title': 'Documentos Escaneados',
            'nomes_folders': nomes_folders,
            'err': err,
        })
    else:  # Se vieram comandos pela url mostrar arquivos
        # pegar endereço IP do cliente
        # Ip = GetIp().get_client_ip(request)
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            Ip = x_forwarded_for.split(',')[-1].strip()
        else:
            Ip = request.META.get('REMOTE_ADDR')

        os.chdir(raiz + '/' + printer)
        nomes_arquivos_jpg = glob.glob('*jpg')  # Arquivos jpg
        nomes_arquivos_jpg.sort(key=os.path.getmtime, reverse=True)  # Ordenando por data reversa
        nomes_arquivos_pdf = glob.glob('*pdf')  # Arquivos pdf
        nomes_arquivos_pdf.sort(key=os.path.getmtime,
                                reverse=True)  # Ordenando por data reversa
        # Verificar se há arquivos sendo construidos
        nomes_arquivos_load = glob.glob('*')
        load = []

        for fili in nomes_arquivos_load:
            if (not (fili[-3::] == 'pdf') and not (fili[-3::] == 'png') and not (fili[-3::] == 'jpg') and not (
                fili[-3::] == 'tif') and not (fili[-3::] == 'wps') and not (fili[-2::] == 'db')):
                load.append(fili)
        # concatenando arquivos
        nomes_arquivos = load + nomes_arquivos_pdf + nomes_arquivos_jpg
        lista = []
        for fff in nomes_arquivos:
            lista.append(fff)  # .decode("latin-1"))<-No python3 isto não funciona
        nomes_arquivos = lista
        # Acentos não funcionam fazer algo para solucionar isso

        # Abrindo Arquivo
        url = raiz + '/' + printer + '/' + arquivo
        if (not (arquivo == '*file*')):
            with open(url, 'rb') as pdf:
                if (action == 'dow'):  # Forçar Download
                    try:
                        # Tenta ler arquivo
                        response = HttpResponse(pdf.read(), content_type='application/force-download')
                        response['Content-Disposition'] = 'inline;filename=' + arquivo
                        pdf.closed
                        # Salva log
                        log = logs(data=datetime.datetime.now(), action='Down',
                                   item='Digitalizacoes/%s/%s' % (str(printer), arquivo),
                                   resumo='Digitalizacoes/%s/%s foi baixado por %s' % (
                                   str(printer), arquivo, str(request.session['userl'])), user=request.session['userl'],
                                   ip=Ip)
                        log.save()

                        return response
                    except:
                        pdf.closed
                        return render(request, 'digitalizacoes/digitalizacoes.html', {
                            'title': 'Documentos Escaneados',
                            'nomes_arquivos': nomes_arquivos,
                            'msg': sys.exc_info(),
                            'printer': printer,
                        })
                elif (action == 'ope'):  # Abrir Arquivo
                    try:
                        # Tenta ler arquivo
                        if (arquivo[-3::] == 'pdf'):
                            response = HttpResponse(pdf.read(), content_type='application/pdf')
                        elif (arquivo[-3::] == 'jpg'):
                            response = HttpResponse(pdf.read(), content_type='open')
                        response['Content-Disposition'] = 'inline;filename=' + arquivo
                        pdf.closed
                        # Salva log
                        log = logs(data=datetime.datetime.now(), action='Vis',
                                   item='Digitalizacoes/%s/%s' % (str(printer), arquivo),
                                   resumo='Digitalizacoes/%s/%s foi visualizado por %s' % (
                                   str(printer), arquivo, str(request.session['userl'])), user=request.session['userl'],
                                   ip=Ip)
                        log.save()

                        return response
                    except:
                        return render(request, 'digitalizacoes/digitalizacoes.html', {
                            'title': 'Documentos Escaneados',
                            'nomes_arquivos': nomes_arquivos,
                            'msg': sys.exc_info(),
                            'printer': printer,
                        })
                elif (action == 'del'):  # Excluir arquivo
                    try:
                        # Remover arquivo
                        pdf.closed
                        os.remove(url)
                        nomes_arquivos.remove(arquivo)

                        # Salva log
                        log = logs(data=datetime.datetime.now(), action='Exc',
                                   item='Digitalizacoes/%s/%s' % (str(printer), arquivo),
                                   resumo='Digitalizacoes/%s/%s foi excluido por %s' % (
                                   str(printer), arquivo, str(request.session['userl'])), user=request.session['userl'],
                                   ip=Ip)
                        log.save()

                        # Recarrega página com mensagem de suesso
                        return render(request, 'digitalizacoes/digitalizacoes.html', {
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
                        log = logs(data=datetime.datetime.now(), action='Err',
                                   item='Digitalizacoes/%s/%s' % (str(printer), arquivo),
                                   resumo='Arquivo não foi removido, err: %s' % (str(sys.exc_info()[1])),
                                   user=request.session['userl'], ip=Ip)
                        log.save()

                        # return redirect('/jasmine/escaneados/'+printer+'/*file*/*action*/', kwargs={'action': err})
                        return render(request, 'digitalizacoes/digitalizacoes.html', {
                            'title': 'Documentos Escaneados',
                            'nomes_arquivos': nomes_arquivos,
                            'printer': printer,
                        })
                    except:
                        pdf.closed

                        messages.error(request, str(sys.exc_info()[1]))

                        # return redirect('/jasmine/escaneados/'+printer+'/*file*/*action*/', kwargs={'action': err})
                        return render(request, 'digitalizacoes/digitalizacoes.html', {
                            'title': 'Documentos Escaneados',
                            'nomes_arquivos': nomes_arquivos,
                            'printer': printer,
                        })

        return render(request, 'digitalizacoes/digitalizacoes.html', {
            'title': 'Documentos Escaneados',
            'nomes_arquivos': nomes_arquivos,
            'printer': printer,
            'itemselec': 'DIGITALIZAÇÕES',
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

    return render(request, 'digitalizacoes/digitalizacoes.html', {
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
