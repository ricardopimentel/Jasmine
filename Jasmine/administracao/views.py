import sys

import datetime
from django.contrib import messages
from django.db import connection
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from Jasmine.administracao.forms import DigiForm, AdForm, CriarTutoForm
from Jasmine.core.models import config, logs, tutoriais


def pasta_digi(request):
    if request.session['usertip'] == 'admin':
        try:
            model = (config.objects.get(id=1))
        except:
            model = ''
            messages.error(request, sys.exc_info())
        # Vefirica se veio algo pelo POST
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
                resumo = 'Administracao/Config Digitalizacoes/ foi alterado por: ' + request.session[
                    'userl'] + '\nO campo Endereco pasta digitalizacoes tinha o valor: \n    ' + pasta_old + '\nFoi Alterado para: \n    ' + pasta_new + '\n'
                log = logs(
                    data=datetime.datetime.now(),
                    action='Alt',
                    item='Administração/Config AD',
                    resumo=resumo,
                    user=request.session['userl'],
                    ip=Ip)
                log.save()

                messages.success(request, 'Configurações salvas com sucesso!')
            return render(request, 'admin_config_pasta_digi.html', {
                'form': form,
                'itemselec': 'ADMINISTRAÇÃO',
            })
        # Se não veio algo do POST cria instancia vazia dos formulários com os dados vindos do banco de dados
        else:
            form = DigiForm(initial={'pasta_dig': model.pasta_dig})
            return render(request, 'admin_config_pasta_digi.html', {
                'form': form,
                'itemselec': 'ADMINISTRAÇÃO',
            })
    else:
        messages.error(request, "Você não tem permissão para acessar essa página, redirecionando para HOME")
        return redirect('/jasmine/')


def dados_ad(request):
    if request.session['usertip'] == 'admin':
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
            return render(request, 'admin_config_ad.html', {'form': form})
        # Se não veio algo do POST cria instancia vazia dos formulários com os dados vindos do banco de dados
        else:
            form = AdForm(request,
                          initial={'dominio': model.dominio, 'endservidor': model.endservidor, 'gadmin': model.gadmin,
                                   'ou': model.ou, 'filter': model.filter})
            return render(request, 'admin_config_ad.html', {
                'form': form,
                'itemselec': 'ADMINISTRAÇÃO',
            })
    else:
        messages.error(request, "Você não tem permissão para acessar essa página, redirecionando para HOME")
        return redirect('/jasmine/')


def add_tutorial(request):
    if request.session['usertip'] == 'admin':
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
            return render(request, 'admin_criacao_tutorial.html', {'form': form})
        # Se não veio algo do POST cria instancia vazia dos formulários com os dados vindos do banco de dados
        else:
            # Cria uma instancia Vazia do form
            form = CriarTutoForm(request, initial={'data': datetime.datetime.today(), 'user': request.session['nome']})
            return render(request, 'admin_criacao_tutorial.html', {
                'form': form,
                'itemselec': 'ADMINISTRAÇÃO',
            })
    else:
        return redirect('/jasmine/')


def admin(request):
    if request.session['usertip'] == 'admin':
        msg = ''
        return render(request, 'admin_home.html', {
            'itemselec': 'ADMINISTRAÇÃO',
            'msg': msg,
        })
    else:
        messages.error(request, "Você não tem permissão para acessar essa página, redirecionando para HOME")
        return redirect('/jasmine/')


