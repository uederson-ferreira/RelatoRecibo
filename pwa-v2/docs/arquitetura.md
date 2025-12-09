# Arquitetura RelatoRecibo v2.0 - Python + FastAPI

## Visão Geral

Migração de PWA vanilla (HTML/CSS/JS) para arquitetura moderna com separação frontend/backend usando **Python + FastAPI**.

```bash
┌─────────────────────────────────────────────────────────────┐
│                         CLIENTE                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │         Frontend - PWA (Vite + React + TS)            │  │
│  │  - React 18 + TypeScript                              │  │
│  │  - TanStack Query (cache + sync)                      │  │
│  │  - Zustand (state management)                         │  │
│  │  - PWA (offline-first com Workbox)                    │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓ HTTPS/REST
┌─────────────────────────────────────────────────────────────┐
│                       BACKEND API                            │
│  ┌───────────────────────────────────────────────────────┐  │
│  │            Python + FastAPI + Uvicorn                 │  │
│  │  - FastAPI (API REST + auto docs)                     │  │
│  │  - Pillow (processamento de imagens)                  │  │
│  │  - pytesseract (OCR server-side)                      │  │
│  │  - ReportLab (geração de PDF)                         │  │
│  │  - supabase-py (service_role key)                     │  │
│  │  - python-jose (JWT Authentication)                   │  │
│  │  - Pydantic (validação automática)                    │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓ PostgreSQL
┌─────────────────────────────────────────────────────────────┐
│                      SUPABASE                                │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  PostgreSQL + Row Level Security (RLS)                │  │
│  │  - Auth (usuários e sessões)                          │  │
│  │  - Storage (imagens de recibos)                       │  │
│  │  - Database (relatórios e recibos)                    │  │
│  │  - Realtime (opcional - sync em tempo real)           │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Stack Tecnológica

### Frontend (PWA)

- **Framework:** Vite + React 18 + TypeScript
- **State Management:** Zustand (global) + TanStack Query (server state)
- **Routing:** React Router v6
- **UI/Styling:** TailwindCSS + Shadcn/ui
- **Forms:** React Hook Form + Zod validation
- **PWA:** Vite PWA Plugin + Workbox
- **HTTP Client:** Axios
- **Camera:** React-Camera-Pro ou getUserMedia API
- **Date:** date-fns

### Backend (API) - **Python Stack**

#### Core

- **Runtime:** Python 3.11+
- **Framework:** FastAPI 0.104+
- **ASGI Server:** Uvicorn (dev) / Gunicorn + Uvicorn workers (prod)
- **Language:** Python com Type Hints

#### Processamento

- **OCR:** pytesseract + Tesseract OCR Engine
- **Image Processing:** Pillow (PIL)
- **PDF Generation:** ReportLab
- **File Upload:** FastAPI UploadFile

#### Database & Auth

- **Database Client:** supabase-py (service_role key)
- **Authentication:** python-jose (JWT) + passlib (password hashing)
- **Validation:** Pydantic (built-in FastAPI)

#### Segurança & Utilities

- **CORS:** FastAPI CORSMiddleware
- **Rate Limiting:** slowapi
- **Logging:** loguru
- **Environment:** python-dotenv
- **Testing:** pytest + httpx

### Database & Services

- **Database:** Supabase (PostgreSQL 15)
- **Storage:** Supabase Storage (S3-compatible)
- **Auth:** Supabase Auth
- **Realtime:** Supabase Realtime (opcional)

## Estrutura de Pastas

```bash
relatorecibo/
├── frontend/                    # PWA React
│   ├── public/
│   │   ├── manifest.json
│   │   ├── robots.txt
│   │   └── icons/
│   ├── src/
│   │   ├── assets/             # Imagens, fonts
│   │   ├── components/         # Componentes React
│   │   │   ├── ui/            # Componentes base (shadcn)
│   │   │   ├── reports/       # Componentes de relatórios
│   │   │   ├── receipts/      # Componentes de recibos
│   │   │   └── layout/        # Header, Layout, etc
│   │   ├── hooks/             # Custom hooks
│   │   ├── lib/               # Utilities, helpers
│   │   ├── pages/             # Páginas/Routes
│   │   ├── services/          # API calls, axios config
│   │   ├── store/             # Zustand stores
│   │   ├── types/             # TypeScript types
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── vite-env.d.ts
│   ├── .env.example
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── package.json
│
├── backend/                     # API Python FastAPI
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI app entry point
│   │   ├── config.py           # Settings (pydantic BaseSettings)
│   │   ├── dependencies.py     # Dependency injection
│   │   │
│   │   ├── api/                # API routes
│   │   │   ├── __init__.py
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── router.py  # Main router
│   │   │       ├── auth.py
│   │   │       ├── reports.py
│   │   │       ├── receipts.py
│   │   │       └── profile.py
│   │   │
│   │   ├── core/               # Core functionality
│   │   │   ├── __init__.py
│   │   │   ├── security.py    # JWT, password hashing
│   │   │   ├── middleware.py  # Custom middleware
│   │   │   └── exceptions.py  # Custom exceptions
│   │   │
│   │   ├── models/             # Pydantic models (schemas)
│   │   │   ├── __init__.py
│   │   │   ├── report.py
│   │   │   ├── receipt.py
│   │   │   ├── user.py
│   │   │   └── common.py      # Common schemas
│   │   │
│   │   ├── services/           # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── ocr_service.py
│   │   │   ├── pdf_service.py
│   │   │   ├── storage_service.py
│   │   │   ├── supabase_service.py
│   │   │   └── auth_service.py
│   │   │
│   │   └── utils/              # Helpers
│   │       ├── __init__.py
│   │       ├── image.py       # Image processing utils
│   │       ├── validators.py  # Custom validators
│   │       └── formatters.py  # Data formatters
│   │
│   ├── tests/                  # Pytest tests
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   ├── test_reports.py
│   │   └── test_receipts.py
│   │
│   ├── uploads/                # Temp upload folder (gitignored)
│   ├── .env.example
│   ├── .gitignore
│   ├── requirements.txt        # Production dependencies
│   ├── requirements-dev.txt    # Development dependencies
│   ├── Dockerfile
│   ├── render.yaml             # Render.com config
│   ├── pytest.ini
│   └── README.md
│
├── sql/                         # Database schemas
│   ├── 01_schema.sql
│   ├── 02_rls_policies.sql
│   ├── 03_storage_policies.sql
│   └── 04_functions.sql
│
├── docs/                        # Documentação
│   ├── arquitetura-python.md
│   ├── api.md
│   ├── deployment.md
│   └── setup.md
│
├── .gitignore
└── README.md
```

## Fluxo de Dados

### 1. Autenticação

```bash
Frontend → POST /api/v1/auth/login
         → Backend (FastAPI)
         → Supabase Auth (via supabase-py)
         ← JWT Token (python-jose)
         ← User Session
