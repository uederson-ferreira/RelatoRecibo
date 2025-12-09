#!/bin/bash

echo "Instalando dependências do RelatoRecibo..."

echo "1. Limpando cache e node_modules..."
rm -rf node_modules
rm -f package-lock.json
npm cache clean --force

echo "2. Instalando pacotes básicos..."
npm install --legacy-peer-deps

echo "3. Instalando react-navigation..."
npm install --save --legacy-peer-deps @react-navigation/native@^7.0.0 @react-navigation/stack@^7.0.0 react-native-gesture-handler@^2.22.0

echo "4. Verificando instalação..."
npm list --depth=0

echo ""
echo "Instalação concluída!"
echo ""
echo "Para iniciar o app, execute:"
echo "  npx expo start"
