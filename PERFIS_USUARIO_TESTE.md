# Perfis de Usuário para Teste

Este arquivo contém os perfis de usuário criados para teste do sistema. Todos os usuários têm nome de usuário e senha iguais.

## 🔐 Credenciais de Acesso

### Administrador
- **Username:** `admin`
- **Senha:** `admin`
- **Email:** `admin@sistemaagil.com`
- **Tipo:** Administrador
- **Descrição:** Acesso total ao sistema, pode gerenciar todos os usuários, projetos e configurações.

### Líder de Projeto
- **Username:** `lider`
- **Senha:** `lider`
- **Email:** `lider@sistemaagil.com`
- **Tipo:** Líder
- **Descrição:** Pode criar e gerenciar projetos, atribuir tarefas e gerenciar equipes.

### Colaborador/Desenvolvedor
- **Username:** `colaborador`
- **Senha:** `colaborador`
- **Email:** `colaborador@sistemaagil.com`
- **Tipo:** Colaborador
- **Descrição:** Pode executar tarefas atribuídas, atualizar status e colaborar em projetos.

### Product Owner
- **Username:** `product_owner`
- **Senha:** `product_owner`
- **Email:** `product.owner@sistemaagil.com`
- **Tipo:** Product Owner
- **Descrição:** Define requisitos do produto, prioriza backlog e valida entregas.

### Scrum Master
- **Username:** `scrum_master`
- **Senha:** `scrum_master`
- **Email:** `scrum.master@sistemaagil.com`
- **Tipo:** Scrum Master
- **Descrição:** Facilita processos ágeis, remove impedimentos e coordena cerimônias.

### Designer
- **Username:** `designer`
- **Senha:** `designer`
- **Email:** `designer@sistemaagil.com`
- **Tipo:** Designer
- **Descrição:** Responsável por UX/UI, prototipagem e design de interfaces.

### QA/Tester
- **Username:** `qa_tester`
- **Senha:** `qa_tester`
- **Email:** `qa.tester@sistemaagil.com`
- **Tipo:** QA/Tester
- **Descrição:** Executa testes, reporta bugs e garante qualidade do produto.

### DevOps
- **Username:** `devops`
- **Senha:** `devops`
- **Email:** `devops@sistemaagil.com`
- **Tipo:** DevOps
- **Descrição:** Gerencia infraestrutura, CI/CD e automação de processos.

### Analista
- **Username:** `analista`
- **Senha:** `analista`
- **Email:** `analista@sistemaagil.com`
- **Tipo:** Analista
- **Descrição:** Analisa requisitos, documenta processos e apoia na definição de soluções.

## 📊 Resumo dos Perfis

| Username      | Senha         | Tipo          | Role Principal        |
|---------------|---------------|---------------|-----------------------|
| admin         | admin         | Administrador | Gestão completa       |
| lider         | lider         | Líder         | Gestão de projetos    |
| colaborador   | colaborador   | Colaborador   | Execução de tarefas   |
| product_owner | product_owner | Product Owner | Definição de produto  |
| scrum_master  | scrum_master  | Scrum Master  | Facilitação ágil      |
| designer      | designer      | Designer      | UX/UI Design          |
| qa_tester     | qa_tester     | QA/Tester     | Qualidade e testes    |
| devops        | devops        | DevOps        | Infraestrutura        |
| analista      | analista      | Analista      | Análise de requisitos |

## 🚀 Como Usar

1. Acesse o sistema através da URL de login
2. Use qualquer um dos usernames acima
3. Digite a mesma palavra como senha
4. Explore as funcionalidades de acordo com o perfil

## 🔧 Comandos Django para Criar os Usuários

```python
# Executar no Django shell: python manage.py shell

from django.contrib.auth import get_user_model
from apps.accounts.models import UserProfile

User = get_user_model()

# Criar os usuários
usuarios = [
    {'username': 'admin', 'email': 'admin@sistemaagil.com', 'first_name': 'Admin', 'is_staff': True, 'is_superuser': True},
    {'username': 'lider', 'email': 'lider@sistemaagil.com', 'first_name': 'Líder'},
    {'username': 'colaborador', 'email': 'colaborador@sistemaagil.com', 'first_name': 'Colaborador'},
    {'username': 'product_owner', 'email': 'product.owner@sistemaagil.com', 'first_name': 'Product Owner'},
    {'username': 'scrum_master', 'email': 'scrum.master@sistemaagil.com', 'first_name': 'Scrum Master'},
    {'username': 'designer', 'email': 'designer@sistemaagil.com', 'first_name': 'Designer'},
    {'username': 'qa_tester', 'email': 'qa.tester@sistemaagil.com', 'first_name': 'QA Tester'},
    {'username': 'devops', 'email': 'devops@sistemaagil.com', 'first_name': 'DevOps'},
    {'username': 'analista', 'email': 'analista@sistemaagil.com', 'first_name': 'Analista'}
]

for usuario_data in usuarios:
    user, created = User.objects.get_or_create(
        username=usuario_data['username'],
        defaults={
            'email': usuario_data['email'],
            'first_name': usuario_data['first_name'],
            'is_staff': usuario_data.get('is_staff', False),
            'is_superuser': usuario_data.get('is_superuser', False)
        }
    )
    if created:
        user.set_password(usuario_data['username'])  # Senha igual ao username
        user.save()
        print(f"Usuário {usuario_data['username']} criado com sucesso!")
    else:
        print(f"Usuário {usuario_data['username']} já existe.")
```

## 📝 Notas Importantes

- **Ambiente de Teste:** Estas credenciais são apenas para ambiente de teste
- **Segurança:** Em produção, sempre use senhas seguras e únicas
- **Perfis:** Cada usuário pode ter roles diferentes em equipes diferentes
- **Flexibilidade:** O sistema permite que um usuário tenha múltiplos papéis

## 🔄 Próximos Passos

Após criar os usuários:
1. Teste o login com cada perfil
2. Crie equipes e atribua usuários
3. Crie projetos e atribua equipes
4. Teste as funcionalidades específicas de cada role
5. Verifique permissões e acessos

---
*Arquivo gerado automaticamente para facilitar os testes do Sistema Ágil*