Frontend ← Store token
```

### 2. Upload de Recibo + OCR

```bash
Frontend (Camera) → captura imagem
                  → comprime imagem (client-side)
                  → POST /api/v1/receipts (multipart/form-data)

Backend (FastAPI) → valida auth (JWT dependency)
                  → recebe arquivo (UploadFile)
                  → otimiza imagem (Pillow)
                  → upload para Supabase Storage (supabase-py)
                  → processa OCR (pytesseract)
                  → extrai valor com regex
                  → salva no DB (service_role key)
                  → retorna dados + URL da imagem

Frontend ← recebe dados
         → atualiza cache (TanStack Query)
         → atualiza UI (React)
```

### 3. Geração de PDF

```bash
Frontend → GET /api/v1/reports/{id}/pdf

Backend → busca relatório + recibos (Supabase)
        → gera PDF (ReportLab)
        → retorna StreamingResponse

Frontend ← download PDF
```

## Segurança

### Frontend

- ✅ Usa apenas **anon key** do Supabase (segura para expor)
- ✅ Armazena JWT em localStorage ou httpOnly cookie
- ✅ HTTPS obrigatório em produção
- ✅ CSP (Content Security Policy)

### Backend (FastAPI)

- ✅ Usa **service_role key** (NUNCA exposta)
- ✅ Dependency injection para autenticação (`Depends(get_current_user)`)
- ✅ Validação automática de input (Pydantic)
- ✅ Rate limiting (slowapi)
- ✅ CORS configurado (CORSMiddleware)
- ✅ Headers de segurança
- ✅ Upload limitado (size + file types + MIME validation)
- ✅ Sanitização de inputs

### Database (Supabase)

- ✅ Row Level Security (RLS) habilitado
- ✅ Policies baseadas em user_id (auth.uid())
- ✅ Storage policies por usuário
- ✅ Indexes otimizados

## Funcionalidades

### MVP (Fase 1)

- [ ] Autenticação (login/registro)
- [ ] CRUD de relatórios
- [ ] Upload de recibo com câmera
- [ ] OCR para detectar valores
- [ ] Lista de recibos por relatório
- [ ] Edição manual de valores
- [ ] Geração de PDF
- [ ] PWA offline-first

### Fase 2 (Futuro)

- [ ] Compartilhamento de relatórios
- [ ] Multi-usuário (times)
- [ ] Dashboard com gráficos
- [ ] Export Excel/CSV
- [ ] Categorização de despesas
- [ ] Anexos adicionais (notas fiscais XML)
- [ ] OCR melhorado com ML (opcional)

## Offline-First Strategy

### Frontend PWA

```javascript
// Service Worker com Workbox
- Cache de assets estáticos (HTML, CSS, JS, images)
- Cache de API responses (TanStack Query + IndexedDB)
- Background sync para uploads pendentes
- Estratégias de cache:
  * Network-first: API calls
  * Cache-first: Assets estáticos
  * StaleWhileRevalidate: Imagens de recibos
