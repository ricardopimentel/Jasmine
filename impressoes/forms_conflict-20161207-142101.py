# -*- coding: utf-8 -*-
from django import forms
from impressoes.libs.conexaoAD import conexaoAD
from impressoes.models import config, tutoriais
import sys
from tinymce.widgets import TinyMCE

class LoginForm(forms.Form):
    usuario = forms.CharField(label="", max_length=20, widget=forms.TextInput(attrs={'placeholder': 'Login'}))
    senha = forms.CharField(label="", widget=forms.PasswordInput(attrs={'placeholder': 'Senha'}))
    
    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean(self):
        # tenta conectar ao banco de dados para pegar parametros do ldap
        ou = ''
        try:
            conf = config.objects.get(id=1)
            ou = conf.ou
        except:
            ou = ''
            
        # Inicializa váriaveis
        cleaned_data = self.cleaned_data
        usuario = cleaned_data.get("usuario")
        senha = cleaned_data.get("senha")
        if usuario and senha:
            # Cria Conexão LDAP ou = 'OU=ca-paraiso, OU=reitoria, OU=ifto, DC=ifto, DC=local'
            c = conexaoAD(usuario, senha, ou)
            result = c.Login() #tenta login no ldap
            if(result == ('i')):
                # Adiciona erro na validação do formulário
                raise forms.ValidationError("Usuário ou senha incorretos", code='invalid')
            elif(result == ('n')):
                # Adiciona erro na validação do formulário
                raise forms.ValidationError("Servidor AD não encontrado", code='invalid')
            else: # se logou
                # Retirar virgulas do member of
                result[1]['memberOf'] = str(result[1]['memberOf']).replace(',', '')
                # Remover cabeçalhos desnecessarios 
                ret = repr(result[1])
                # Verificar se usuário é administrador grupo de admin = G_ADMINS_AD_IFTO
                if(ret.find(str(conf.gadmin)) > -1):
                    self.request.session['usertip'] = 'admin'
                    # Preparar menu admin
                    self.request.session['menu'] = ['HOME', 'RELATÓRIOS', 'DIGITALIZAÇÕES', 'ADMINISTRAÇÃO', 'AJUDA']
                    self.request.session['url'] = ['jasmine/', 'jasmine/relatorio/*user*/*printer*/*host*/', 'jasmine/escaneados/*printer*/*file*/*action*', 'jasmine/admin', 'jasmine/ajuda/**topc**']
                else:
                    self.request.session['usertip'] = 'user'
                    # Preparar menu user
                    self.request.session['menu'] = ['HOME', 'RELATÓRIOS', 'DIGITALIZAÇÕES', 'AJUDA']
                    self.request.session['url'] = ['jasmine/', 'jasmine/relatorio/*user*/*printer*/*host*/', 'jasmine/escaneados/*printer*/*file*/*action*', 'jasmine/ajuda/**topc**']

                ret = ret.replace('[', '')
                ret = ret.replace(']', '')
                result = eval(ret)
                #logou então, adicionar os dados do usuário na sessão
                self.request.session['userl'] = usuario
                self.request.session['nome'] = result['displayName'].title()
        
        # Sempre retorne a coleção completa de dados válidos.
        return cleaned_data
    
class DigiForm(forms.ModelForm):
    class Meta:
        model = config
        fields = ('pasta_dig',)
        
    def __init__(self, *args, **kwargs):
        super(DigiForm, self).__init__(*args, **kwargs)
        self.fields['pasta_dig'].widget = forms.TextInput(attrs={
            'placeholder': 'Endereço da Pasta Digitalizações'})
        
        self.fields['pasta_dig'].label=""