def view_tutorial(request, Action, Id):
    if request.session['usertip'] == 'admin':
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
                    model = tutoriais.objects.get(id=Id)

                    # Salva itens antigos em variaves para gerar log
                    titulo_old = model.titulo
                    texto_old = model.texto

                    # Salva os itens novos (digitados pelo usuário)
                    model.titulo = request.POST['titulo']
                    model.texto = request.POST['texto']
                    titulo_new = request.POST['titulo']
                    texto_new = request.POST['texto']
                    model.save()  # Salva no bd

                    # Resumo do que foi feito
                    resumo = 'Um tutorial foi alterado por: ' + request.session['userl']
                    resumo_item = ''
                    if not titulo_old == titulo_new:
                        resumo_item += '\nO Titulo foi alterado de:\n    ' + titulo_old + '\npara:\n    ' + titulo_new
                    if not texto_old == texto_new:
                        resumo_item += '\nO Texto foi alterado de:\n' + texto_old + '\npara:\n' + texto_new
                    resumo += resumo_item

                    # Salvar log
                    log = logs(
                        data=datetime.datetime.now(),
                        action='Alt',
                        item='Administração/Tutorial',
                        resumo=resumo,
                        user=request.session['userl'],
                        ip=Ip)
                    log.save()
                except:
                    raise sys.exc_info()[1]
                    # Salvar log
                    log = logs(
                        data=datetime.datetime.now(),
                        action='Err',
                        item='Administração/Tutorial',
                        resumo=sys.exc_info(),
                        user=request.session['userl'],
                        ip=Ip)
                    log.save()
                # Chama a página novamente
                messages.success(request, 'Tutorial salvo com sucesso!')
                # Cria uma instancia Vazia do form
                # Gera form de criar tutorial
                form = CriarTutoForm(request, initial={'data': datetime.datetime.today(), 'user': request.session['nome']})
            # Depois de salvar a edição, redireciona para o criar tutorial
            return render_to_response('admin_criacao_tutorial.html', {'form': form}, context_instance=RequestContext(request))
        # Se não veio algo do POST cria instancia vazia dos formulários com os dados vindos do banco de dados
        else:
            # Verifica no banco de dados se o id passado equivale a algum tutorial salvo
            bd = []
            try:  # tenta conexao e buscar id do tutorial
                bd = tutoriais.objects.get(id=Id)
            except:
                # Salvar log
                log = logs(
                    data=datetime.datetime.now(),
                    action='Err',
                    item='Administração/Tutorial',
                    resumo=sys.exc_info(),
                    user=request.session['userl'],
                    ip=Ip)
                log.save()
            if bd:  # se houver retorno no bd
                if Action == 'delete':
                    # Guarda informações antes de excluir
                    titulo = bd.titulo
                    texto = bd.texto

                    # Apaga tutorial com o id informado
                    bd.delete()

                    # Resumo do que foi feito
                    resumo = 'Um tutorial foi excluido por: ' + request.session['userl']
                    resumo += '\nO Titulo era:\n    ' + titulo + '\nO Texto era:\n    ' + texto

                    # Salvar log
                    log = logs(
                        data=datetime.datetime.now(),
                        action='Exc',
                        item='Administração/Tutorial',
                        resumo=resumo,
                        user=request.session['userl'],
                        ip=Ip)
                    log.save()

                    # Renderizar a pagina principal de ajuda, com msg de excusão bem sucedida ou não
                    tutos = tutoriais.objects.all()
                    lasttutos = tutoriais.objects.all().order_by('-id')[:3]
                    messages.success(request, "Tutorial Excluído com Sucesso!")
                    return render(request, 'admin_ajuda.html', {
                        'title': 'Ajuda',
                        'tutos': tutos,
                        'last': lasttutos,
                        'itemselec': 'AJUDA',
                    })
                else:
                    # Cria uma instancia preenchida do editar tutorial form
                    form = CriarTutoForm(request,
                                         initial={'data': bd.data, 'titulo': bd.titulo, 'texto': bd.texto, 'user': bd.user})
                    return render(request, 'admin_edicao_tutorial.html', {
                        'form': form,
                        'itemselec': 'ADMINISTRAÇÃO',
                        'id': Id,
                    })
            else:
                # Cria uma instancia Vazia do form para criar um tutorial novo
                form = CriarTutoForm(request, initial={'data': datetime.datetime.today(), 'user': request.session['nome']})
                messages.error(request, "Tutorial desejado não existe, você pode criar um novo!")
                return render(request, 'admin_criacao_tutorial.html', {
                    'form': form,
                    'itemselec': 'ADMINISTRAÇÃO',
                    'id': Id,
                })
    else:
        messages.error(request, "Você não tem permissão para acessar essa página, redirecionando para HOME")
        return redirect('/jasmine/')


def ajuda(request, topc):
    tutos = tutoriais.objects.all()
    lasttutos = tutoriais.objects.all().order_by('-id')[:3]
    if topc == '**topc**': # Se for a url padrão, rederiza a página inicial
        # Finalizando renderização da página
        return render(request, 'admin_ajuda.html', {
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
        return render(request, 'admin_ajuda.html', {
                             'title': 'Ajuda',
                             'tutos': tutos,
                             'itemselec': 'AJUDA',
                             'last': lasttutos,
                             'post': post,
                         })