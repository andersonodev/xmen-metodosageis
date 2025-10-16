#!/bin/bash

# Script de inicialização rápida do Xmen-AgileTeam
# Este script executa todas as etapas necessárias para rodar o projeto

set -e

echo "🦾 XMEN-AGILETEAM - INICIALIZAÇÃO RÁPIDA"
echo "========================================"

# Verificar se Python 3 está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instale Python 3.8+ para continuar."
    exit 1
fi

echo "✅ Python $(python3 --version) encontrado"

# Ir para o diretório do projeto
cd "$(dirname "$0")"

# Criar ambiente virtual se não existir
if [ ! -d "venv" ]; then
    echo "🔧 Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativar ambiente virtual
echo "🔧 Ativando ambiente virtual..."
source venv/bin/activate

# Instalar dependências
echo "📦 Instalando dependências..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1

echo "✅ Dependências instaladas"

# Criar .env se não existir
if [ ! -f ".env" ]; then
    echo "🔧 Criando arquivo .env..."
    cp .env.example .env
fi

# Aplicar migrations
echo "🗄️  Aplicando migrations..."
python manage.py makemigrations > /dev/null 2>&1
python manage.py migrate > /dev/null 2>&1

echo "✅ Banco de dados configurado"

# Coletar arquivos estáticos
echo "📁 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput > /dev/null 2>&1

# Perguntar se deve criar dados de exemplo
read -p "📊 Deseja criar dados de exemplo? (Y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
    echo "🌱 Criando dados de exemplo..."
    python manage.py seed_data > /dev/null 2>&1
    echo "✅ Dados de exemplo criados"
fi

# Perguntar se deve criar superusuário
read -p "👤 Deseja criar um superusuário? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "👤 Criando superusuário..."
    python manage.py createsuperuser
fi

echo ""
echo "🎉 INICIALIZAÇÃO CONCLUÍDA COM SUCESSO!"
echo ""
echo "🚀 PRÓXIMOS PASSOS:"
echo "   1. Ativar ambiente: source venv/bin/activate"
echo "   2. Executar servidor: python manage.py runserver"
echo "   3. Acessar aplicação: http://localhost:8000"
echo "   4. Ver API docs: http://localhost:8000/api/docs/"
echo ""
echo "🔧 COMANDOS ÚTEIS:"
echo "   make help          - Ver todos os comandos"
echo "   make run           - Executar servidor"
echo "   make test          - Executar testes"
echo "   make clean         - Limpar cache"
echo ""
echo "📚 ENDPOINTS PRINCIPAIS:"
echo "   /api/auth/login/         - Login"
echo "   /api/skills/             - Habilidades"
echo "   /api/teams/              - Times"
echo "   /api/projects/           - Projetos"
echo "   /api/tasks/              - Tarefas"
echo "   /api/recommendations/    - IA"
echo ""
echo "🐳 DOCKER (ALTERNATIVO):"
echo "   docker-compose up --build"
echo ""

# Verificar se Redis está rodando (para WebSockets e Celery)
if ! pgrep -x "redis-server" > /dev/null; then
    echo "⚠️  ATENÇÃO: Redis não está rodando"
    echo "   Para usar WebSockets e notificações, instale e execute Redis:"
    echo "   - macOS: brew install redis && redis-server"
    echo "   - Ubuntu: sudo apt install redis-server"
    echo "   - Docker: docker run -p 6379:6379 redis:alpine"
fi

echo "✨ Pronto para desenvolver! Boa sorte! 🦾"