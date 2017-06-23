# Jasmine

Sistema de visualização de relatórios de impressões.

## Como utilizar?

1. Clone o repositório.
2. Crie um virtualenv com python 3.5
3. Ative o virtualenv
4. Instale as dependêcias
5. Configure a instancia com o .env
    - Defina uma SECRET_KEY segura para a instância
    - Defina DEBUG=False
6. Execute os testes

```console
git clone https://gitlab.com/smkbarbosa/Jasmine.git Jasmine
cd Jasmine
python -m venv .Jasmine
source .Jasmine/bin/activate
pip install -r requirements.txt
cp contrib/env-sample .env
nano .env
python manage.py test
```
