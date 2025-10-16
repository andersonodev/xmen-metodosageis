#!/bin/bash

# Script de inicialização do Xmen-AgileTeam
set -e

echo "🚀 Iniciando setup do Xmen-AgileTeam..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para logs
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    log_error "Python 3 não encontrado. Instale Python 3.12 ou superior."
    exit 1
fi

# Verificar versão do Python
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.12"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    log_warn "Python $PYTHON_VERSION encontrado. Recomendado: $REQUIRED_VERSION ou superior."
fi

# Criar ambiente virtual se não existir
if [ ! -d "venv" ]; then
    log_info "Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativar ambiente virtual
log_info "Ativando ambiente virtual..."
source venv/bin/activate

# Atualizar pip
log_info "Atualizando pip..."
pip install --upgrade pip

# Instalar dependências
log_info "Instalando dependências..."
pip install -r requirements.txt

# Criar arquivo .env se não existir
if [ ! -f ".env" ]; then
    log_info "Criando arquivo .env..."
    cp .env.example .env
    log_warn "Configure as variáveis de ambiente em .env conforme necessário."
fi

# Executar migrations
log_info "Executando migrations..."
python manage.py makemigrations
python manage.py migrate

# Criar superusuário se solicitado
read -p "Deseja criar um superusuário? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "Criando superusuário..."
    python manage.py createsuperuser
fi

# Povoar com dados de exemplo se solicitado
read -p "Deseja povoar o banco com dados de exemplo? (Y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
    log_info "Povoando banco com dados de exemplo..."
    python manage.py seed_data
fi

# Coletar arquivos estáticos
log_info "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

log_info "✅ Setup concluído com sucesso!"
echo
echo "🎯 Próximos passos:"
echo "  1. Ativar ambiente virtual: source venv/bin/activate"
echo "  2. Executar servidor: python manage.py runserver"
echo "  3. Acessar aplicação: http://localhost:8000"
echo "  4. Ver documentação: http://localhost:8000/api/docs/"
echo
echo "🐳 Ou use Docker:"
echo "  1. docker-compose up --build"
echo "  2. Acessar: http://localhost:8000"
echo
echo "📚 Comandos úteis:"
echo "  make help          - Ver todos os comandos disponíveis"
echo "  make dev-setup     - Setup completo para desenvolvimento"
echo "  make quick-start   - Iniciar com Docker"
echo
log_info "Bom desenvolvimento! 🦾"