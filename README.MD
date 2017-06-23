# Jasmine

Sistema de visualização de relatórios de impressões.

## Como utilizar?

1. Clone o repositório.
```console
git clone https://gitlab.com/smkbarbosa/Jasmine.git Jasmine
```
2. Crie um virtualenv com python 3.5
```console
cd Jasmine
python -m venv .Jasmine
```
3. Ative o virtualenv
```console
source .Jasmine/bin/activate
```
4. Instale as dependêcias
```console
sudo apt-get install libmysqlclient-dev
sudo apt-get install ghostscript
sudo apt-get install tesseract-ocr
sudo cp contrib/por.traineddata /usr/share/tesseract-ocr/tessdata/por.traineddata
wget http://download.gna.org/wkhtmltopdf/0.12/0.12.4/wkhtmltox-0.12.4_linux-generic-amd64.tar.xz tar xvJf wkhtmltox-0.12.4_linux-generic-amd64.tar.xz
sudo cp wkhtmltox/bin/wkhtmlto* /usr/bin/
pip install -r requirements.txt
```
5. Configure a instancia com o .env
```console
cp contrib/env-sample .env
nano .env
```
   - Defina uma SECRET_KEY segura para a instância
   - Defina DEBUG=False
6. Rodar as migrações
```console
python manage.py migrate
```
7. Execute os testes
```console
python manage.py test
```
8. Testar configuração inicial
```console
python manage.py runmodwsgi
```
   - Acessar pelo navegador o endereço: http://servidor:8000/jasmine
   - Se tudo ocorreu bem, será apresentada a página de configuração do sistema.
9. Executar o Setup
```console
sudo python manage.py runmodwsgi --setup-only --port=8000 --user user --server-root=/etc/mod_wsgi-express-80
```
10. Copie o arquivo jasmine-server para /etc/init.d/ e coloque na inicialização do sistema
```console
sudo cp contrib/jasmine-server /etc/init.d/jasmine
sudo update-rc.d jasmine defaults
```
11. Inicie o serviço
```console
sudo /etc/init.d/jasmine start
```
12. Acesse a página de configuração http://servidor:8000/jasmine
- Preencha os dados solicitados e clique em salvar
13. Criar estrutura das pastas onde serão armazenados os arquivos digitalizados, uma pasta raiz e pastas internas para cada impressora e uma pasta para arquivos temporários temp.
Exemplo:


    /home/cgti/
        Digitalizacoes/
            impressora1/
            impressora2/
            impressora3/
            temp/
13. Compartilhar as pastas das impressoras.
```console

```
14. Configurar local das digitalizações no sitema.
- Faça Login
- Acesse o menu Administração
- Acesse Conf. de Digitalizações
- Especifique o local da pasta raiz dos arquivos digitalizados.
