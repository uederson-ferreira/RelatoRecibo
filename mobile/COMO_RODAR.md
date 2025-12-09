# Como Rodar o RelatoRecibo

## 🚀 Início Rápido

### 1. Instalar Expo Go no Celular

**iPhone:**

- Abra a App Store
- Procure por "Expo Go"
- Instale o app

**Android:**

- Abra a Play Store
- Procure por "Expo Go"
- Instale o app

### 2. Iniciar o Servidor

No terminal, dentro da pasta do projeto:

```bash
npx expo start
```

### 3. Abrir no Celular

**iPhone:**

1. Abra o app Câmera nativo
2. Aponte para o QR code que apareceu no terminal
3. Toque na notificação que aparecer
4. O app abrirá no Expo Go

**Android:**

1. Abra o app Expo Go
2. Toque em "Scan QR code"
3. Aponte para o QR code no terminal
4. O app abrirá automaticamente

## 📱 Outras Formas de Rodar

### Simulador iOS (apenas Mac)

```bash
npx expo start --ios
```

*Requer Xcode instalado*

### Emulador Android

```bash
npx expo start --android
```

*Requer Android Studio e emulador configurado*

### Navegador (apenas para testar UI)

```bash
npx expo start --web
```

*Muitas funcionalidades não funcionarão (câmera, AsyncStorage, etc.)*

## 🎯 Como Usar o App

### Primeiro Uso

1. **Criar um Relatório**
   - Na tela inicial, toque em "+ Novo"
   - Digite um nome (ex: "Despesas Dezembro")
   - Toque em "Criar"

2. **Adicionar um Recibo**
   - Entre no relatório criado
   - Toque no botão "+" (canto inferior direito)
   - Posicione o recibo dentro da área marcada
   - Tire a foto
   - O app tentará detectar o valor (atualmente é mockado)
   - Confirme ou edite o valor
   - Pronto! O recibo foi adicionado

3. **Gerar PDF**
   - Dentro do relatório, toque em "Gerar PDF"
   - O PDF será gerado com todas as fotos
   - Compartilhe via WhatsApp, email, etc.

## 🔧 Comandos Úteis

### Limpar cache e reiniciar

```bash
npx expo start --clear
```

### Ver logs detalhados

```bash
npx expo start --dev-client
```

### Reinstalar dependências

```bash
./install.sh
```

Ou manualmente:

```bash
rm -rf node_modules package-lock.json
npm cache clean --force
npm install --legacy-peer-deps
```

## ❓ Problemas Comuns

### "Metro Bundler is taking too long"

Solução:

```bash
npx expo start --clear
```

### Erro de permissão de câmera

- iOS: Vá em Configurações > Expo Go > Permitir Câmera
- Android: O app pedirá permissão automaticamente

### QR code não funciona

Alternativa: No terminal, pressione:

- `i` - para abrir no iOS
- `a` - para abrir no Android
- `w` - para abrir no navegador

### App não conecta

Certifique-se de que:

- Celular e computador estão na mesma rede WiFi
- Firewall não está bloqueando a conexão

## 📖 Mais Informações

- README.md - Documentação completa
- STATUS.md - Status do desenvolvimento
- QUICKSTART.md - Guia de instalação

## 💡 Dicas

1. **Teste no celular real** para ter a melhor experiência
2. **Use luz adequada** ao fotografar recibos para melhor qualidade
3. **Verifique os valores** extraídos pelo OCR (atualmente são mockados)
4. **Faça backup** exportando PDFs regularmente

## 🎨 Interface

- **Tela Inicial**: Lista de relatórios
- **Detalhes**: Recibos de um relatório específico
- **Câmera**: Captura de novos recibos

Boa sorte! 🎉
