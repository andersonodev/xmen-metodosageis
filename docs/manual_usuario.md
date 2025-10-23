# Manual de Uso — Xmen AgileTeam

Este manual orienta líderes, colaboradores e administradores a navegar pelas principais telas do Xmen AgileTeam. Incluímos fluxos passo a passo, indicações de campos e sugestões de captura de tela para que a equipe de design complemente o documento com imagens oficiais.

> ℹ️ **Política do repositório:** arquivos binários (PNG, JPG, PDF, etc.) não são versionados. Utilize um armazenamento externo ou anexe as imagens ao criar releases.

> 💡 **Como adicionar capturas:** execute a aplicação localmente, acesse cada tela listada e salve a imagem na pasta `docs/imagens/` (fora do controle de versão) ou em um repositório compartilhado. Atualize os caminhos das figuras conforme necessário quando distribuir o manual.

## 1. Acesso Seguro

### 1.1 Login
1. Abra `/accounts/login/`.
2. Informe e-mail ou usuário e senha.
3. Opcional: clique em **Entrar com Google** ou **Entrar com GitHub** para simular OAuth.
4. Finalize com **Entrar** — usuários não verificados receberão orientação para confirmar o e-mail.

> Captura sugerida: `![Tela de login](imagens/login.png)`

### 1.2 Recuperação e Verificação de Conta
- A página exibe atalho para recuperação de senha.
- Usuários recém-registrados veem aviso de verificação e botão para reenviar token de e-mail.

## 2. Cadastro de Colaboradores

### 2.1 Formulário de Registro
1. Acesse `/accounts/register/`.
2. Preencha **Nome**, **Sobrenome**, **E-mail**, **Senha** e confirme a senha.
3. Defina a **Descrição do Perfil** e selecione a **Data de Início** (obrigatória) e **Data de Fim** (opcional) para o projeto atual.
4. Escolha o **Papel** (Líder ou Colaborador) e aceite os termos.
5. Envie e aguarde o token de confirmação enviado por e-mail.

> Captura sugerida: `![Formulário de registro](imagens/registro.png)`

### 2.2 Fluxo de Confirmação de E-mail
- Ao registrar, o sistema gera token temporário; a tela de confirmação em `/accounts/verify-email/<token>/` valida o acesso.
- Usuários confirmados são redirecionados ao dashboard correspondente ao papel.

## 3. Perfil do Colaborador

### 3.1 Visualização Rápida
- `/accounts/profile/` mostra resumo de habilidades, projetos ativos e eventos de segurança.
- Botões principais: **Editar Perfil**, **Ver Perfil Completo**, **Atualizar Competências**.

### 3.2 Perfil Completo
1. Abra `/accounts/profile/full/` para visualizar histórico completo.
2. A tela exibe habilidades técnicas e comportamentais, projetos anteriores e equipes atuais.
3. Use os filtros laterais para destacar competências ou buscar por projetos específicos.

> Capturas sugeridas:
> - `![Perfil resumido](imagens/perfil-resumo.png)`
> - `![Perfil completo](imagens/perfil-completo.png)`

### 3.3 Edição de Competências
1. Em **Editar Competências**, utilize os campos do tipo *tag* para adicionar habilidades técnicas.
2. Defina nível de proficiência (0–5) e destaque competências comportamentais no seletor dedicado.
3. Salve as alterações e acompanhe o feedback imediato no painel lateral.

## 4. Gestão de Projetos

### 4.1 Criação de Projetos
1. Acesse `/projects/create/`.
2. Informe **Nome do Projeto**, **Descrição**, **Datas de Início/Fim**, **Objetivos (OKRs)** e **Habilidades Requeridas**.
3. Utilize o seletor de requisitos para ranquear competências.
4. Salve como rascunho ou publique imediatamente.

### 4.2 Visualização de Projetos Ativos
- `/projects/active/` apresenta cards com status, equipe e progresso.
- Cada card linka para métricas específicas e histórico de sprints.

> Capturas sugeridas:
> - `![Lista de projetos](imagens/projetos-ativos.png)`
> - `![Formulário de projeto](imagens/projeto-form.png)`

## 5. Busca e Composição de Equipes

### 5.1 Busca por Colaboradores
1. Navegue até `/accounts/collaborators/search/`.
2. Filtre por competência, senioridade e disponibilidade.
3. Reordene resultados por afinidade, proficiência ou última participação em projeto.

### 5.2 Rascunho de Equipes
1. Em `/teams/drafts/`, crie um novo rascunho.
2. Adicione colaboradores usando o seletor inteligente de skills.
3. Salve como rascunho para continuar depois ou finalize para promover a equipe a projeto ativo.

> Capturas sugeridas:
> - `![Busca de colaboradores](imagens/busca-colaboradores.png)`
> - `![Rascunho de equipe](imagens/rascunho-equipe.png)`

## 6. Importação em Massa

1. Acesse `/accounts/import/`.
2. Faça upload do arquivo CSV/Excel com colunas `name`, `email`, `role`, `skills`.
3. O pré-validador aponta linhas com erros e permite download do relatório de inconsistências.
4. Ao confirmar, o sistema envia e-mails de boas-vindas com instruções de primeiro acesso.

> Captura sugerida: `![Importação em massa](imagens/importacao.png)`

## 7. Dashboards e Relatórios

### 7.1 Dashboard Principal
- `/dashboards/` reúne gráficos de alocação, velocidade de sprint e distribuição de competências (renderizados via Chart.js).
- Interações chave: aplicar filtros de período, exportar dados em CSV e gerar relatórios PDF.

### 7.2 Geração de Relatórios
1. Abra `/projects/report-generator/`.
2. Selecione filtros (projeto, sprint, intervalo de datas) e métricas desejadas.
3. Clique em **Gerar Relatório** para visualizar gráficos e resumo textual.

## 8. Administração e Permissões

1. `/accounts/users/manage/` lista todos os usuários com papéis "Líder" ou "Colaborador".
2. Utilize os menus suspensos para atualizar permissões e ativar/desativar contas.
3. O log de eventos registra alterações críticas e é exibido na mesma tela.

## 9. Boas Práticas de Segurança

- Tokens JWT expiram automaticamente; utilize o endpoint `/api/auth/refresh/` para renovar.
- Dados sensíveis (biografias, notas internas) são criptografados via `apps.accounts.encryption`.
- Habilite HTTPS em produção e configure variáveis `FERNET_KEY` e `DJANGO_SECRET_KEY` no ambiente.

## 10. Testes Recomendados

| Cenário | Comando |
| --- | --- |
| Suite completa | `pytest` |
| Autenticação | `pytest tests/test_accounts.py -v` |
| Checks Django | `python manage.py check` |

Execute os testes antes de cada deploy para garantir a estabilidade das integrações e fluxos críticos.

---

Para dúvidas adicionais, consulte `docs/README_RAPIDO.md` ou abra uma issue no repositório.
