# Documentação do Sistema Saúde Connect

## Visão Geral
O Saúde Connect é uma plataforma web que conecta profissionais de saúde freelancers com pacientes. O sistema permite que profissionais cadastrem seus serviços e especialidades, passando por um processo de aprovação administrativa, enquanto pacientes podem se cadastrar e buscar profissionais de acordo com suas necessidades específicas.

## Funcionalidades Principais

### Para Profissionais de Saúde
- Cadastro com envio de diploma para verificação
- Cadastro de múltiplas atividades/especialidades
- Perfil profissional com biografia e experiência
- Status de aprovação (pendente, aprovado, rejeitado)

### Para Pacientes
- Cadastro simplificado
- Busca de profissionais por especialidade/atividade
- Visualização de perfis profissionais aprovados

### Para Administradores
- Painel administrativo para aprovação de profissionais
- Visualização de diplomas enviados
- Aprovação ou rejeição de cadastros
- Gerenciamento de atividades/especialidades

## Estrutura do Projeto

```
saude-connect/
├── venv/                  # Ambiente virtual Python
├── src/                   # Código-fonte da aplicação
│   ├── models/            # Modelos de dados
│   │   ├── user.py        # Modelo de usuário base
│   │   ├── professional.py # Modelo de profissional e atividades
│   │   └── patient.py     # Modelo de paciente
│   ├── routes/            # Rotas da API
│   │   ├── user.py        # Autenticação e perfil
│   │   ├── auth.py        # Cadastro de profissionais
│   │   ├── patient.py     # Cadastro de pacientes
│   │   ├── admin.py       # Painel administrativo
│   │   └── search.py      # Busca de profissionais
│   ├── static/            # Arquivos estáticos (frontend)
│   │   ├── uploads/       # Diretório para upload de diplomas
│   │   └── index.html     # Página inicial
│   └── main.py            # Ponto de entrada da aplicação
└── requirements.txt       # Dependências do projeto
```

## Fluxos Principais

### Cadastro de Profissional
1. O profissional preenche o formulário de cadastro
2. Envia seus dados pessoais, diploma e especialidades
3. O sistema armazena os dados e marca o status como "pendente"
4. Um administrador revisa o cadastro e aprova ou rejeita
5. O profissional recebe notificação do resultado

### Cadastro de Paciente
1. O paciente preenche o formulário de cadastro
2. Envia seus dados pessoais
3. O cadastro é aprovado automaticamente

### Busca de Profissionais
1. O paciente acessa a plataforma
2. Filtra profissionais por especialidade ou categoria
3. Visualiza a lista de profissionais aprovados
4. Acessa o perfil detalhado do profissional escolhido

## API Endpoints

### Autenticação
- `POST /api/user/login` - Login de usuário
- `GET /api/user/profile` - Obter perfil do usuário logado

### Cadastro
- `POST /api/auth/register/professional` - Cadastro de profissional
- `POST /api/patient/register` - Cadastro de paciente
- `GET /api/auth/activities` - Listar atividades disponíveis

### Administração
- `GET /api/admin/professionals/pending` - Listar profissionais pendentes
- `POST /api/admin/professionals/{id}/approve` - Aprovar profissional
- `POST /api/admin/professionals/{id}/reject` - Rejeitar profissional
- `GET /api/admin/professionals/{id}/diploma` - Visualizar diploma
- `GET /api/admin/activities` - Listar todas as atividades
- `POST /api/admin/activities` - Criar nova atividade

### Busca
- `GET /api/search/professionals` - Buscar profissionais por atividade/categoria
- `GET /api/search/activities/categories` - Listar categorias de atividades

## Credenciais de Acesso

### Administrador
- Email: admin@saudeconnect.com
- Senha: admin123

## Instruções para Teste

1. Acesse a URL fornecida
2. Teste o cadastro de profissionais (com upload de diploma)
3. Teste o cadastro de pacientes
4. Faça login como administrador para aprovar profissionais
5. Teste a busca de profissionais por especialidade
6. Verifique se apenas profissionais aprovados aparecem nas buscas

## Próximos Passos e Melhorias Futuras

- Implementação de sistema de mensagens entre pacientes e profissionais
- Agendamento de consultas e serviços
- Sistema de avaliações e comentários
- Integração com meios de pagamento
- Aplicativo móvel para Android e iOS
