# 🗄️ Setup do Supabase - RelatoRecibo

Guia completo para configurar o banco de dados Supabase.

---

## ✅ Configuração Concluída

- ✅ Credenciais do Supabase configuradas no `.env`
- ✅ Backend pronto para conectar ao Supabase
- ⏳ Falta executar os scripts SQL no Supabase

---

## 📋 Próximos Passos

### 1. Acessar o Supabase Dashboard

Abra o link:

```
https://supabase.com/dashboard/project/euecdkkmnrzqbetzgujw
```

### 2. Executar os Scripts SQL

Execute os scripts **na ordem** usando o **SQL Editor**:

#### 📄 Script 1: Schema (Tabelas)

1. No dashboard, clique em **SQL Editor** (sidebar esquerda)
2. Clique em **New query**
3. Copie o conteúdo de: `pwa-v2/sql/01_schema.sql`
4. Cole no editor e clique em **Run**

**O que este script faz:**

- Cria as tabelas: `users`, `reports`, `receipts`
- Define as colunas e tipos de dados
- Configura chaves primárias e estrangeiras
- Adiciona constraints de validação

#### 🔒 Script 2: RLS Policies (Segurança)

1. Nova query no SQL Editor
2. Copie o conteúdo de: `pwa-v2/sql/02_rls_policies.sql`
3. Cole e execute

**O que este script faz:**

- Habilita Row Level Security (RLS)
- Cria políticas de acesso por usuário
- Garante que cada usuário vê apenas seus dados
- Previne acesso não autorizado

#### 📦 Script 3: Storage Policies (Bucket)

1. Nova query no SQL Editor
2. Copie o conteúdo de: `pwa-v2/sql/03_storage_policies.sql`
3. Cole e execute

**O que este script faz:**

- Cria o bucket `receipts` para armazenar imagens
- Define políticas de upload/download
- Limita tamanho de arquivos (5MB)
- Restringe tipos de arquivo (jpg, png, webp)

#### ⚙️ Script 4: Functions (Funções)

1. Nova query no SQL Editor
2. Copie o conteúdo de: `pwa-v2/sql/04_functions.sql`
3. Cole e execute

**O que este script faz:**

- Cria função para recalcular totais de relatórios
- Cria triggers automáticos
- Função de atualização de timestamps
- Validações customizadas

---

## ✓ Verificação

Depois de executar todos os scripts, verifique:

### 1. Tabelas Criadas

- Vá em **Table Editor** (sidebar)
- Deve ver 3 tabelas:
  - ✅ `users`
  - ✅ `reports`
  - ✅ `receipts`

### 2. Storage Bucket

- Vá em **Storage** (sidebar)
- Deve ver o bucket:
  - ✅ `receipts`

### 3. Testar Conexão

Execute o backend para testar a conexão:

```bash
cd pwa-v2/backend

# Instalar dependências (se necessário)
pip install -r backend-requirements.txt

# Rodar o servidor
uvicorn app.main:app --reload
```

O servidor deve iniciar em: `http://localhost:8000`

Acesse a documentação da API: `http://localhost:8000/docs`

---

## 🔑 Credenciais Configuradas

Arquivo `.env` criado com:

```env
SUPABASE_URL=https://euecdkkmnrzqbetzgujw.supabase.co
SUPABASE_ANON_KEY=eyJhbGc...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...
JWT_SECRET_KEY=D2xrwJr5...
```

⚠️ **IMPORTANTE:** O arquivo `.env` está no `.gitignore` e **não será commitado** no Git!

---

## 🧪 Testar a API

Depois de rodar o backend, você pode testar:

### 1. Health Check

```bash
curl http://localhost:8000/
```

Resposta esperada:

```json
{
  "status": "ok",
  "message": "RelatoRecibo API v2.0.0",
  "environment": "development"
}
```

### 2. Criar Usuário

```bash
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@example.com",
    "password": "SenhaForte123!",
    "full_name": "Usuário Teste"
  }'
```

### 3. Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@example.com",
    "password": "SenhaForte123!"
  }'
```

Isso retornará um `access_token` que você usa para autenticar as próximas requisições.

---

## 📚 Recursos

- [Documentação Supabase](https://supabase.com/docs)
- [Supabase Python Client](https://github.com/supabase-community/supabase-py)
- [FastAPI Docs](https://fastapi.tiangolo.com/)

---

## 🐛 Troubleshooting

### Erro: "relation does not exist"

**Causa:** Tabelas não foram criadas
**Solução:** Execute o script `01_schema.sql`

### Erro: "new row violates row-level security policy"

**Causa:** RLS policies não configuradas
**Solução:** Execute o script `02_rls_policies.sql`

### Erro: "permission denied for schema storage"

**Causa:** Storage policies não configuradas
**Solução:** Execute o script `03_storage_policies.sql`

### Backend não conecta ao Supabase

**Verificar:**

1. Arquivo `.env` existe em `pwa-v2/backend/`
2. Credenciais estão corretas no `.env`
3. URL do Supabase está acessível

---

## 📞 Suporte

Se tiver problemas:

1. Verifique os logs do backend (terminal onde rodou `uvicorn`)
2. Verifique o SQL Editor do Supabase por erros
3. Revise este guia passo a passo

**Projeto:** RelatoRecibo v2.0
**Status:** Backend 90% completo + Supabase configurado ✅
