# Mapeamento de Funcionalidades - Saúde Connect

## 1. Funcionalidades Essenciais

### 1.1 Cadastro e Autenticação
- **Pacientes e Profissionais**
  - Sistema de cadastro separado para cada tipo de usuário
  - Autenticação via email/senha com JWT
  - Recuperação de senha

- **Verificação de Profissionais**
  - Upload de documentos (diplomas)
  - Fluxo de aprovação por administrador
  - Notificações de status de aprovação

### 1.2 Perfis Detalhados
- **Profissionais**
  - Foto profissional (upload e gerenciamento)
  - Descrição pessoal (bio)
  - Áreas de atuação (limitadas a 3)
  - Serviços oferecidos (com preços e descrições)
  - Experiência e formação
  - Sistema de avaliações

### 1.3 Busca e Filtros Avançados
- **Busca de Profissionais**
  - Por tipo de serviço
  - Por localização
  - Por disponibilidade
  - Por avaliações
  - Ordenação por relevância/preço/avaliação

### 1.4 Sistema de Agendamento e Pagamento
- **Agendamento**
  - Seleção de data/hora
  - Confirmação pelo profissional
  - Cancelamento e reagendamento

- **Pagamento**
  - Integração com gateway de pagamento
  - Histórico de transações
  - Comprovantes

### 1.5 Avaliações e Feedback
- **Sistema de Avaliação**
  - Avaliação por estrelas (1-5)
  - Comentários
  - Moderação de avaliações

### 1.6 Painel Administrativo
- **Gerenciamento**
  - Aprovação de cadastros
  - Gerenciamento de categorias
  - Monitoramento de transações
  - Relatórios e estatísticas

## 2. Painéis de Usuário

### 2.1 Painel do Profissional de Saúde
- **Perfil Profissional**
  - Informações pessoais
  - Documentação e certificados
  - Biografia

- **Gerenciamento de Atividades**
  - Adicionar atividades (até 3)
  - Editar/remover atividades
  - Status de aprovação

- **Histórico de Atendimentos**
  - Lista de atendimentos
  - Avaliações recebidas

- **Notificações e Mensagens**
  - Alertas de novas solicitações
  - Sistema de mensagens diretas

- **Configurações da Conta**
  - Atualização de dados
  - Preferências
  - Desativação de conta

### 2.2 Painel do Administrador
- **Gerenciamento de Profissionais**
  - Aprovação de cadastros
  - Monitoramento de atividades

- **Gerenciamento de Pacientes**
  - Visualização de cadastros
  - Histórico de atendimentos

- **Relatórios e Estatísticas**
  - Atendimentos realizados
  - Avaliações
  - Atividades populares

## 3. Requisitos Técnicos

### 3.1 Backend
- **API RESTful**
  - Endpoints para todas as funcionalidades
  - Autenticação JWT
  - Validação de dados

- **Banco de Dados**
  - Modelos para usuários, profissionais, pacientes, atividades, agendamentos
  - Relacionamentos e integridade referencial

- **Segurança**
  - Proteção contra injeção SQL
  - Validação de entrada
  - Controle de acesso baseado em papéis

### 3.2 Frontend
- **Interface Responsiva**
  - Design mobile-first
  - Compatibilidade com diferentes dispositivos

- **Componentes React com Shadcn/ui**
  - Estilo consistente com Upwork
  - Componentes reutilizáveis
  - Formulários com validação

- **Experiência do Usuário**
  - Feedback visual para ações
  - Carregamento assíncrono
  - Tratamento de erros amigável

## 4. Priorização de Desenvolvimento

### Fase 1: Funcionalidades Críticas
1. Correção de erros de cadastro e login
2. Implementação do fluxo básico de aprovação de profissionais
3. Busca e listagem de profissionais

### Fase 2: Funcionalidades Essenciais
1. Sistema de agendamento
2. Perfis detalhados
3. Avaliações e feedback

### Fase 3: Melhorias e Refinamentos
1. Painel administrativo completo
2. Relatórios e estatísticas
3. Melhorias de UX/UI

## 5. Arquitetura do Sistema

### 5.1 Estrutura de Diretórios
```
saude-connect/
├── src/
│   ├── models/         # Modelos de dados
│   ├── routes/         # Endpoints da API
│   ├── static/         # Arquivos estáticos (atual)
│   ├── react-frontend/ # Novo frontend React
│   └── main.py         # Ponto de entrada da aplicação
└── docs/              # Documentação
```

### 5.2 Fluxo de Dados
1. Cliente faz requisição → API processa → Banco de dados → Resposta ao cliente
2. Autenticação: Login → JWT → Autorização para rotas protegidas
3. Cadastro: Formulário → Validação → Persistência → Confirmação

### 5.3 Integrações
1. Gateway de pagamento
2. Serviço de upload de arquivos
3. Sistema de notificações
