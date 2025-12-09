# SQL Scripts - RelatoRecibo

## ⚠️ IMPORTANTE

## **Este app atualmente NÃO USA BACKEND ou BANCO DE DADOS SQL**

Os dados são armazenados **localmente no dispositivo móvel** usando AsyncStorage (armazenamento local do React Native).

## Por que os scripts SQL existem?

Estes scripts SQL são fornecidos caso você decida no futuro:

1. **Adicionar sincronização em nuvem** com Supabase/PostgreSQL
2. **Criar um backend** para compartilhar dados entre dispositivos
3. **Implementar backup em servidor**

## Como o app funciona atualmente

```bash
┌─────────────────────┐
│   Dispositivo       │
│                     │
│  ┌──────────────┐   │
│  │ AsyncStorage │   │
│  │  (Local)     │   │
│  └──────────────┘   │
│         ↑           │
│         │           │
│  ┌──────────────┐   │
│  │  App React   │   │
│  │   Native     │   │
│  └──────────────┘   │
└─────────────────────┘
```

**Dados salvos:**

- Relatórios (nome, meta, total, status)
- Recibos (foto, valor, data)
- Tudo armazenado em JSON no dispositivo

**Vantagens:**

- ✅ Funciona offline
- ✅ Não precisa de servidor
- ✅ Sem custos de hospedagem
- ✅ Privacidade total (dados não saem do dispositivo)

**Desvantagens:**

- ❌ Dados perdidos se desinstalar o app
- ❌ Não sincroniza entre dispositivos
- ❌ Sem backup automático

## Como adicionar backend (futuro)

Se você quiser adicionar Supabase no futuro:

### 1. Criar projeto no Supabase

```bash
# Acesse https://supabase.com
# Crie um novo projeto
# Copie a URL e a chave anônima
```

### 2. Executar o schema.sql

```sql
-- No console SQL do Supabase, execute:
-- sql/schema.sql
```

### 3. Configurar o app

```typescript
// Já existe src/services/supabase.ts
// Adicione suas credenciais:

const supabaseUrl = 'SUA_URL_SUPABASE'
const supabaseKey = 'SUA_CHAVE_ANONIMA'
```

### 4. Ativar sincronização

```typescript
// Em src/services/database.ts
// Descomente as chamadas para SupabaseService
```

## Estrutura do Banco (se implementar)

### Tabela `reports`

```sql
id              TEXT PRIMARY KEY
name            TEXT NOT NULL
description     TEXT
target_value    DECIMAL(10, 2)      -- Meta do relatório
total_value     DECIMAL(10, 2)      -- Soma automática dos recibos
receipts_count  INTEGER             -- Quantidade de recibos
status          TEXT                -- draft, completed, sent
created_at      TIMESTAMP
updated_at      TIMESTAMP
completed_at    TIMESTAMP
```

### Tabela `receipts`

```sql
id                  TEXT PRIMARY KEY
report_id           TEXT REFERENCES reports(id)
image_uri           TEXT NOT NULL
cropped_image_uri   TEXT
value               DECIMAL(10, 2)  -- Valor do recibo
description         TEXT
date                TIMESTAMP
created_at          TIMESTAMP
updated_at          TIMESTAMP
```

### Triggers automáticos

- `update_report_totals`: Recalcula total_value e receipts_count automaticamente
- `reports_updated_at`: Atualiza updated_at ao modificar
- `receipts_updated_at`: Atualiza updated_at ao modificar

## Arquivos SQL

### `schema.sql`

Script principal com:

- Criação de tabelas
- Índices para performance
- Triggers para cálculos automáticos
- Constraints e validações

## Perguntas Frequentes

**Q: Preciso executar os scripts SQL agora?**
A: Não! O app funciona perfeitamente sem eles.

**Q: Onde os dados são salvos?**
A: Localmente no dispositivo, em AsyncStorage (similar a localStorage do navegador).

**Q: Os dados são seguros?**
A: Sim, AsyncStorage é criptografado automaticamente pelo sistema operacional (iOS/Android).

**Q: Como fazer backup dos dados?**
A: Atualmente não há backup automático. Você pode exportar PDFs dos relatórios. Se quiser backup automático, implemente o backend com Supabase.

**Q: Posso usar MySQL em vez de PostgreSQL?**
A: Sim, mas precisará adaptar os scripts SQL (principalmente os triggers e funções).
