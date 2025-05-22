# 🩺 SAÚDE CONNECT

[![GitHub repo size](https://img.shields.io/github/repo-size/escariao/saude-connect)](https://github.com/escariao/saude-connect)
[![GitHub issues](https://img.shields.io/github/issues/escariao/saude-connect)](https://github.com/escariao/saude-connect/issues)
[![GitHub last commit](https://img.shields.io/github/last-commit/escariao/saude-connect)](https://github.com/escariao/saude-connect/commits/master)

O **Saúde Connect** é uma plataforma que conecta profissionais de saúde freelancers com pacientes que buscam atendimento especializado. O sistema permite que profissionais cadastrem múltiplas especialidades e serviços, enquanto pacientes podem encontrar o profissional ideal para suas necessidades de saúde.  

**Funcionamento online**: https://saude-connect.onrender.com  

## 🚀 **Principais Funcionalidades**

✅ **Cadastro de Profissionais** - Com envio de diploma para verificação e aprovação administrativa.

✅ **Cadastro de Pacientes** - Interface simples para pacientes se registrarem na plataforma.

✅ **Painel Administrativo** - Para aprovação de profissionais e gerenciamento de especialidades.

✅ **Múltiplas Especialidades** - Profissionais podem cadastrar diversas especialidades e serviços.

✅ **Sistema de Busca** - Pacientes podem encontrar profissionais por especialidade ou categoria.

✅ **Perfis Detalhados** - Informações completas sobre cada profissional e seus serviços.

## 🔧 **Tecnologias Utilizadas**

| Tecnologia | Descrição |
|------------|-----------|
| **🐍 Python/Flask** | Framework web para backend |
| **🗄️ PostgreSQL/MySQL** | Banco de dados relacional |
| **🌐 HTML/CSS/JS** | Frontend responsivo |
| **🔒 JWT** | Autenticação e autorização |
| **📱 Bootstrap** | Framework CSS para design responsivo |

## 💻 **Como Usar**

### Instalação Local

```bash
# Clone o repositório
git clone https://github.com/escariao/saude-connect.git

# Entre no diretório
cd saude-connect

# Crie um ambiente virtual
python -m venv venv

# Ative o ambiente virtual
# No Windows:
venv\Scripts\activate
# No Linux/Mac:
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

# Execute a aplicação
python -m src.main
```

### Implantação no Render

1. Crie uma conta no [Render](https://render.com)
2. Conecte seu repositório GitHub
3. Crie um novo Web Service apontando para o repositório
4. Configure as variáveis de ambiente:
   - `SECRET_KEY`: Chave secreta para a aplicação
   - `DATABASE_URL`: URL de conexão com o PostgreSQL
   - `FLASK_ENV`: `production`
5. Configure o Build Command: `pip install -r requirements.txt`
6. Configure o Start Command: `gunicorn src.main:app`

## 📋 **Estrutura do Projeto**

```
saude-connect/
├── src/
│   ├── models/         # Modelos de dados
│   ├── routes/         # Rotas da API
│   ├── static/         # Arquivos estáticos (CSS, JS, imagens)
│   │   ├── css/        # Estilos CSS
│   │   ├── js/         # Scripts JavaScript
│   │   └── uploads/    # Uploads de arquivos (diplomas)
│   └── main.py         # Ponto de entrada da aplicação
├── venv/               # Ambiente virtual Python
├── requirements.txt    # Dependências do projeto
└── README.md           # Este arquivo
```

## 🔐 **Credenciais de Teste**

### Administrador
- **Email**: admin@saudeconnect.com
- **Senha**: admin123

## 📱 **Páginas Principais**

- **/** - Página inicial
- **/login.html** - Login de usuários
- **/cadastro-paciente.html** - Cadastro de pacientes
- **/cadastro-profissional.html** - Cadastro de profissionais
- **/busca.html** - Busca de profissionais
- **/admin.html** - Painel administrativo
- **/perfil-paciente.html** - Perfil do paciente
- **/perfil-profissional.html** - Perfil do profissional

## 🔄 **API Endpoints**

### Autenticação
- `POST /api/auth/login` - Login de usuários
- `POST /api/auth/register/patient` - Cadastro de pacientes
- `POST /api/auth/register/professional` - Cadastro de profissionais

### Profissionais
- `GET /api/search/professionals` - Busca de profissionais
- `GET /api/search/activities/categories` - Lista de categorias de atividades

### Administração
- `GET /api/admin/professionals/pending` - Lista de profissionais pendentes
- `POST /api/admin/professionals/{id}/approve` - Aprovar profissional
- `POST /api/admin/professionals/{id}/reject` - Rejeitar profissional

## 📝 **Requisitos do Sistema**

- Python 3.8+
- PostgreSQL ou MySQL
- Navegador web moderno

---

### Desenvolvido por Andrey Montenegro