class AdForm(forms.ModelForm):
    # Cria dois campos que não estão no banco de dados, são eles: usuário e senha. Os dados desses campos são providos pelo Active Directory 
    usuario = forms.CharField(label="", max_length=20, widget=forms.TextInput(attrs={'placeholder': 'Usuário'}))
    senha = forms.CharField(label="", widget=forms.PasswordInput(attrs={'placeholder': 'Senha'}))
    
    class Meta: # Define os campos vindos do Model
        model = config
        fields = ('dominio', 'endservidor', 'gadmin', 'ou',)
        
    def __init__(self, request, *args, **kwargs): # INIT define caracteristicas para os campos de formulário vindos do Model (banco de dados)
        super(AdForm, self).__init__(*args, **kwargs)
        self.fields['dominio'].widget = forms.TextInput(attrs={
            'placeholder': 'Dominio',
            'title': 'Dominio'})
        self.fields['endservidor'].widget = forms.TextInput(attrs={
            'placeholder': 'Endereço',
            'title': 'Endereço IP do controlador de dominio'})
        self.fields['gadmin'].widget = forms.TextInput(attrs={
            'placeholder': 'Grupo Administradores',
            'title': 'Grupo dos administradores do sistema'})
        self.fields['ou'].widget = forms.TextInput(attrs={
            'placeholder': 'Base',
            'title': 'Estrutura completa de onde o sistema irá buscar os elementos'})
        self.fields['dominio'].label=""
        self.fields['endservidor'].label=""
        self.fields['gadmin'].label=""
        self.fields['ou'].label=""
    
    def clean(self):
        # Inicializa váriaveis com os dados digitados no formulario
        cleaned_data = self.cleaned_data
        usuario = cleaned_data.get("usuario")
        senha = cleaned_data.get("senha")
        dominio = cleaned_data.get("dominio")
        endservidor = cleaned_data.get("endservidor")
        gadmin = cleaned_data.get("gadmin")
        ou = cleaned_data.get("ou")      
        
        if usuario and senha:# Usuário e senha OK
            # Cria Conexão LDAP ou = 'OU=ca-paraiso, OU=reitoria, OU=ifto, DC=ifto, DC=local'
            c = conexaoAD(usuario, senha, ou)
            result = c.PrimeiroLogin(usuario, senha, dominio, endservidor) #tenta login no ldap e salva resultado em result
            if(result == ('i')): # Credenciais invalidas (usuario e/ou senha)
                # Adiciona erro na validação do formulário
                raise forms.ValidationError("Usuário ou senha incorretos", code='invalid')
            elif(result == ('n')): # Server Down
                # Adiciona erro na validação do formulário
                raise forms.ValidationError("Erro na Conexão", code='invalid')
            else: # se logou
                try: # Tenta salvar tudo no banco de dados
                    conf = config.objects.get(id=1)
                    conf.dominio = dominio
                    conf.endservidor = endservidor
                    conf.gadmin = gadmin
                    conf.ou = ou
                    conf.save()
                except:
                    raise forms.ValidationError(sys.exc_info())
        # Sempre retorne a coleção completa de dados válidos.
        return cleaned_data

class CriarTutoForm(forms.ModelForm):
    # Sobrescrevendo alguns campos do Model
    data = forms.CharField(widget=forms.HiddenInput())
    user = forms.CharField(widget=forms.HiddenInput())
    
    class Meta:
        model = tutoriais
        fields = ('titulo','texto',)
        
    def __init__(self, *args, **kwargs):
        super(CriarTutoForm, self).__init__(*args, **kwargs)
        self.fields['titulo'].widget = forms.TextInput(attrs={'placeholder': 'Titulo'})
        
        self.fields['titulo'].label=""
        self.fields['texto'].label="Tutorial"
    
    def clean(self):
        cleaned_data = self.cleaned_data
        # Inicializa váriaveis com os dados digitados no formulario
        try:            
            model = tutoriais(titulo = cleaned_data.get('titulo'), texto = cleaned_data.get('texto'), data = cleaned_data.get('data'), user = cleaned_data.get('user'))
            model.save() # Salva no bd
        except:
            raise forms.ValidationError(sys.exc_info()[1])
        # Sempre retorne a coleção completa de dados válidos.
        return cleaned_data
        
