#!/bin/bash

# Script de Instalação Rápida
# Sistema de Gestão de Alunos

echo "=========================================="
echo "Sistema de Gestão de Alunos"
echo "Instalação Rápida"
echo "=========================================="
echo ""

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado!"
    echo "Por favor, instale o Python 3.8 ou superior."
    exit 1
fi

echo "✓ Python encontrado: $(python3 --version)"
echo ""

# Verificar se pip está instalado
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 não encontrado!"
    echo "Por favor, instale o pip3."
    exit 1
fi

echo "✓ pip3 encontrado"
echo ""

# Instalar dependências
echo "Instalando dependências..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Dependências instaladas com sucesso!"
    echo ""
    echo "=========================================="
    echo "Próximos Passos:"
    echo "=========================================="
    echo ""
    echo "1. Configure o Supabase:"
    echo "   - Acesse https://supabase.com"
    echo "   - Crie um projeto"
    echo "   - Execute o script schema.sql no SQL Editor"
    echo ""
    echo "2. Inicie o sistema:"
    echo "   python3 main.py"
    echo ""
    echo "3. Configure as credenciais quando solicitado"
    echo ""
    echo "Para mais informações, leia o arquivo README.md"
    echo ""
else
    echo ""
    echo "❌ Erro ao instalar dependências!"
    echo "Tente instalar manualmente:"
    echo "  pip3 install PySide6 supabase python-dotenv"
    exit 1
fi
