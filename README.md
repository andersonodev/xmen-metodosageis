# 🦾 Xmen-AgileTeam

Sistema completo para automação de formação de equipes ágeis usando Django + AI.

## 📋 Índice

- [Características](#características)
- [Tecnologias](#tecnologias)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Instalação Rápida](#instalação-rápida)
- [Desenvolvimento](#desenvolvimento)
- [API Documentation](#api-documentation)
- [Deploy](#deploy)
- [Testes](#testes)
- [Contribuição](#contribuição)

## 🚀 Características

### ⚡ Principais Funcionalidades
- **Autenticação JWT** com roles (Líder/Colaborador)
- **Gestão de Habilidades** com categorias e níveis de proficiência
- **Formação Inteligente de Equipes** com IA
- **Kanban Boards** em tempo real
- **Chat em Tempo Real** por projeto
- **Métricas e Dashboards** automatizados
- **Sistema de Notificações** personalizável
- **Gestão de Sprints e OKRs**
- **Integrações Externas** (CSV, APIs)

### 🤖 IA e Automação
- Recomendação automática de membros para equipes
- Análise de risco de atrasos em projetos
- Sugestão de papéis Scrum baseada em habilidades
- Métricas automatizadas de performance

### 🔄 Tempo Real
- Chat por projeto via WebSockets
- Atualizações de board em tempo real
- Notificações instantâneas
- Status de presença de usuários

## 🛠 Tecnologias

### Backend
- **Django 5.1** - Framework web
- **Django REST Framework** - API REST
- **Django Channels** - WebSockets
- **Celery** - Tasks assíncronas
- **Redis** - Cache e message broker
- **SQLite** - Banco de dados (dev)
- **JWT** - Autenticação

### Frontend Ready
- **WebSockets** para real-time
- **REST API** completa
- **Swagger/OpenAPI** docs
- **CORS** configurado

### DevOps
- **Docker** + **Docker Compose**
- **pytest** para testes
- **Coverage** reports
- **GitHub Actions** ready

## 📁 Estrutura do Projeto

```
xmen/
├── 📁 apps/                    # Aplicações Django modulares
│   ├── 📁 accounts/           # Autenticação e usuários
│   ├── 📁 skills/             # Gestão de habilidades
│   ├── 📁 teams/              # Formação de equipes
│   ├── 📁 projects/           # Gestão de projetos
│   ├── 📁 tasks/              # Kanban e tarefas
│   ├── 📁 dashboards/         # Métricas e relatórios
│   ├── 📁 notifications/      # Sistema de notificações
│   ├── 📁 chat/               # Chat em tempo real
│   ├── 📁 recommendations/    # IA e recomendações
│   └── 📁 integrations/       # Integrações externas
├── 📁 xmen_agile_team/        # Configurações do projeto
├── 📁 tests/                  # Testes automatizados
├── 📁 docker/                 # Configurações Docker
├── 🐳 docker-compose.yml      # Orquestração de containers
├── 📋 requirements.txt        # Dependências Python
├── 🔧 Makefile               # Comandos de desenvolvimento
└── 🚀 setup.sh               # Script de inicialização
```

## ⚡ Instalação Rápida

### Opção 1: Script Automático (Recomendado)
```bash
# Clone o repositório
git clone <seu-repositorio>
cd xmen

# Execute o script de setup
./setup.sh
```

### Opção 2: Docker (Mais Rápido)
```bash
# Subir toda a aplicação
make quick-start

# Ou manualmente
docker-compose up --build
```

### Opção 3: Manual
```bash
# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Configurar banco
python manage.py migrate

# Povoar com dados de exemplo
python manage.py seed_data

# Executar servidor
python manage.py runserver
```

## 🔧 Desenvolvimento

### Comandos Úteis (Makefile)
```bash
make help              # Ver todos os comandos
make dev-setup         # Setup completo para desenvolvimento
make quick-start       # Iniciar com Docker
make run               # Executar servidor local
make test              # Executar testes
make test-cov          # Testes com coverage
make lint              # Verificar código
make migrate           # Aplicar migrations
make seed              # Povoar dados de exemplo
make clean             # Limpar cache e arquivos temporários
```

### Executar Serviços em Desenvolvimento
```bash
# Terminal 1: Django server
python manage.py runserver

# Terminal 2: Celery worker
celery -A xmen_agile_team worker -l info

# Terminal 3: Celery beat (agendamento)
celery -A xmen_agile_team beat -l info

# Terminal 4: Redis (se local)
redis-server
```

## 📚 API Documentation

### Acessar Documentação
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

### Principais Endpoints

#### Autenticação
```
POST /api/auth/register/     # Registrar usuário
POST /api/auth/login/        # Login
POST /api/auth/refresh/      # Renovar token
POST /api/auth/logout/       # Logout
```

#### Habilidades
```
GET/POST    /api/skills/categories/  # Categorias de habilidades
GET/POST    /api/skills/             # Habilidades
GET/POST    /api/skills/user-skills/ # Habilidades do usuário
```

#### Equipes
```
GET/POST    /api/teams/                    # Equipes
POST        /api/teams/{id}/invite/        # Convidar membro
POST        /api/teams/{id}/join/          # Entrar na equipe
```

#### Projetos
```
GET/POST    /api/projects/                 # Projetos
GET/POST    /api/projects/{id}/sprints/    # Sprints
GET/POST    /api/projects/{id}/okrs/       # OKRs
```

#### Tarefas (Kanban)
```
GET/POST    /api/tasks/boards/             # Boards
GET/POST    /api/tasks/columns/            # Colunas
GET/POST    /api/tasks/tasks/              # Tarefas
POST        /api/tasks/tasks/{id}/move/    # Mover tarefa
```

#### Recomendações (IA)
```
POST /api/recommendations/team-allocation/      # Recomendar equipe
POST /api/recommendations/delay-risk/           # Analisar risco
POST /api/recommendations/scrum-roles/          # Sugerir papéis
```

## 🐳 Deploy

### Docker Compose (Produção)
```bash
# Configurar ambiente
cp .env.example .env
# Editar .env com configurações de produção

# Subir aplicação
docker-compose -f docker-compose.prod.yml up -d

# Ver logs
docker-compose logs -f
```

### Configurações de Produção
```env
# .env
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgres://user:pass@db:5432/dbname
REDIS_URL=redis://redis:6379/0
```

## 🧪 Testes

### Executar Testes
```bash
# Todos os testes
make test

# Com coverage
make test-cov

# Testes específicos
pytest tests/test_accounts.py -v

# Testes de integração
pytest tests/integration/ -v
```

### Estrutura de Testes
```
tests/
├── test_accounts.py           # Testes de autenticação
├── test_skills.py             # Testes de habilidades
├── test_teams.py              # Testes de equipes
├── test_projects.py           # Testes de projetos
├── test_tasks.py              # Testes de kanban
├── test_recommendations.py    # Testes de IA
├── integration/               # Testes de integração
└── fixtures/                  # Dados de teste
```

## 🔌 WebSockets

### Chat em Tempo Real
```javascript
// Frontend example
const chatSocket = new WebSocket(
    'ws://localhost:8000/ws/chat/project-1/'
);

chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    console.log('Mensagem recebida:', data.message);
};

// Enviar mensagem
chatSocket.send(JSON.stringify({
    'message': 'Olá equipe!',
    'type': 'chat_message'
}));
```

### Board Updates
```javascript
// Atualizações do board
const boardSocket = new WebSocket(
    'ws://localhost:8000/ws/board/project-1/'
);

boardSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    if (data.type === 'task_moved') {
        // Atualizar posição da tarefa
        updateTaskPosition(data.task_id, data.new_column);
    }
};
```

## 🤖 Sistema de IA

### Recomendação de Equipes
O sistema analisa:
- Habilidades necessárias vs disponíveis
- Experiência dos membros
- Histórico de colaboração
- Carga de trabalho atual

### Análise de Riscos
Fatores considerados:
- Progresso vs timeline
- Complexidade das tarefas
- Disponibilidade da equipe
- Histórico de projetos similares

## 📊 Métricas e Dashboards

### Métricas Automatizadas
- **Velocity da equipe**
- **Burndown charts**
- **Tempo médio por tarefa**
- **Taxa de conclusão de sprints**
- **Distribuição de habilidades**

### Dashboards Disponíveis
- Dashboard de projeto
- Métricas de equipe
- Relatórios de performance
- Análise de skills gap

## 🛡️ Segurança

### Implementado
- ✅ Autenticação JWT
- ✅ Autorização baseada em roles
- ✅ Validação de dados
- ✅ Rate limiting (Redis)
- ✅ CORS configurado
- ✅ SQL injection protection (Django ORM)

### Recomendações
- Configurar HTTPS em produção
- Implementar 2FA (opcional)
- Monitoramento de logs
- Backup automático do banco

## 🔄 Integrações

### Implementadas
- ✅ Import CSV de usuários/skills
- ✅ Webhook para notificações
- ✅ API REST completa

### Roadmap
- [ ] Slack integration
- [ ] Jira sync
- [ ] GitHub integration
- [ ] Trello import

## 🚀 Performance

### Otimizações
- Caching com Redis
- Database indexing
- Paginação automática
- Query optimization
- Background tasks com Celery

### Monitoramento
```bash
# Flower (Celery monitor)
http://localhost:5555

# Django Debug Toolbar (dev)
# Habilitado automaticamente em DEBUG=True
```

## 🤝 Contribuição

### Setup de Desenvolvimento
```bash
# Fork e clone o projeto
git clone your-fork-url
cd xmen

# Setup do ambiente
./setup.sh

# Instalar hooks pre-commit
pre-commit install

# Criar branch para feature
git checkout -b feature/nova-funcionalidade
```

### Padrões
- **Commits**: Use conventional commits
- **Código**: Siga PEP 8
- **Testes**: Mantenha coverage > 80%
- **Docs**: Documente novas features

## 📜 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🆘 Suporte

### FAQ
**Q: Como resetar o banco de dados?**
```bash
rm db.sqlite3
python manage.py migrate
python manage.py seed_data
```

**Q: Como adicionar uma nova skill category?**
```bash
python manage.py shell
>>> from apps.skills.models import SkillCategory
>>> SkillCategory.objects.create(name="Nova Categoria", description="Descrição")
```

**Q: Como configurar em produção?**
- Use PostgreSQL ao invés de SQLite
- Configure Redis externo
- Use servidor web (nginx + gunicorn)
- Configure variáveis de ambiente

### Contato
- 📧 Email: seu-email@exemplo.com
- 💬 Discord: Seu Discord
- 🐛 Issues: [GitHub Issues](link-para-issues)

---

**Feito com ❤️ para automatizar formação de equipes ágeis** 🦾