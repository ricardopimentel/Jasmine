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

3 Visualizar a chave, selecionar e copiar o conteúdo
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

7 Configurando DEBUG e SECRET_KEY (Criar Secret Key segura)
```console
dokku config:set jasmine DEBUG='False'
dokku config:set jasmine SECRET_KEY='sua secret_key'
```

8 Clone o repositório, no final será aprsentado o endereço para acessar a aplicação
```console
sudo dokku plugin:install https://github.com/crisward/dokku-clone.git clone
dokku clone jasmine https://gitlab.com/smkbarbosa/Jasmine.git
```

9 Identifique ID do container
```console
sudo docker ps
```
![Print2](contrib/dokkuprint2.png)

10 Acesse o container e instale as dependêcias
```console
sudo docker exec -it <CONTAINER ID> apt-get update
sudo docker exec -it <CONTAINER ID> apt-get install ghostscript
sudo docker exec -it <CONTAINER ID> apt-get install tesseract-ocr
sudo docker exec -it <CONTAINER ID> wget https://gitlab.com/smkbarbosa/Jasmine/raw/master/contrib/por.traineddata
sudo docker exec -it <CONTAINER ID> cp por.traineddata /usr/share/tesseract-ocr/tessdata/por.traineddata
sudo docker exec -it <CONTAINER ID> wget https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.4/wkhtmltox-0.12.4_linux-generic-amd64.tar.xz
sudo docker exec -it <CONTAINER ID> tar -Jxf wkhtmltox-0.12.4_linux-generic-amd64.tar.xz
sudo docker exec -it <CONTAINER ID> cp /wkhtmltox/bin/wkhtmltopdf /usr/bin/
```

11 Criar a estrutura de pastas para receber os documentos digitalizados
```console
sudo mkdir -p  "/var/lib/dokku/data/storage/jasmine"
sudo mkdir -p  "/var/lib/dokku/data/storage/jasmine/Digitalizacoes"
sudo mkdir -p  "/var/lib/dokku/data/storage/jasmine/Digitalizacoes/Impressora 1/"
sudo mkdir -p  "/var/lib/dokku/data/storage/jasmine/Digitalizacoes/Impressora 2/"
...
sudo mkdir -p  "/var/lib/dokku/data/storage/jasmine/Digitalizacoes/temp/"
sudo chown -R dokku:dokku /var/lib/dokku/data/storage/jasmine
sudo chmod -R 777 /var/lib/dokku/data/storage/jasmine/
dokku storage:mount jasmine /var/lib/dokku/data/storage/jasmine:/app/storage
dokku ps:rebuild jasmine
```

Exemplo:

```tree
/var/lib/dokku/data/storage/jasmine/
                        Digitalizacoes/
                                impressora 1/
                                impressora 2/
                                impressora 3/
                                temp/
```
A pasta temp é obrigatória

12 Compartilhar pastas de digitalizações com samba, edite o arquivo smb.conf 
```console
sudo nano /etc/samba/smb.conf
```

Adicione o trecho abaixo no fim do arquivo para cada pasta de impressora compartilhada, não compartilhar a pasta temp
```console
[impressora1]
comment = Documentos digitalizados
path = /var/lib/dokku/data/storage/jasmine/Digitalizacoes/Impressora 1/
public = yes
guest ok = yes
writable = yes
browseable = no
```
Reinicie o Samba

```console
sudo /etc/init.d/samba restart
```

13 Executar as migrações
```console
dokku run jasmine python manage.py migrate
```

14 Visualizar dados de conexão com o banco de dados DATABASE_URL
```console
dokku config jasmine
DATABASE_URL: mysql://usuario:senha@host:porta/database
```

15 Substituir o arquivo do backend do jasmine no cups e configurar banco de dados
```console
wget https://gitlab.com/smkbarbosa/Jasmine/raw/master/contrib/jasmine-backend
sudo cp jasmine-backend /usr/lib/cups/backend/jasmine
sudo chmod 755 /usr/lib/cups/backend/jasmine
sudo chown root /usr/lib/cups/backend/jasmine
sudo nano /usr/lib/cups/backend/jasmine
```
![Print4](contrib/dokkuprint4.png)

Reiniciar CUPS
```console
sudo /etc/init.d/cups restart
```

15 Pegar IP do container e colocar no arquivo de hosts do servidor
```console
sudo docker inspect <CONTAINER ID>
```
![Print3](contrib/dokkuprint3.png)

```console
sudo nano /etc/hosts
```
Adicionar a linha
```console
<IP container>    <Nome do HostContainer>
```
Exemplo:
```console
172.17.0.4      dokku-mysql-jasmine
```

17 Acesse a página de configuração http://servidor:porta/jasmine

- Preencha os dados solicitados e clique em salvar



18 Configurar local das digitalizações no sitema.

- Faça Login
- Acesse o menu Administração
- Acesse Conf. de Digitalizações
- Especifique o local da pasta raiz dos arquivos digitalizados.
    
    ```console
    /var/lib/dokku/data/storage/jasmine/Digitalizacoes
    ```

