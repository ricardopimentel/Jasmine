# encoding: utf-8
# encoding: iso-8859-1
# encoding: win-1252

import ldap3 as ldap
from Jasmine.impressoes.models import config

class conexaoAD(object):
    
    def __init__(self, username, password, base):
        try:
            conf = config.objects.get(id=1)
            self.username = username
            self.password = password
            self.base = base
            self.dominio = conf.dominio
            self.endservidor = conf.endservidor
        except:
            self.username = username
            self.password = password
            self.base = base
            self.dominio = ''
            self.endservidor = ''
            
        # servidor ad
        self.LDAP_SERVER = 'ldap://%s' % self.endservidor
        # nome completo do usuario no AD
        self.LDAP_USERNAME = self.username+ '@'+ self.dominio
        # sua senha
        self.LDAP_PASSWORD = self.password
        
    def Login(self):
        try:
            l=ldap.initialize(self.LDAP_SERVER)
            l.set_option(ldap.OPT_REFERRALS, 0)
            l.simple_bind_s(self.LDAP_USERNAME, self.LDAP_PASSWORD)
            user_filter = '(name=%s)' %self.username
            base_dn = self.base
            res = l.search_ext_s(base_dn, ldap.SCOPE_SUBTREE, user_filter, ['displayName', 'memberof'])
            l.unbind()
            try:
                return res[0]
            except:
                return 'o' # Usuario fora do escopo permitido
        except ldap.INVALID_CREDENTIALS:
            l.unbind()
            return 'i' # Credenciais Invalidas
        except ldap.SERVER_DOWN:
            return 'n' # Servidor não encotrado

    def PrimeiroLogin(self, Username, Password, Dominio, Endservidor):
        # servidor ad
        LDAP_SERVER = 'ldap://%s' % Endservidor
        # nome completo do usuario no AD
        LDAP_USERNAME = Username+ '@'+ Dominio
        # sua senha
        LDAP_PASSWORD = Password
        
        try:
            l=ldap.initialize(LDAP_SERVER)
            l.set_option(ldap.OPT_REFERRALS, 0)
            l.simple_bind_s(LDAP_USERNAME, LDAP_PASSWORD)
            user_filter = '(name=%s)' %Username
            res = l.search_ext_s(self.base, ldap.SCOPE_SUBTREE, user_filter, ['displayName', 'memberof'])
            l.unbind()
            return res[0]
        except ldap.INVALID_CREDENTIALS:
            l.unbind()
            return 'i'
        except ldap.SERVER_DOWN:
            return 'n'
    
    def TestarCredenciais(self): # desconsiderar metodo, apenas testes
        try:
            # build a client
            ldap_client = ldap.initialize(self.LDAP_SERVER)
            # perform a synchronous bind
            ldap_client.set_option(ldap.OPT_REFERRALS, 0)
            ldap_client.simple_bind_s(self.LDAP_USERNAME, self.LDAP_PASSWORD)
            ldap_client.unbind()
            return 's'
        except ldap.INVALID_CREDENTIALS:
            ldap_client.unbind()
            return 'i'
        except ldap.SERVER_DOWN:
            return 'n'
        # all is well
        # get all user groups and store it in cerrypy session for future use
        #cherrypy.session[username] = str(ldap_client.search_s(base_dn, ldap.SCOPE_SUBTREE, ldap_filter, attrs)[0][1]['memberOf'])


