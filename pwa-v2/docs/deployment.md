# Guia de Deploy - RelatoRecibo

Deploy da aplicação RelatoRecibo (Frontend + Backend Python) em ambientes de produção.

## Arquitetura de Deploy

```bash
┌─────────────────────────────────────────────────┐
│  Frontend (Vercel)                              │
│  - React PWA                                    │
│  - CDN Global                                   │
│  - HTTPS automático                             │
│  - relatorecibo.vercel.app                      │
└─────────────────────────────────────────────────┘
                    ↓ HTTPS API Calls
┌─────────────────────────────────────────────────┐
│  Backend (Render.com)                           │
│  - FastAPI + Python                             │
│  - Tesseract OCR                                │
│  - api.relatorecibo.com                         │
└─────────────────────────────────────────────────┘
                    ↓ PostgreSQL + Storage
┌─────────────────────────────────────────────────┐
│  Supabase                                       │
│  - PostgreSQL Database                          │
│  - File Storage (S3)                            │
│  - Authentication                               │
└─────────────────────────────────────────────────┘
```

---

## 1. Setup Supabase

### Criar Projeto

1. Acesse [supabase.com](https://supabase.com)
2. Crie uma nova organização (se necessário)
3. Crie um novo projeto
   - Nome: `relatorecibo`
   - Database Password: gere uma senha forte
   - Region: escolha a mais próxima (South America - São Paulo)

### Configurar Database

1. No Supabase Dashboard, vá em **SQL Editor**
2. Execute os scripts SQL na ordem:

   ```sql
   -- Execute cada arquivo SQL
   sql/01_schema.sql
   sql/02_rls_policies.sql
   sql/03_storage_policies.sql
   sql/04_functions.sql
   ```

### Configurar Storage

1. Vá em **Storage**
2. Crie um bucket chamado `receipts`
   - Public: **false** (private)
   - File size limit: 5MB
   - Allowed MIME types: `image/jpeg`, `image/png`, `image/webp`

### Configurar Authentication

1. Vá em **Authentication** > **Settings**
2. Habilite **Email Provider**
3. Configure **Email Templates** (opcional)
4. Habilite **Email Confirmations** se desejar

### Obter Credentials

Vá em **Settings** > **API** e copie:

- ✅ Project URL
- ✅ `anon` `public` key (para frontend)
- ✅ `service_role` `secret` key (para backend - **NUNCA exponha**)

---

## 2. Deploy do Backend (Render.com)

### Preparar Repositório

1. **Criar estrutura backend/**

   ```bash
   mkdir -p backend/app
   cd backend
   ```

2. **Criar arquivos de configuração:**

#### `backend/.env.example`

```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# JWT
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this

# Environment
ENVIRONMENT=production

# CORS
ALLOWED_ORIGINS=["https://relatorecibo.vercel.app"]
```

#### `backend/Dockerfile`

```dockerfile
FROM python:3.11-slim

# Install system dependencies (Tesseract OCR)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-por \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Render will set PORT env var)
EXPOSE 8000

# Start application
CMD ["gunicorn", "app.main:app", "--workers", "2", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

#### `backend/render.yaml`

```yaml
services:
  - type: web
    name: relatorecibo-api
    env: docker
    region: oregon # ou sao-paulo se disponível
    plan: free
    dockerfilePath: ./Dockerfile
    envVars:
      - key: PYTHON_VERSION
        value: "3.11"
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_ANON_KEY
        sync: false
      - key: SUPABASE_SERVICE_ROLE_KEY
        sync: false
      - key: JWT_SECRET_KEY
        generateValue: true
      - key: ENVIRONMENT
        value: production
      - key: ALLOWED_ORIGINS
        value: '["https://relatorecibo.vercel.app"]'
    healthCheckPath: /health
```

#### `backend/requirements.txt`

```bash
# Copiar do arquivo backend-requirements.txt criado anteriormente
# Adicionar gunicorn para produção:
gunicorn==21.2.0
```

### Deploy no Render

1. **Criar conta no Render.com**
   - Acesse [render.com](https://render.com)
   - Faça login com GitHub

2. **Conectar repositório**
   - New + > Web Service
   - Connect seu repositório GitHub
   - Root Directory: `backend`
   - Environment: Docker

3. **Configurar variáveis de ambiente**
   No dashboard do Render, adicione:

   ```bash
   SUPABASE_URL=https://xxx.supabase.co
   SUPABASE_ANON_KEY=eyJxxx...
   SUPABASE_SERVICE_ROLE_KEY=eyJxxx... (CUIDADO!)
   JWT_SECRET_KEY=(gerado automaticamente ou custom)
   ENVIRONMENT=production
   ALLOWED_ORIGINS=["https://relatorecibo.vercel.app"]
   ```

4. **Deploy**
   - Clique em "Create Web Service"
   - Aguarde o build (5-10 minutos na primeira vez)
   - Anote a URL: `https://relatorecibo-api.onrender.com`

5. **Testar**

   ```bash
   curl https://relatorecibo-api.onrender.com/health
   # Deve retornar: {"status":"healthy","version":"2.0.0"}
   ```

### Limitações do Free Tier (Render)

⚠️ **Importante:**

- ✅ 750 horas/mês (suficiente se um único serviço)
- ⚠️ **Sleep após 15 min de inatividade** (cold start ~30s)
- ✅ 512MB RAM
- ✅ SSL grátis
- ⚠️ **Reinicia após 90 dias** se não houver activity

**Solução para cold start:**

- Use um serviço de ping (ex: UptimeRobot) para fazer requests a cada 10min
- Ou aceite o delay de ~30s na primeira request

---

## 3. Deploy do Frontend (Vercel)

### Preparar Frontend

1. **Criar arquivo de ambiente:**

#### `frontend/.env.example`

```bash
VITE_API_URL=https://relatorecibo-api.onrender.com/api/v1
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

1. **Configurar build:**

#### `frontend/vite.config.ts`

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      manifest: {
        name: 'RelatoRecibo',
        short_name: 'RelatoRecibo',
        theme_color: '#2196F3',
        background_color: '#ffffff',
        display: 'standalone',
        icons: [
          {
            src: '/icon-192.png',
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: '/icon-512.png',
            sizes: '512x512',
            type: 'image/png'
          }
        ]
      }
    })
  ],
  build: {
    outDir: 'dist',
    sourcemap: false,
  }
})
```

### Deploy na Vercel

1. **Criar conta na Vercel**
   - Acesse [vercel.com](https://vercel.com)
   - Login com GitHub

2. **Importar projeto**
   - New Project
   - Import seu repositório
   - Root Directory: `frontend`
   - Framework Preset: Vite
   - Build Command: `npm run build`
   - Output Directory: `dist`

3. **Configurar variáveis de ambiente**
   No dashboard da Vercel > Settings > Environment Variables:

   ```bash
   VITE_API_URL=https://relatorecibo-api.onrender.com/api/v1
   VITE_SUPABASE_URL=https://xxx.supabase.co
   VITE_SUPABASE_ANON_KEY=eyJxxx...
   ```

4. **Deploy**
   - Clique em "Deploy"
   - Aguarde build (~2 minutos)
   - URL: `https://relatorecibo.vercel.app`

5. **Configurar domínio customizado (Opcional)**
   - Settings > Domains
   - Add domain: `relatorecibo.com`
   - Configure DNS conforme instruções

---

## 4. Configuração de CORS

No backend, certifique-se de que o CORS permite a origem do Vercel:

```python
# backend/app/config.py
ALLOWED_ORIGINS = [
    "http://localhost:5173",  # dev
    "https://relatorecibo.vercel.app",  # production
    "https://relatorecibo.com"  # custom domain (se tiver)
]
```

Redeploy o backend se necessário.

---

## 5. CI/CD com GitHub Actions

### Backend - `.github/workflows/deploy-backend.yml`

```yaml
name: Deploy Backend to Render

on:
  push:
    branches: [main]
    paths:
      - 'backend/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Trigger Render Deploy
        run: |
          curl -X POST ${{ secrets.RENDER_DEPLOY_HOOK_URL }}
```

### Frontend - `.github/workflows/deploy-frontend.yml`

```yaml
name: Deploy Frontend to Vercel

on:
  push:
    branches: [main]
    paths:
      - 'frontend/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          working-directory: ./frontend
```

**Configurar secrets no GitHub:**

- `RENDER_DEPLOY_HOOK_URL` (Render Dashboard > Settings > Deploy Hook)
- `VERCEL_TOKEN` (Vercel Settings > Tokens)
- `VERCEL_ORG_ID` e `VERCEL_PROJECT_ID` (`.vercel/project.json`)

---

## 6. Monitoramento e Logs

### Backend (Render)

**Logs em tempo real:**

```bash
# Via Render Dashboard
https://dashboard.render.com > Logs tab
```

**Adicionar Sentry (Opcional):**

```python
# backend/app/main.py
import sentry_sdk

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    environment=settings.ENVIRONMENT,
)
```

### Frontend (Vercel)

**Analytics:**

- Vercel Analytics (built-in)
- Google Analytics (adicionar ao index.html)

---

## 7. Backup e Manutenção

### Database Backup (Supabase)

Supabase faz backups automáticos (plano Free tem backups diários por 7 dias).

**Backup manual:**

```bash
# Via Supabase CLI
supabase db dump -f backup.sql
```

### Storage Backup

Implementar rotina de backup do Storage bucket para outro S3.

---

## 8. Custos Estimados

### Free Tier (Desenvolvimento/MVP)

| Serviço | Plano | Custo | Limitações |
|---------|-------|-------|-----------|
| **Supabase** | Free | $0 | 500MB DB, 1GB Storage, 50k MAU |
| **Render** | Free | $0 | 750h/mês, sleep após 15min |
| **Vercel** | Hobby | $0 | 100GB bandwidth/mês |
| **TOTAL** | | **$0/mês** | Limitações aplicam |

### Produção (Pago)

| Serviço | Plano | Custo |
|---------|-------|-------|
| **Supabase** | Pro | $25/mês |
| **Render** | Starter | $7/mês |
| **Vercel** | Pro | $20/mês |
| **TOTAL** | | **$52/mês** |

---

## 9. Checklist de Deploy

### Pré-Deploy

- [ ] Supabase configurado (database + storage + RLS)
- [ ] Backend testado localmente
- [ ] Frontend testado localmente
- [ ] Variáveis de ambiente documentadas
- [ ] Dockerfile funcional

### Deploy Backend

- [ ] Render.com configurado
- [ ] Variáveis de ambiente adicionadas
- [ ] Tesseract OCR instalado
- [ ] Health check funcionando
- [ ] API docs acessíveis (/api/docs)

### Deploy Frontend

- [ ] Vercel configurado
- [ ] Build bem-sucedido
- [ ] PWA manifest correto
- [ ] Service Worker registrado
- [ ] HTTPS funcionando

### Pós-Deploy

- [ ] Testar fluxo completo (signup → upload → PDF)
- [ ] Verificar CORS
- [ ] Testar offline mode (PWA)
- [ ] Configurar domínio customizado
- [ ] Configurar CI/CD
- [ ] Setup monitoring (Sentry, etc)
- [ ] Documentar URLs de produção

---

## 10. Troubleshooting

### Backend não inicia

## **Erro: "Tesseract not found"**

```dockerfile
# Adicionar ao Dockerfile:
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-por
```

## **Erro: "Port already in use"**

```bash
# Render usa variável PORT automaticamente
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "$PORT"]
```

### CORS Errors

## **Erro: "Access-Control-Allow-Origin"**

```python
# Verificar ALLOWED_ORIGINS no backend
ALLOWED_ORIGINS = ["https://relatorecibo.vercel.app"]
```

### Cold Start (Render Free)

**Solução:**

1. Usar UptimeRobot para ping a cada 10min
2. Ou aceitar delay de ~30s

### Build Failures (Vercel)

## **Erro: "Module not found"**

```bash
# Limpar cache
vercel --force
```

---

## Recursos

- [Render Docs](https://render.com/docs)
- [Vercel Docs](https://vercel.com/docs)
- [Supabase Docs](https://supabase.com/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

---

## Suporte

Problemas? Abra uma issue no GitHub ou consulte a documentação oficial dos serviços.
