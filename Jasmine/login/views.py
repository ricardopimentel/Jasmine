import sys
from django.shortcuts import render

from Jasmine.administracao.forms import AdForm
from Jasmine.login.forms import LoginForm
from Jasmine.core.models import config


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

    if dominio:  # Dominio existe no banco de dados
        # Se vier algo pelo post significa que houve requisição
        if request.method == 'POST':
            # cria uma instancia do formulario com os dados vindos do request POST:
            form = LoginForm(request, data=request.POST)
            # Checa se os dados são válidos:
            if form.is_valid():
                # Chama a página novamente
                return render(request, 'login.html', {'form': form, 'err': ''})
        else:  # se não veio nada no post cria uma instancia vazia
            form = LoginForm(request)

        return render(request, 'login.html', {
            'title': 'Home',
            'form': form,
            'itemselec': 'HOME',
        })
    else:  # Dominio não existe no banco de dados
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
        else:  # se não veio nada no post cria uma instancia vazia
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