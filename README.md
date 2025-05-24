
# 🚀 Saúde Connect 🩺

![Status](https://img.shields.io/badge/status-active-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)
![Version](https://img.shields.io/badge/version-1.0.0-yellow)

## 📝 Descrição
O **Saúde Connect** é uma plataforma para conectar **pacientes** e **profissionais da saúde**. Inspirado no Upwork, mas especializado em atendimentos domiciliares.

➡️ Pacientes buscam profissionais e enviam propostas.
➡️ Profissionais aceitam e realizam o atendimento presencial.

## 💻 Tecnologias Utilizadas
- Python 3.11
- Flask
- SQLAlchemy
- PostgreSQL
- JavaScript
- HTML/CSS

## 📁 Estrutura de Diretórios
saude-connect/
├── src/
│   ├── models/
│   │   ├── user.py
│   │   ├── patient.py
│   │   ├── professional.py
│   │   └── professional_activity.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── patient.py
│   │   ├── professional.py
│   │   └── professional_activity.py
│   └── main.py
├── static/
│   ├── js/
│   │   └── activities.js
│   └── activities.html
├── tests/
│   └── test_professional_activity.py
└── README.md

## ⚙️ Como rodar o backend
1. Instale as dependências:
   pip install -r requirements.txt
2. Configure a variável de ambiente:
   DATABASE_URL=postgresql://<user>:<password>@<host>:<port>/<dbname>
3. Inicie o servidor:
   flask run

## 🌐 Como rodar o frontend
Abra o arquivo:
static/activities.html

## ✅ Como rodar os testes
1. Instale o pytest:
   pip install pytest pytest-flask
2. Execute:
   pytest tests/

## 🔮 Funcionalidades
✅ Cadastro de profissionais e pacientes
✅ Profissional pode cadastrar várias atividades
✅ Paciente pode buscar atividades
✅ Sistema de propostas
✅ CRUD completo para atividades
✅ Testes automatizados

## 📜 Licença
Este projeto está licenciado sob a Licença MIT.

## ✍️ Autor
Desenvolvido por: Andrey

## 🚀 Contribuições
Pull requests são bem-vindos!