```

### Sync Strategy

```bash
Offline → Dados salvos em IndexedDB
       → Background Sync API registra task

Online  → Service Worker detecta conexão
        → Background Sync envia dados pendentes
        → TanStack Query refetch
        → UI atualizada
```

## Comparação: Node.js vs Python

| Aspecto | Node.js (Express) | Python (FastAPI) | Vencedor |
|---------|-------------------|------------------|----------|
| **Performance** | Excelente | Excelente (async) | Empate ⚖️ |
| **Curva de aprendizado** | Média | Fácil | 🐍 Python |
| **OCR** | Tesseract.js | pytesseract (nativo) | 🐍 Python |
| **PDF** | PDFKit | ReportLab | 🐍 Python |
| **Type Safety** | TypeScript | Type Hints + Pydantic | 🐍 Python |
| **Auto-docs** | Manual (Swagger) | Automático (FastAPI) | 🐍 Python |
| **Validação** | Zod (manual) | Pydantic (automático) | 🐍 Python |
| **Processamento Imagem** | Sharp | Pillow | Empate ⚖️ |
| **ML/AI futuro** | Limitado | Excelente (NumPy, etc) | 🐍 Python |
| **Comunidade** | Gigante | Gigante | Empate ⚖️ |
| **Deploy** | Fácil | Fácil | Empate ⚖️ |
| **Hospedagem grátis** | Muitas opções | Muitas opções | Empate ⚖️ |

**Resultado:** Python + FastAPI é **superior para este caso de uso** (OCR + PDF + validação).

## Vantagens da Nova Arquitetura (Python)

### Performance

- ✅ OCR server-side nativo (mais rápido e preciso)
- ✅ Async/await (FastAPI é assíncrono)
- ✅ Cache inteligente (TanStack Query)
- ✅ Imagens otimizadas (Pillow + Supabase CDN)
- ✅ Code splitting (Vite)
- ✅ Lazy loading de rotas

### Escalabilidade

- ✅ Database relacional (PostgreSQL)
- ✅ Armazenamento ilimitado (Supabase Storage)
- ✅ Multi-tenancy (RLS por usuário)
- ✅ API stateless (horizontal scaling)
- ✅ ASGI (suporta WebSockets para futuras features)

### Developer Experience

- ✅ Type-safety end-to-end (Python Type Hints + TypeScript)
- ✅ Hot reload (Uvicorn auto-reload)
- ✅ Documentação automática (Swagger UI + ReDoc)
- ✅ Validação automática (Pydantic)
- ✅ Testes fáceis (pytest)
- ✅ Menos boilerplate que Express

### Manutenibilidade

- ✅ Código modular
- ✅ Separação de concerns
- ✅ Padrões estabelecidos
- ✅ Documentação de tipos
- ✅ Auto-docs sempre atualizadas

## Plano de Migração

### Fase 1: Setup Inicial (1 semana)

1. ✅ Setup Supabase (database + auth + storage)
2. Setup Backend FastAPI
   - Estrutura de pastas
   - Configuração de ambiente
   - Dependências (requirements.txt)
3. Setup Frontend (Vite + React + TS)
   - Estrutura de pastas
   - TailwindCSS + Shadcn
   - React Router
4. Implementar autenticação básica

### Fase 2: Core Features (2-3 semanas)

1. CRUD de relatórios (backend + frontend)
2. Upload de recibos (multipart + storage)
3. Integração OCR (pytesseract)
4. Lista e visualização de recibos
5. Geração de PDF (ReportLab)

### Fase 3: PWA & Polish (1-2 semanas)

1. Service Worker + offline support
2. Background sync
3. Camera integration
4. Testes (pytest + vitest)
5. Error handling e validações
6. UI/UX polish

### Fase 4: Deploy (1 semana)

1. Deploy backend (Render.com)
2. Deploy frontend (Vercel)
3. CI/CD (GitHub Actions)
4. Monitoring e logs
5. Documentação final

### Fase 5: Migração de Dados (Opcional)

1. Script para exportar dados do IndexedDB
2. Script para importar no Supabase
3. Preservar histórico de usuários existentes

## Deploy - Opções de Hospedagem

### Backend Python (Recomendações)

#### 🏆 Render.com (Recomendado)

```yaml
# render.yaml
services:
  - type: web
    name: relatorecibo-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker
    envVars:
      - key: PYTHON_VERSION
        value: 3.11
