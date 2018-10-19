import sys
from django.shortcuts import render, redirect, resolve_url as r

from Jasmine.administracao.forms import AdForm
from Jasmine.login.forms import LoginForm
from Jasmine.core.models import config


def login(request):
    try:  # Verificar se usuario esta logado
        if request.session['nome']:
            return redirect(r('home'))
    except KeyError: # Se não estiver logado, prepara tela de login
        # Preparando menu
        set_menu_de_login(request)

        if get_dominio():  # Se dominio existe no banco de dados, não é o promeiro acesso ao sistema
            if request.method == 'POST':
                # cria uma instancia do formulario com os dados vindos do request POST:
                form = LoginForm(request, data=request.POST)
                # Checa se os dados são válidos:
                if form.is_valid():
                    # Caso o login seja concluído, redireciona para a HOME
                    return redirect(r('home'))
            else:  # se não veio nada no post cria uma instancia vazia
                form = LoginForm(request)

            return render(request, 'login.html', {
                'title': 'Home',
                'form': form,
                'itemselec': 'HOME',
            })
        else:  # Dominio não existe no banco de dados, redireciona para página de primeiro acesso
            return redirect(r('primeiro_acesso'))

def logout(request):
    try:
        del request.session['nome']
        del request.session['userl']
        del request.session['menu']
        del request.session['url']
    except KeyError:
        print(sys.exc_info())
    return redirect(r('home'))

def primeiroacesso(request):
    if request.method == 'POST':
        # cria uma instancia do formulario de preenchimento dos dados do AD com os dados vindos do request POST:
        form = AdForm(request, data=request.POST)
        # Checa se os dados são válidos:
        if form.is_valid():
            # Cria uma instancia vazia do formulário de Login
            form = LoginForm(request)
            # Chama a página novamente
            return render(request, 'login.html', {'form': form, 'err': ''})
    else:  # se não veio nada no post cria uma instancia vazia
        form = AdForm(request)
    return render(request, 'admin_config_ad_inicial.html', {
        'title': 'Home',
        'form': form,
        'itemselec': 'HOME',
    })

def set_menu_de_login(request):
    # Preparando o Menu
    request.session['menu'] = ['HOME']
    request.session['url'] = ['jasmine/login/']
    request.session['img'] = ['home24.png']

def get_dominio():
    try:
        conf = config.objects.get(id=1) # Procura a configuração do ad no banco de dados, ela tem que estar no indice 1 da tabela config
        return conf.dominio
    except:
        return None