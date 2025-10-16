"""
Celery configuration for xmen_agileteam project.

NOTA: Celery foi removido para compatibilidade com deploy gratuito.
Para tarefas em background, considere usar:
- django-background-tasks (para tarefas simples)
- django-q (alternativa leve)
- Scheduled jobs do Heroku (para tarefas periódicas)
"""

# Configuração desabilitada para deploy gratuito
# import os
# from celery import Celery
# from django.conf import settings

# Para reativar Celery quando tiver Redis disponível:
# 1. Descomente as importações acima
# 2. Adicione redis==5.0.1 e celery==5.3.4 ao requirements.txt
# 3. Adicione REDIS_URL nas variáveis de ambiente
# 4. Reative o worker no Procfile