```

**Vantagens:**

- ✅ 750h/mês grátis
- ✅ Auto-deploy via GitHub
- ✅ SSL grátis
- ✅ PostgreSQL grátis (se precisar além do Supabase)

#### Railway

```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "$PORT"]
```

#### Google Cloud Run

```yaml
# app.yaml
runtime: python311
entrypoint: gunicorn app.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

### Frontend React

#### Vercel (Recomendado)

- Deploy automático via GitHub
- Edge network global
- Domínio grátis (.vercel.app)

#### Netlify

- Alternativa ao Vercel
- Mesmas funcionalidades

## Requisitos de Sistema

### Desenvolvimento

- **Python:** 3.11+
- **Node.js:** 18+ (para frontend)
- **Tesseract OCR:** Instalado no sistema

  ```bash
  # macOS
  brew install tesseract tesseract-lang

  # Ubuntu/Debian
  sudo apt-get install tesseract-ocr tesseract-ocr-por

  # Windows
  # Download from: https://github.com/UB-Mannheim/tesseract/wiki
  ```

- **PostgreSQL:** Supabase (cloud) ou local para testes

### Produção (Render.com)

```yaml
# render.yaml - System dependencies
buildCommand: |
  apt-get update && apt-get install -y tesseract-ocr tesseract-ocr-por
  pip install -r requirements.txt
```

## Próximos Passos

1. **Criar requirements.txt** com todas as dependências
2. **Implementar estrutura base** do FastAPI
3. **Criar modelos Pydantic** para validação
4. **Implementar serviços** (OCR, PDF, Storage)
5. **Setup frontend** com Vite + React
6. **Integração** frontend ↔ backend
7. **Testes** e documentação
8. **Deploy** para Render + Vercel
