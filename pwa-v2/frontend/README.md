# RelatoRecibo Frontend

Frontend React + TypeScript + Vite para o sistema RelatoRecibo.

## 🚀 Tecnologias

- **React 18** + **TypeScript**
- **Vite** (build tool)
- **React Router v6** (navegação)
- **TanStack Query** (data fetching e cache)
- **Zustand** (state management)
- **React Hook Form** + **Zod** (formulários e validação)
- **TailwindCSS** (estilização)
- **Axios** (HTTP client)
- **date-fns** (manipulação de datas)
- **Lucide React** (ícones)

## 📦 Instalação

```bash
cd pwa-v2/frontend
npm install
```

## 🏃 Executar

```bash
npm run dev
```

A aplicação estará disponível em `http://localhost:3000`

## 🔧 Configuração

Crie um arquivo `.env` na raiz do frontend:

```env
VITE_API_URL=http://localhost:8000
```

## 📁 Estrutura

```bash
src/
├── components/       # Componentes reutilizáveis
│   ├── Layout.tsx
│   ├── CreateReportModal.tsx
│   ├── ReceiptCard.tsx
│   └── UploadReceiptModal.tsx
├── pages/            # Páginas da aplicação
│   ├── LoginPage.tsx
│   ├── SignupPage.tsx
│   ├── DashboardPage.tsx
│   ├── ReportsPage.tsx
│   └── ReportDetailsPage.tsx
├── services/         # Serviços de API
│   ├── api.ts
│   ├── authService.ts
│   ├── reportService.ts
│   └── receiptService.ts
├── stores/           # Zustand stores
│   └── authStore.ts
├── types/            # TypeScript types
│   └── index.ts
├── App.tsx           # Componente principal
├── main.tsx          # Entry point
└── index.css         # Estilos globais
```

## 🎨 Features

- ✅ Autenticação (Login/Signup)
- ✅ Dashboard com estatísticas
- ✅ CRUD de Relatórios
- ✅ CRUD de Recibos
- ✅ Upload de imagens de recibos
- ✅ Processamento OCR automático
- ✅ Geração e download de PDF
- ✅ Interface responsiva
- ✅ PWA (Progressive Web App)

## 🏗️ Build

```bash
npm run build
```

Os arquivos serão gerados em `dist/`

## 📝 Scripts

- `npm run dev` - Inicia servidor de desenvolvimento
- `npm run build` - Build para produção
- `npm run preview` - Preview do build de produção
- `npm run lint` - Executa ESLint

## 🔐 Autenticação

O frontend usa JWT tokens armazenados no localStorage via Zustand persist middleware.

## 📱 PWA

A aplicação é uma PWA configurada com Vite PWA Plugin. Para instalar:

1. Acesse a aplicação no navegador
2. Clique no ícone de instalação na barra de endereços
3. Ou use o menu do navegador: "Adicionar à tela inicial"

## 🌐 Deploy

### Vercel (Recomendado)

```bash
npm install -g vercel
vercel
```

### Netlify

```bash
npm run build
# Arraste a pasta dist/ para netlify.com/drop
```

## 📚 Documentação da API

A API está documentada em `/api/docs` quando o backend estiver rodando.
