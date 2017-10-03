# Jasmine

Sistema de visualização de relatórios de impressões.

## Pré-requisitos
- Ter instalado:
    - cups+jasmine ([Parte 1](https://sempreupdate.com.br/2016/10/como-instalar-uma-impressora-em-distribuicoes-baseadas-no-ubuntu-ou-fedora-parte-1.html) e [Parte 2](https://sempreupdate.com.br/2016/11/gerando-relatorios-de-impressao-parte-2.html))

## Como utilizar?
1 Instalando Dokku
```console
wget https://raw.githubusercontent.com/dokku/dokku/v0.7.2/bootstrap.sh
sudo DOKKU_TAG=v0.7.2 bash bootstrap.sh
```

2 Gerar chave ssh (Aceite as três opções pedidas por default. Não inserir password)
```console
ssh-keygen -t rsa
```

3 Copiar a chave selecionando o conteúdo
```console
cat ~/.ssh/id_rsa.pub
```

4 Acessar o endereço IP do servidor pelo navegador, colar a chave copiada e pressionar Finish Setup
![Print1](contrib/dokkuprint1.png)

5 Criar o app Jasmine
```console
dokku apps:create jasmine
```

6 Instalar plugin mysql, criar serviço e ligar ao app
```console
sudo dokku plugin:install https://github.com/dokku/dokku-mysql.git mysql
dokku mysql:create jasmine
dokku mysql:link jasmine jasmine
```

7 Configurando DEBUG e SECRET_KEY
```console
dokku config:set fjfundo DEBUG='False'
dokku config:set fjfundo SECRET_KEY='sua secret_key'
```

8 Clone o repositório

```console
sudo dokku plugin:install https://github.com/crisward/dokku-clone.git clone
dokku clone jasmine https://gitlab.com/smkbarbosa/Jasmine.git
```

9 Instale as dependêcias

```console
sudo apt-get install libmysqlclient-dev
sudo apt-get install ghostscript
sudo apt-get install tesseract-ocr
sudo cp contrib/por.traineddata /usr/share/tesseract-ocr/tessdata/por.traineddata
wget https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.4/wkhtmltox-0.12.4_linux-generic-amd64.tar.xz tar xvJf wkhtmltox-0.12.4_linux-generic-amd64.tar.xz
sudo tar -Jxf wkhtmltox-0.12.4_linux-generic-amd64.tar.xz
sudo cp wkhtmltox/bin/wkhtmlto* /usr/bin/
```

7 Substituir o arquivo do backend do jasmine no cups e configurar banco de dados

```console
sudo cp contrib/jasmine-backend /usr/lib/cups/backend/jasmine
sudo chmod 755 /usr/lib/cups/backend/jasmine
sudo nano /usr/lib/cups/backend/jasmine
```

8 Execute os testes

```console
python manage.py test
```

13 Acesse a página de configuração http://servidor:8000/jasmine

- Preencha os dados solicitados e clique em salvar

14 Criar estrutura das pastas onde serão armazenados os arquivos digitalizados, uma pasta raiz e pastas internas para cada impressora e uma pasta para arquivos temporários temp.
Exemplo:

```tree
    /home/cgti/
        Digitalizacoes/
            impressora1/
            impressora2/
            impressora3/
            temp/
```
        
15 Compartilhar as pastas das impressoras.

```console

```

16 Configurar local das digitalizações no sitema.

- Faça Login
- Acesse o menu Administração
- Acesse Conf. de Digitalizações
- Especifique o local da pasta raiz dos arquivos digitalizados.

