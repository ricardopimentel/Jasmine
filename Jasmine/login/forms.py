from django import forms

from Jasmine.core.libs.conexaoAD3 import conexaoAD
from Jasmine.core.models import config


class LoginForm(forms.Form):
    usuario = forms.CharField(label="", max_length=20, widget=forms.TextInput(attrs={'placeholder': 'Login'}))
    senha = forms.CharField(label="", widget=forms.PasswordInput(attrs={'placeholder': 'Senha'}))
    
    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean(self):
        # tenta conectar ao banco de dados para pegar parametros do ldap
        ou = ''
        filter = ''
        try:
            conf = config.objects.get(id=1)
            ou = conf.ou
            filter = conf.filter
        except:
            pass

        # Inicializa váriaveis
        cleaned_data = self.cleaned_data
        usuario = cleaned_data.get("usuario")
        senha = cleaned_data.get("senha")
        if usuario and senha:
            # Cria Conexão LDAP ou = 'OU=ca-paraiso, OU=reitoria, OU=ifto, DC=ifto, DC=local'
            c = conexaoAD(usuario, senha, ou, filter)
            result = c.Login() #tenta login no ldap
            if(result == ('i')): # Credenciais invalidas
                # Adiciona erro na validação do formulário
                raise forms.ValidationError("Usuário ou senha incorretos")
            elif(result == ('n')): # Server Down
                # Adiciona erro na validação do formulário
                raise forms.ValidationError("Servidor AD não encontrado", code='invalid')
            elif(result == ('o')): # Usuario fora do escopo permitido
                # Adiciona erro na validação do formulário
                print('antes')
                raise forms.ValidationError("Usuário não tem permissão para acessar essa página", code='invalid')
            else: # se logou
                # Retirar virgulas do member of
                result['memberOf'] = str(result['memberOf']).replace(',', '')
                # Remover cabeçalhos desnecessarios 
                ret = repr(result)
                # Verificar se usuário é administrador grupo de admin = G_ADMINS_AD_IFTO
                if(ret.find(str(conf.gadmin)) > -1):
                    self.request.session['usertip'] = 'admin'
                    # Preparar menu admin
                    self.request.session['menu'] = ['HOME', 'RELATÓRIOS', 'DIGITALIZAÇÕES', 'ADMINISTRAÇÃO', 'AJUDA']
                    self.request.session['url'] = ['jasmine/', 'jasmine/relatorio/*user*/*printer*/*host*/', 'jasmine/escaneados/*printer*/*file*/*action*', 'jasmine/admin', 'jasmine/ajuda/**topc**']
                    self.request.session['img'] = ['home24.png', 'relatorio24.png', 'scan24.png', 'admin24.png', 'ajuda24.png']
                else:
                    self.request.session['usertip'] = 'user'
                    # Preparar menu user
                    self.request.session['menu'] = ['HOME', 'RELATÓRIOS', 'DIGITALIZAÇÕES', 'AJUDA']
                    self.request.session['url'] = ['jasmine/', 'jasmine/relatorio/*user*/*printer*/*host*/', 'jasmine/escaneados/*printer*/*file*/*action*', 'jasmine/ajuda/**topc**']
                    self.request.session['img'] = ['home24.png', 'relatorio24.png', 'scan24.png', 'ajuda24.png']

                ret = ret.replace('[', '')
                ret = ret.replace(']', '')
                result = eval(ret)
                #logou então, adicionar os dados do usuário na sessão
                self.request.session['userl'] = usuario
                self.request.session['nome'] = result['displayName'].title()
        
        # Sempre retorne a coleção completa de dados válidos.
        return cleaned_data



