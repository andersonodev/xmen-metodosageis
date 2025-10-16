# 🔐 Acesso Admin - Instruções Especiais

## 🚫 Rota Admin Removida
A rota `/accounts/admin-dashboard/` foi **COMPLETAMENTE REMOVIDA** das URLs públicas por questões de segurança.

## 🔑 Nova Rota Especial
Para acessar o painel administrativo, utilize a rota especial:

### URL de Acesso:
```
http://127.0.0.1:8000/accounts/xmen-admin-special/?token=admin_access_xmen_2024
```

### Requisitos de Acesso:
1. ✅ **Usuário Logado**: Deve estar autenticado no sistema
2. ✅ **Permissão de Admin**: Deve ter `is_superuser = True`
3. ✅ **Token Especial**: Deve fornecer o token `admin_access_xmen_2024`

### Funcionalidades:
- 🔒 **Segurança Total**: A rota não aparece em lugar nenhum do sistema
- 🎯 **Acesso Único**: Só funciona com o token exato
- ⏰ **Sessão Persistente**: Token fica salvo na sessão após primeiro acesso
- 🚫 **Erro 404**: Retorna "Página não encontrada" para usuários não autorizados

### Usuários Admin Disponíveis:
```
Usuário: admin
Senha: admin
Perfil: Administrador do Sistema
```

### Como Usar:
1. Faça login com o usuário admin
2. Acesse a URL especial com o token
3. O token ficará salvo na sua sessão
4. Próximos acessos não precisam do token até fazer logout

### Heroku (Produção):
```
https://seu-app.herokuapp.com/accounts/xmen-admin-special/?token=admin_access_xmen_2024
```

## ⚠️ Importante
- Esta rota é **SECRETA** e deve ser compartilhada apenas com administradores
- Nunca exponha o token em código público ou documentação acessível
- Para trocar o token, edite o arquivo `/apps/accounts/views.py` na função `special_admin_view`