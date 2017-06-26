import sys

import datetime
from django.contrib import messages
from django.db import connection
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from Jasmine.administracao.forms import DigiForm, AdForm, CriarTutoForm
from Jasmine.core.models import config, logs, tutoriais


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
        return render(request, 'admin_config_ad.html', {'form': form})
    # Se não veio algo do POST cria instancia vazia dos formulários com os dados vindos do banco de dados
    else:
        form = AdForm(request,
                      initial={'dominio': model.dominio, 'endservidor': model.endservidor, 'gadmin': model.gadmin,
                               'ou': model.ou})
        return render(request, 'admin_config_ad.html', {
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
        return render(request, 'admin_criacao_tutorial.html', {'form': form})
    # Se não veio algo do POST cria instancia vazia dos formulários com os dados vindos do banco de dados
    else:
        # Cria uma instancia Vazia do form
        form = CriarTutoForm(request, initial={'data': datetime.datetime.today(), 'user': request.session['nome']})
        return render(request, 'admin_criacao_tutorial.html', {
            'form': form,
            'itemselec': 'ADMINISTRAÇÃO',
        })


def admin(request):
    msg = ''
    # Vefirica se veio aolgo pelo POST
    # Cria uma instancia Vazia do form
    return render(request, 'admin_home.html', {
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
                return render(request, 'ajuda.html', {
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

@csrf_exempt
def viewlogs(request, user_u, action_u, host_u):
    # preparação dos parametros iniciais
    data_final = datetime.datetime.today()
    data_inicial = datetime.datetime.fromordinal(data_final.toordinal() - 30)
    titulo = "Registros de Logs dos ultimos 30 dias"
    user_U = user_u
    action_U = action_u
    host_U = host_u
    err = ''

    # Verificar dados salvos na sessão
    try:
        # Se tiver data salva na sessão
        if (request.session['data_iniciall']):
            data_inicial = request.session['data_iniciall']  # Pega data da sessão
            titulo = 'Registros no periodo de ' + datetime.datetime.strptime(str(data_inicial), '%Y-%m-%d').strftime(
                '%d/%m/%Y')  # atualiza titulo
        if (request.session['data_finall']):
            data_final = request.session['data_finall']  # Pega data da sessão
            titulo = titulo + ' a ' + datetime.datetime.strptime(str(data_final), '%Y-%m-%d').strftime(
                '%d/%m/%Y')  # atualiza titulo
        if (request.session['user']):
            user_u = request.session['user']  # Pega usuário da sessão
        if (request.session['action']):
            action_u = request.session['action']  # Pega impressora da sessão
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
    if (action_U == ' '):
        action_u = ''
        request.session['action'] = action_u
    elif (not action_U == 'action'):
        request.session['action'] = action_U
        action_u = action_U
    if (host_U == ' '):
        host_u = ''
        request.session['host'] = host_u
    elif (not host_U == 'host'):
        request.session['host'] = host_U
        host_u = host_U

    # verificar se URL é http://localhost:8000/relatorio/*user*/*action*/*host*/ essa url é o inicio padrão da página relatório
    if (user_U == '*user*' and action_U == '*action*' and host_U == '*host*'):
        titulo = 'Registros de Logs do Sistema'

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
        # verifica se veio ação pelo post
        if (request.POST['action-r']):
            action_u = request.POST['action-r']
            if (action_u == ' '):
                action_u = ''
            # Salvar a printer na sessão
            request.session['action'] = action_u
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
            request.session['data_iniciall'] = data_inicial
            titulo = 'Registros de Logs no periodo de ' + datetime.datetime.strptime(str(data_inicial),
                                                                                     '%Y-%m-%d').strftime(
                '%d/%m/%Y')  # atualiza titulo
        # verifica se veio data final pelo post
        if (request.POST['data-final']):
            data_final = request.POST['data-final']
            # Salvar a data final na sessão
            request.session['data_finall'] = data_final
            titulo = titulo + ' a ' + datetime.datetime.strptime(str(data_final), '%Y-%m-%d').strftime(
                '%d/%m/%Y')  # atualiza titulo
        # Verifica se há erros no formulario
        if (data_inicial > data_final):
            err = "Erro no intervalo da data"
            titulo = 'Registros de Logs do Sistema'

    # preparando consultas ao banco de dados
    cursor = connection.cursor()
    cursor.execute("SELECT user FROM core_logs where user != '' GROUP BY user")
    top_users = cursor.fetchall()
    cursor.execute("SELECT action FROM core_logs where action != '' GROUP BY action")
    top_actions = cursor.fetchall()
    cursor.execute("SELECT ip FROM core_logs where ip != '' GROUP BY ip")
    top_hosts = cursor.fetchall()
    cursor.execute(
        "SELECT data, action, user, ip, item, resumo FROM `core_logs` WHERE user like '%" + user_u + "%' and action like '%" + action_u + "%' and ip like '%" + host_u + "%' and (data BETWEEN '" + str(
            data_inicial) + " 00:00:00' and '" + str(data_final) + " 23:59:59' )")
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
