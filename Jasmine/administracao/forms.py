from django import forms
import sys
from django.core.exceptions import ObjectDoesNotExist
import datetime

from Jasmine.core.libs.conexaoAD3 import conexaoAD
from Jasmine.core.models import config, logs, tutoriais


class DigiForm(forms.ModelForm):
    class Meta:
        model = config
        fields = ('pasta_dig',)

    def __init__(self, *args, **kwargs):
        super(DigiForm, self).__init__(*args, **kwargs)
        self.fields['pasta_dig'].widget = forms.TextInput(attrs={
            'placeholder': 'Endereço da Pasta Digitalizações'})

        self.fields['pasta_dig'].label = ""


class AdForm(forms.ModelForm):
    # Cria dois campos que não estão no banco de dados, são eles: usuário e senha. Os dados desses campos são providos pelo Active Directory
    usuario = forms.CharField(label="", max_length=20, widget=forms.TextInput(attrs={'placeholder': 'Usuário'}))
    senha = forms.CharField(label="", widget=forms.PasswordInput(attrs={'placeholder': 'Senha'}))
    filter = forms.CharField(widget=forms.Textarea)

    class Meta:  # Define os campos vindos do Model
        model = config
        fields = ('dominio', 'endservidor', 'gadmin', 'ou')

    def __init__(self, request, *args,
                 **kwargs):  # INIT define caracteristicas para os campos de formulário vindos do Model (banco de dados)
        super(AdForm, self).__init__(*args, **kwargs)
        self.request = request
        self.fields['dominio'].widget = forms.TextInput(attrs={
            'placeholder': 'Dominio',
            'title': 'Dominio'})
        self.fields['endservidor'].widget = forms.TextInput(attrs={
            'placeholder': 'Endereço Servidor',
            'title': 'Endereço IP do controlador de dominio'})
        self.fields['gadmin'].widget = forms.TextInput(attrs={
            'placeholder': 'Grupo Administradores',
            'title': 'Grupo dos administradores do sistema'})
        self.fields['ou'].widget = forms.TextInput(attrs={
            'placeholder': 'Base',
            'title': 'Estrutura completa de onde o sistema irá buscar os elementos'})
        self.fields['dominio'].label = ""
        self.fields['endservidor'].label = ""
        self.fields['gadmin'].label = ""
        self.fields['ou'].label = ""

    def clean(self):
        # Inicializa váriaveis com os dados digitados no formulario
        cleaned_data = self.cleaned_data
        Usuario = cleaned_data.get("usuario")
        Senha = cleaned_data.get("senha")
        Dominio = cleaned_data.get("dominio")
        Endservidor = cleaned_data.get("endservidor")
        Gadmin = cleaned_data.get("gadmin")
        Ou = cleaned_data.get("ou")
        Filter = cleaned_data.get("filter")

        if Usuario and Senha:  # Usuário e senha OK
            # Cria Conexão LDAP ou = 'OU=ca-paraiso, OU=reitoria, OU=ifto, DC=ifto, DC=local'
            c = conexaoAD(Usuario, Senha, Ou, Filter)
            result = c.PrimeiroLogin(Usuario, Senha, Dominio,
                                     Endservidor, Filter)  # tenta login no ldap e salva resultado em result
            if (result == ('i')):  # Credenciais invalidas (usuario e/ou senha)
                # Adiciona erro na validação do formulário
                raise forms.ValidationError("Usuário ou senha incorretos", code='invalid')
            elif (result == ('n')):  # Server Down
                # Adiciona erro na validação do formulário
                raise forms.ValidationError("Erro na Conexão", code='invalid')
            else:  # se logou
                try:  # Tenta salvar tudo no banco de dados no id 1

                    # pegar endereço IP do cliente
                    x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
                    if x_forwarded_for:
                        Ip = x_forwarded_for.split(',')[-1].strip()
                    else:
                        Ip = self.request.META.get('REMOTE_ADDR')

                    # Pega uma instancia do item conf do banco de dados
                    conf = config.objects.get(id=1)

                    # Cria cabeçalho da váriavel resumo
                    resumo = 'Administracao/Config AD/ foi alterado por: ' + self.request.session['userl']
                    # item do resumo (itens alterados pelo usuário)
                    resumo_item = ''

                    # salva configurações anteriores em variaveis para aplicar ao log
                    dominio_old = conf.dominio
                    endservidor_old = conf.endservidor
                    gadmin_old = conf.gadmin
                    ou_old = conf.ou
                    lista_old = (dominio_old, endservidor_old, gadmin_old, ou_old)
                    # Aplica valores novos (informados pelo usuário) aos campos
                    conf.dominio = Dominio
                    conf.endservidor = Endservidor
                    conf.gadmin = Gadmin
                    conf.ou = Ou
                    conf.filter = Filter
                    lista_new = (Dominio, Endservidor, Gadmin, Ou, Filter)
                    conf.save()
                    # Salva log
                    # Criar resumo
                    lista_rotulos = ('Domínio', 'Endereço Servidor', 'Grupo Administradores', 'Base', 'Filtro')
                    # Procurar outra forma de pegar o indice do for
                    i = 0  # estou criando um contador
                    for item in lista_new:
                        if not item == lista_old[i]:
                            resumo_item += ' \nO campo ' + lista_rotulos[i] + ' tinha o valor: \n    ' + lista_old[
                                i] + '\nFoi Alterado para: \n    ' + lista_new[i] + '\n'
                        i = i + 1  # não aceita o i++ (tenso)
                    if resumo_item:
                        resumo += resumo_item
                        log = logs(
                            data=datetime.datetime.now(),
                            action='Alt',
                            item='Administração/Config AD',
                            resumo=resumo,
                            user=self.request.session['userl'],
                            ip=Ip)
                        log.save()
                except ObjectDoesNotExist:  # caso não exista nada no bd cria um id 1 com os dados passados
                    conf = config(id=1, dominio=Dominio, endservidor=Endservidor, gadmin=Gadmin, ou=Ou, filter=Filter)
                    conf.save()
                    # except:
                    # raise forms.ValidationError(sys.exc_info())
        # Sempre retorne a coleção completa de dados válidos.
        return cleaned_data


