# Guia Rápido das Novas Funcionalidades

## Fluxos aprimorados

- **Login e registro** com confirmação de e-mail simulada e tokens JWT.
- **Editor de competências** em `Skills ▸ Editar` com seleção por categoria.
- **Perfil completo** em `Perfil ▸ Ver completo` mostrando projetos e histórico.
- **Busca de colaboradores** em `Colaboradores ▸ Busca` filtrando por habilidades e nível.
- **Rascunhos de equipes** em `Times ▸ Rascunhos` para salvar composições antes da criação.
- **Importação em massa** em `Colaboradores ▸ Importar` para CSV/XLSX com feedback.
- **Gerenciamento de permissões** em `Colaboradores ▸ Gerenciar` permitindo trocar papéis.
- **Dashboard** atualizado com gráficos de status de projetos e distribuição de skills.

## APIs relevantes

- `POST /accounts/api/auth/register/` — Cria usuários e retorna tokens.
- `POST /accounts/api/auth/login/` — Autentica e entrega JWT.
- `GET /accounts/api/collaborators/search/` — Busca colaboradores via querystring.
- `GET /accounts/api/hr/sync/` — Payload consolidado para integração com RH.

## Dicas

- Use o módulo de relatórios (`/projects/relatorios/`) para gerar prévias filtradas.
- Os gráficos do dashboard usam Chart.js e se atualizam com base nos dados atuais.
- A importação aceita cabeçalhos `username`, `email`, `first_name`, `last_name`, `role` e `password`.
