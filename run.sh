#!/bin/bash

# ============================================================================
# Script de Inicialização - Loja de Informática
# Prepara e executa a aplicação
# ============================================================================

echo "================================================"
echo "🏪 SISTEMA DE LOJA DE INFORMÁTICA"
echo "================================================"
echo ""

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # Sem cor

# Obter diretório do script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check Python
echo -e "${BLUE}📌 Verificando Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✘ Python 3 não encontrado!${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✔ Python ${PYTHON_VERSION} disponível${NC}"
echo ""

# Instalar dependências
echo -e "${BLUE}📌 Verificando dependências...${NC}"
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚙️  Criando ambiente virtual...${NC}"
    python3 -m venv venv
fi

source venv/bin/activate

echo -e "${YELLOW}⚙️  Instalando/Atualizando pacotes...${NC}"
pip install -q -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✔ Dependências instaladas com sucesso${NC}"
else
    echo -e "${RED}✘ Erro ao instalar dependências${NC}"
    exit 1
fi
echo ""

# Verificar MariaDB
echo -e "${BLUE}📌 Verificando MariaDB...${NC}"

# Tentar conectar
if mysql -u root -h localhost -e "SELECT 1" &> /dev/null; then
    echo -e "${GREEN}✔ MariaDB está em execução${NC}"
else
    echo -e "${RED}✘ MariaDB não está acessível${NC}"
    echo -e "${YELLOW}◐ Para iniciar MariaDB:${NC}"
    echo "   /opt/lampp/bin/xampp start"
    echo ""
    read -p "Deseja tentar iniciar? (s/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        /opt/lampp/bin/xampp start
    else
        exit 1
    fi
fi
echo ""

# Verificar/Criar base de dados
echo -e "${BLUE}📌 Verificando Base de Dados...${NC}"

DB_EXISTS=$(mysql -u root -h localhost -e "SHOW DATABASES;" | grep -c "loja_informatica")

if [ $DB_EXISTS -eq 0 ]; then
    echo -e "${YELLOW}⚙️  Base de dados não encontrada${NC}"
    echo -e "${YELLOW}⚙️  Executando setup...${NC}"
    python3 setup_database.py
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}✘ Erro ao criar base de dados${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✔ Base de dados 'loja_informatica' encontrada${NC}"
fi
echo ""

# Executar aplicação
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}✓ Sistema pronto para iniciar!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo -e "${BLUE}► Iniciando aplicação...${NC}"
echo ""

python3 system_loja_informatica.py

# Desativar venv ao sair
deactivate