class CriarTutoForm(forms.ModelForm):
    # Sobrescrevendo alguns campos do Model
    data = forms.CharField(widget=forms.HiddenInput())
    user = forms.CharField(widget=forms.HiddenInput())
    texto = forms.CharField(widget=forms.Textarea())

    class Meta:
        model = tutoriais
        fields = ('titulo', 'texto',)

    def __init__(self, request, *args, **kwargs):
        super(CriarTutoForm, self).__init__(*args, **kwargs)
        self.request = request
        self.fields['titulo'].widget = forms.TextInput(attrs={'placeholder': 'Titulo'})
        self.fields['titulo'].label = ""

    def save(self):
        cleaned_data = self.cleaned_data
        # Inicializa váriaveis com os dados digitados no formulario
        try:
            model = tutoriais(titulo=cleaned_data.get('titulo'), texto=cleaned_data.get('texto'),
                              data=cleaned_data.get('data'), user=cleaned_data.get('user'))
            model.save()  # Salva no bd

            # pegar endereço IP do cliente
            x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                Ip = x_forwarded_for.split(',')[-1].strip()
            else:
                Ip = self.request.META.get('REMOTE_ADDR')
            # Cria cabeçalho da váriavel resumo
            resumo = 'Um novo tutorial foi criado por: ' + self.request.session[
                'userl'] + '\nTitulo: \n' + cleaned_data.get('titulo') + '\nTexto: ' + cleaned_data.get('texto')
            # Salvar log
            log = logs(
                data=datetime.datetime.now(),
                action='Inc',
                item='Administração/Tutorial',
                resumo=resumo,
                user=self.request.session['userl'],
                ip=Ip)
            log.save()
        except:
            raise forms.ValidationError(sys.exc_info()[1])
        # Sempre retorne a coleção completa de dados válidos.
        return cleaned_data