# Saúde Connect

Sistema de conexão entre profissionais de saúde freelancers e pacientes.

## Requisitos

- Python 3.8+
- MySQL

## Instalação

1. Clone o repositório:
```
git clone <url-do-repositorio>
```

2. Crie um ambiente virtual:
```
python -m venv venv
```

3. Ative o ambiente virtual:
- Windows:
```
venv\Scripts\activate
```
- Linux/Mac:
```
source venv/bin/activate
```

4. Instale as dependências:
```
pip install -r requirements.txt
```

5. Configure o banco de dados MySQL:
- Crie um banco de dados chamado `mydb`
- As credenciais padrão são:
  - Usuário: root
  - Senha: password
  - Host: localhost
  - Porta: 3306

## Executando a aplicação

```
python -m src.main
```

A aplicação estará disponível em `http://localhost:5000`

## Credenciais de Administrador

- Email: admin@saudeconnect.com
- Senha: admin123

## Estrutura do Projeto

- `src/models/`: Modelos de dados
- `src/routes/`: Rotas da API
- `src/static/`: Arquivos estáticos (frontend)
- `src/main.py`: Ponto de entrada da aplicação

## Funcionalidades

- Cadastro de profissionais com envio de diploma
- Cadastro de pacientes
- Painel administrativo para aprovação de profissionais
- Busca de profissionais por especialidade/atividade
- Múltiplas atividades por profissional

## Implantação em Servidores Gratuitos

### Opção 1: PythonAnywhere

1. Crie uma conta em [PythonAnywhere](https://www.pythonanywhere.com/)
2. Faça upload do arquivo zip e extraia
3. Crie um aplicativo web Flask
4. Configure o WSGI para apontar para `src.main:app`
5. Configure o banco de dados MySQL

### Opção 2: Heroku

1. Crie uma conta no [Heroku](https://www.heroku.com/)
2. Instale o Heroku CLI
3. Crie um arquivo `Procfile` com o conteúdo: `web: gunicorn src.main:app`
4. Adicione `gunicorn` ao requirements.txt
5. Configure o banco de dados (Heroku PostgreSQL ou ClearDB MySQL)

### Opção 3: Render

1. Crie uma conta no [Render](https://render.com/)
2. Crie um novo Web Service
3. Configure o comando de build: `pip install -r requirements.txt`
4. Configure o comando de start: `gunicorn src.main:app`
5. Configure o banco de dados (Render PostgreSQL)
