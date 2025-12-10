#!/bin/bash
# Script para iniciar o frontend

cd "$(dirname "$0")"

echo "🚀 Iniciando RelatoRecibo Frontend..."
echo ""

# Verifica se node_modules existe
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependências..."
    npm install
    echo ""
fi

# Verifica se .env existe
if [ ! -f ".env" ]; then
    echo "⚠️  Arquivo .env não encontrado. Criando..."
    echo "VITE_API_URL=http://localhost:8000" > .env
    echo "✓ Arquivo .env criado!"
    echo ""
fi

echo "🌐 Iniciando servidor de desenvolvimento..."
echo "Frontend estará disponível em: http://localhost:3000"
echo "Backend deve estar rodando em: http://localhost:8000"
echo ""
echo "Pressione CTRL+C para parar o servidor"
echo ""

npm run dev
