# RelatoRecibo - Monorepo

> **Sistema completo de gestão de recibos e prestação de contas**

Projeto com múltiplas versões e plataformas do RelatoRecibo.

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![React](https://img.shields.io/badge/React-18-61DAFB)
![React Native](https://img.shields.io/badge/React%20Native-Latest-blue)

---

## 📁 Estrutura do Monorepo

```bash
RelatoRecibo/
├── mobile/                      # 📱 React Native App (iOS/Android)
│   ├── App.js
│   ├── package.json
│   └── README.md
│
├── pwa-v2/                      # 🚀 PWA v2.0 (Python + React)
│   ├── docs/                    # Documentação completa
│   │   ├── arquitetura.md
│   │   ├── arquitetura-modular.md
│   │   ├── code-templates.md
│   │   ├── backend-examples.md
│   │   ├── deployment.md
│   │   └── api.md
│   ├── sql/                     # Database schemas
│   │   ├── 01_schema.sql
│   │   ├── 02_rls_policies.sql
│   │   ├── 03_storage_policies.sql
│   │   └── 04_functions.sql
│   ├── old-version/             # Versão vanilla arquivada
│   ├── backend-requirements.txt
│   ├── backend-requirements-dev.txt
│   └── README.md
│
├── .gitignore                   # Global gitignore
└── README.md                    # Este arquivo
```

---

## 🎯 Versões Disponíveis

### 1. 📱 Mobile (React Native)

**Localização:** `mobile/`

- React Native + Expo
- iOS + Android
- OCR nativo
- SQLite local

**Status:** ✅ Funcional

[Ver documentação →](mobile/README.md)

### 2. 🚀 PWA v2.0 (Moderna)

**Localização:** `pwa-v2/`

**Stack:**

- **Backend:** Python 3.11+ + FastAPI
- **Frontend:** React 18 + TypeScript + Vite
- **Database:** Supabase (PostgreSQL)
- **Deploy:** Render.com (backend) + Vercel (frontend)

**Features:**

- ✅ Arquitetura modular (< 300 linhas por arquivo)
- ✅ 100% documentado (docstrings + type hints)
- ✅ OCR server-side (pytesseract)
- ✅ PDF profissional (ReportLab)
- ✅ PWA offline-first
- ✅ Row Level Security (RLS)

**Status:** 🚧 Em desenvolvimento

[Ver documentação →](pwa-v2/README.md)

### 3. 📝 PWA v1.0 (Vanilla)

**Localização:** `pwa-v2/old-version/`

- HTML + CSS + JavaScript puro
- Tesseract.js client-side
- IndexedDB
- jsPDF

**Status:** 📦 Arquivado (referência)

---

## 🚦 Quick Start

### Mobile (React Native)

```bash
cd mobile
npm install
npm start
```

### PWA v2.0

**Backend:**

```bash
cd pwa-v2
python3 -m venv venv
source venv/bin/activate
pip install -r backend-requirements-dev.txt
cd backend
uvicorn app.main:app --reload
```

**Frontend:**

```bash
cd pwa-v2/frontend
npm install
npm run dev
```

---

## 📚 Documentação

### Arquitetura PWA v2.0

- [`pwa-v2/docs/arquitetura.md`](pwa-v2/docs/arquitetura.md) - Visão geral
- [`pwa-v2/docs/arquitetura-modular.md`](pwa-v2/docs/arquitetura-modular.md) - Modularização
- [`pwa-v2/docs/code-templates.md`](pwa-v2/docs/code-templates.md) - Templates de código
- [`pwa-v2/docs/deployment.md`](pwa-v2/docs/deployment.md) - Deploy

### API & Database

- [`pwa-v2/docs/api.md`](pwa-v2/docs/api.md) - API REST
- [`pwa-v2/sql/`](pwa-v2/sql/) - SQL schemas

---

## 🛠️ Tecnologias

### Mobile

- React Native + Expo
- SQLite
- React Navigation

### PWA v2.0 -

**Frontend:**

- React 18 + TypeScript
- Vite + TailwindCSS
- TanStack Query + Zustand

**Backend:**

- Python 3.11 + FastAPI
- pytesseract (OCR)
- ReportLab (PDF)
- Pydantic

**Infrastructure:**

- Supabase (PostgreSQL + Storage + Auth)
- Render.com (backend)
- Vercel (frontend)

---

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma feature branch (`git checkout -b feature/nome`)
3. Commit suas mudanças (`git commit -m 'feat: adiciona feature'`)
4. Push para a branch (`git push origin feature/nome`)
5. Abra um Pull Request

**Convenções:**

- Commits: [Conventional Commits](https://www.conventionalcommits.org/)
- Python: PEP 8 + docstrings obrigatórias
- TypeScript: ESLint + Prettier
- Arquivos: < 300 linhas

---

## 📄 Licença

MIT License - veja [LICENSE](LICENSE)

---

## 👥 Autores

## **RelatoRecibo Team**

---

## 🔗 Links

- **GitHub:** <https://github.com/uederson-ferreira/RelatoRecibo>
- **API Docs (PWA v2):** <https://api.relatorecibo.com/api/docs> (em breve)

---

**Status do Projeto:** 🚧 Em desenvolvimento ativo

**Última atualização:** 2025-12-09
