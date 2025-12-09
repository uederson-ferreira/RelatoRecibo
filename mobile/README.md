# RelatoRecibo - Sistema de Gestão de Recibos

Aplicativo móvel para prestação de contas de recibos com captura de fotos, OCR para extração de valores e geração de relatórios em PDF.

## Funcionalidades

- **Criação de Relatórios**: Organize seus recibos em relatórios personalizados
- **Meta de Valores**: Defina metas e acompanhe o progresso com barra visual
- **Captura de Fotos**: Tire fotos dos recibos diretamente pelo app ou escolha da galeria
- **Recorte Automático**: Detecção e recorte automático da área central do recibo (80%)
- **Visualização de Fotos**: Toque no recibo para ver a foto em tela cheia
- **OCR (Reconhecimento de Texto)**: Extração automática de valores dos recibos
- **Edição Manual**: Confirme ou edite os valores detectados
- **Armazenamento Local**: Todos os dados ficam salvos no dispositivo com AsyncStorage
- **Sincronização em Nuvem**: Opção de backup com Supabase (configuração opcional - scripts SQL inclusos)
- **Geração de PDF**: Crie relatórios profissionais em PDF com fotos e valores
- **Compartilhamento**: Envie os relatórios por email, WhatsApp, etc.

## Stack Tecnológica

- **React Native** com **Expo**
- **TypeScript** para tipagem
- **@react-navigation** para navegação entre telas
- **expo-camera** para captura de fotos
- **expo-image-manipulator** para processamento e recorte de imagens
- **expo-print** para geração de PDFs
- **AsyncStorage** para armazenamento local
- **Supabase** para sincronização em nuvem (opcional)

## Instalação

### Pré-requisitos

- Node.js 18+
- npm ou yarn
- Expo CLI
- Expo Go app no seu celular (iOS ou Android)

### Passos

1. Clone o repositório:

```bash
git clone <url-do-repositorio>
cd RelatoRecibo
```

1. Instale as dependências:

```bash
npm install
```

1. Inicie o app:

```bash
npx expo start
```

1. Escaneie o QR code com o app Expo Go

## Estrutura do Projeto

```bash
src/
├── components/       # Componentes reutilizáveis
├── screens/          # Telas do aplicativo
│   ├── HomeScreen.tsx
│   ├── ReportDetailsScreen.tsx
│   └── CameraCaptureScreen.tsx
├── navigation/       # Configuração de navegação
│   └── AppNavigator.tsx
├── services/         # Serviços e lógica de negócio
│   ├── database.ts          # Armazenamento local (AsyncStorage)
│   ├── ocr.ts              # Processamento OCR
│   ├── imageProcessing.ts  # Manipulação de imagens
│   ├── pdf.ts              # Geração de PDFs
│   └── supabase.ts         # Sincronização em nuvem
├── types/           # Definições TypeScript
│   └── index.ts
└── utils/           # Utilitários
```

## Como Usar

### 1. Criar um Relatório

1. Na tela inicial, toque em **"+ Novo"**
2. Digite um nome para o relatório
3. Toque em **"Criar"**

### 2. Adicionar Recibos

1. Entre no relatório criado
2. Toque no botão **"+"** (flutuante no canto inferior direito)
3. Posicione o recibo dentro da área marcada
4. Tire a foto
5. O app tentará detectar o valor automaticamente
6. Confirme ou edite o valor detectado
7. O recibo será adicionado ao relatório

### 3. Gerar PDF

1. Entre no relatório desejado
2. Toque em **"Gerar PDF"**
3. O PDF será criado e você poderá compartilhá-lo

## Configuração Avançada

### OCR com Tesseract

Para melhor precisão no OCR, você pode instalar o Tesseract:

1. Instale a biblioteca:

```bash
npm install react-native-tesseract-ocr
```

1. Siga as instruções em `src/services/ocr.ts` para ativar o Tesseract

### Sincronização com Supabase

1. Crie uma conta em <https://supabase.com>
1. Crie um novo projeto
1. Execute os scripts SQL fornecidos em `src/services/supabase.ts`
1. Instale o cliente Supabase:

```bash
npx expo install @supabase/supabase-js
```

1. Crie um arquivo `.env`:

```bash
EXPO_PUBLIC_SUPABASE_URL=sua-url-do-supabase
EXPO_PUBLIC_SUPABASE_ANON_KEY=sua-chave-anon
```

1. Descomente o código em `src/services/supabase.ts`

## Melhorias Futuras

- [ ] Implementar OCR real com Tesseract ou Google Vision
- [ ] Adicionar detecção de bordas para recorte automático mais preciso
- [ ] Implementar autenticação de usuários
- [ ] Adicionar categorização de recibos
- [ ] Implementar busca e filtros
- [ ] Adicionar gráficos e estatísticas
- [ ] Suporte para múltiplos idiomas
- [ ] Modo escuro
- [ ] Exportar para Excel/CSV
- [ ] Backup automático

## ✅ Melhorias Recentes (v1.0.0)

1. **Visualização de Fotos em Tela Cheia**
   - Clique em qualquer recibo para ver a foto completa
   - Modal elegante com fundo escuro
   - Mostra valor e data do recibo

2. **Crop Automático Melhorado**
   - Corta automaticamente para 80% da área central
   - Remove bordas e fundo desnecessários
   - Foca na área do recibo

3. **Correção de Erros de Salvamento**
   - Resolvido erro "não foi possível processar a imagem"
   - Simplificado fluxo de processamento
   - Removido step redundante de cópia de arquivo

4. **Gerador de Ícone**
   - HTML interativo para gerar ícone do app
   - Design profissional com recibo e câmera
   - Ver `assets/generate-icon.html`

Ver detalhes completos em [MELHORIAS.md](./MELHORIAS.md)

## Problemas Conhecidos

- O OCR atual é um placeholder que retorna valores mockados
- É necessário configurar manualmente o Supabase para sincronização (opcional)

## Licença

MIT

## Suporte

Para reportar bugs ou solicitar features, abra uma issue no repositório.
