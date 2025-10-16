# 🚀 Deploy no Heroku - Guia Completo

## 📋 Pré-requisitos

1. **Conta no Heroku**: https://signup.heroku.com/
2. **Heroku CLI instalada**: https://devcenter.heroku.com/articles/heroku-cli
3. **Git instalado e configurado**

## 🛠️ Preparação (JÁ FEITO)

✅ **Arquivos criados/atualizados:**
- `Procfile` - Comandos para executar no Heroku
- `requirements.txt` - Dependências Python otimizadas
- `runtime.txt` - Versão do Python (3.11.7)
- `settings.py` - Configurado para produção
- `.env.example` - Exemplo de variáveis de ambiente

## 🚀 Passo a Passo para Deploy

### 1. Login no Heroku
```bash
heroku login
```

### 2. Criar o App no Heroku
```bash
# Substitua "xmen-agileteam" pelo nome desejado (deve ser único)
heroku create xmen-agileteam

# Ou deixe o Heroku escolher um nome aleatório
heroku create
```

### 3. Configurar Variáveis de Ambiente
```bash
# Gerar uma SECRET_KEY segura
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Configurar no Heroku (substitua pela chave gerada acima)
heroku config:set SECRET_KEY="sua-chave-super-secreta-gerada"
heroku config:set DEBUG=False
```

### 4. Adicionar Add-ons GRATUITOS
```bash
# PostgreSQL gratuito (Hobby Dev - até 10k rows)
heroku addons:create heroku-postgresql:mini

# Redis gratuito (Hobby Dev - até 25MB)  
heroku addons:create heroku-redis:mini
```

### 5. Deploy do Código
```bash
# Adicionar e commitar arquivos
git add .
git commit -m "Configuração para deploy no Heroku"

# Fazer o deploy
git push heroku main
```

### 6. Executar Migrações
```bash
# Criar as tabelas no PostgreSQL
heroku run python manage.py migrate

# Criar superusuário
heroku run python manage.py createsuperuser

# Criar usuários de teste
heroku run python manage.py shell < create_test_users.py
```

### 7. Coletar Arquivos Estáticos
```bash
heroku run python manage.py collectstatic --noinput
```

## 🌐 Acessar a Aplicação

```bash
# Abrir no navegador
heroku open

# Ver logs em tempo real
heroku logs --tail

# Acessar shell do Django
heroku run python manage.py shell
```

## 🔐 Acesso Admin Especial

Para acessar o painel administrativo em produção:
```
https://seu-app.herokuapp.com/accounts/xmen-admin-special/?token=admin_access_xmen_2024
```

## 📊 Monitoramento

```bash
# Status do app
heroku ps

# Configurações
heroku config

# Logs
heroku logs --tail

# Executar comandos
heroku run python manage.py <comando>
```

## 💰 Recursos Gratuitos do Heroku

- **Dyno**: 550-1000 horas/mês (grátis)
- **PostgreSQL Mini**: Até 10k rows
- **Redis Mini**: Até 25MB de memória
- **Bandwidth**: Ilimitado

## 🔧 Comandos Úteis

```bash
# Reiniciar o app
heroku restart

# Escalar dynos (0 = desligar, 1 = ligar)
heroku ps:scale web=1
heroku ps:scale worker=0  # Worker do Celery (opcional)

# Backup do banco
heroku pg:backups:capture
heroku pg:backups:download

# Conectar ao PostgreSQL
heroku pg:psql
```

## ⚠️ Importante

1. **Sleep Mode**: Apps gratuitos "dormem" após 30min de inatividade
2. **Limitações**: 550-1000h/mês de execução
3. **Domínio**: Será `https://nome-do-app.herokuapp.com`
4. **SSL**: HTTPS é automático
5. **Backups**: Configure backups regulares do PostgreSQL

## 🐛 Solução de Problemas

```bash
# Ver erros detalhados
heroku logs --tail

# Verificar status
heroku ps:scale

# Reiniciar se necessário
heroku restart

# Verificar configuração do banco
heroku config | grep DATABASE_URL

# Verificar Redis
heroku config | grep REDIS_URL
```

## 🔄 Updates Futuros

Para atualizar o app após mudanças no código:
```bash
git add .
git commit -m "Nova funcionalidade"
git push heroku main
```

## 📞 Suporte

- **Heroku Dev Center**: https://devcenter.heroku.com/
- **Status do Heroku**: https://status.heroku.com/
- **Comunidade**: https://help.heroku.com/

---

🎉 **Pronto!** Sua aplicação Django estará rodando no Heroku com recursos totalmente gratuitos!