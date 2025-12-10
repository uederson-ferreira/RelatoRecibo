#!/bin/bash
# Script para ativar o ambiente virtual

cd "$(dirname "$0")"
source venv/bin/activate
echo "✓ Ambiente virtual ativado!"
echo "Para desativar, digite: deactivate"
