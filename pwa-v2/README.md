# RelatoRecibo v2.0 🚀

> **PWA moderna para gestão de recibos e prestação de contas com OCR**

Sistema completo de relatórios de despesas com upload de fotos, reconhecimento automático de valores (OCR) e geração de PDF profissional. Arquitetura moderna com frontend React e backend Python FastAPI.

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-teal)
![React](https://img.shields.io/badge/React-18-61DAFB)
![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-success)

---

## 📌 Importante: Versão 2.0

Esta é a **versão 2.0** com arquitetura moderna:

- ✅ **Backend Python + FastAPI** (OCR server-side mais rápido)
- ✅ **Frontend React + TypeScript** (componentizado)
- ✅ **Supabase** (PostgreSQL + Auth + Storage)
- ✅ **Modular e escalável**

📁 A **versão 1.0 (vanilla)** está arquivada em [`old-version/`](old-version/)

## 🚀 Stack Tecnológica

### Frontend (PWA)

- **React 18** + **TypeScript** + **Vite**
- **TailwindCSS** + **Shadcn/ui** (componentes)
- **TanStack Query** (cache e sincronização)
- **Zustand** (state management)
- **PWA** (offline-first com Workbox)
- **React Router v6** (navegação)

### Backend (API)

- **Python 3.11+** + **FastAPI**
- **pytesseract** (OCR server-side - mais rápido!)
- **ReportLab** (geração de PDF profissional)
- **Pillow** (processamento de imagens)
- **Pydantic** (validação automática)
- **Uvicorn** (ASGI server)

### Database & Services

- **Supabase** (PostgreSQL + Storage + Auth)
- **Row Level Security (RLS)** - isolamento por usuário
- **Storage Policies** - imagens privadas por usuário

### Deploy (Free Tier)

- **Backend:** Render.com (750h/mês grátis)
- **Frontend:** Vercel (ilimitado grátis)
- **Database:** Supabase (500MB grátis)

## 🚀 Como Usar

### 1. Gerar Ícones (Opcional)

```bash
# Abra no navegador
open generate-icons.html

# Ou visite diretamente
file:///caminho/para/generate-icons.html
```

Baixe os ícones 192x192 e 512x512, renomeie e coloque na pasta raiz.

### 2. Servir Localmente

## **Opção A: Python**

```bash
# Python 3
python3 -m http.server 8000

# Acesse: http://localhost:8000
```

## **Opção B: Node.js**

```bash
# Instale http-server globalmente
npm install -g http-server

# Rode
http-server -p 8000

# Acesse: http://localhost:8000
```

## **Opção C: VS Code Live Server**

1. Instale extensão "Live Server"
2. Clique direito em `index.html`
3. "Open with Live Server"

### 3. Testar no Celular

1. **Encontre seu IP local**:

   ```bash
   # Mac/Linux
   ifconfig | grep inet

   # Windows
   ipconfig
   ```

2. **Acesse do celular**:

   ```bash
   http://SEU_IP:8000
   ```

   Exemplo: `http://192.168.1.100:8000`

3. **Instalar como PWA**:
   - Chrome Android: Menu → "Adicionar à tela inicial"
   - Safari iOS: Compartilhar → "Adicionar à Tela Inicial"

## 🌐 Deploy (Produção)

### Opção 1: Vercel (Recomendado)

```bash
# Instale Vercel CLI
npm install -g vercel

# Na pasta do PWA
vercel

# Siga os passos
# ✅ Deploy em ~30 segundos!
```

### Opção 2: Netlify

1. Arraste a pasta para [netlify.com/drop](https://app.netlify.com/drop)
2. ✅ Pronto! URL gerada

### Opção 3: GitHub Pages

```bash
# Crie repositório no GitHub
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/seu-usuario/relatorecibo.git
git push -u origin main

# Vá em Settings → Pages
# Source: main branch
# ✅ Disponível em: https://seu-usuario.github.io/relatorecibo
```

## 📱 Como Usar o App

### 1. Criar um Relatório

```bash
1. Tela inicial → "+ Novo"
2. Digite nome do relatório
3. (Opcional) Defina meta de valor
4. "Criar"
```

### 2. Adicionar Recibos

```bash
1. Clique no relatório
2. Botão "+" no canto inferior
3. "Tirar Foto" ou "Escolher da Galeria"
4. OCR detecta valor automaticamente! ✨
5. Confirme ou edite
6. Salvo!
```

### 3. Visualizar Fotos

```bash
1. Clique em qualquer recibo
2. Foto abre em tela cheia
3. Clique fora para fechar
```

### 4. Gerar PDF

```bash
1. No relatório com recibos
2. "Gerar PDF"
3. PDF baixado automaticamente!
```

## 📁 Estrutura do Projeto

```bash
RelatoRecibo-PWA/
├── index.html              # App principal
├── styles.css              # Estilos
├── app.js                  # Lógica do app
├── db.js                   # IndexedDB (Dexie)
├── ocr.js                  # OCR com Tesseract.js ⭐
├── pdf.js                  # Geração de PDF
├── sw.js                   # Service Worker
├── manifest.json           # PWA manifest
├── generate-icons.html     # Gerador de ícones
├── icon-192.png            # Ícone pequeno
├── icon-512.png            # Ícone grande
└── README.md               # Este arquivo
```

## 🎨 Screenshots

### Tela Principal

- Lista de relatórios
- Indicador de progresso da meta
- Status colorido

### Detalhes do Relatório

- Grid de recibos com fotos
- Estatísticas (total, média, progresso)
- Botões para gerar PDF e excluir

### Captura de Recibo

- Botão "Tirar Foto"
- Botão "Escolher da Galeria"
- **OCR automático** ✨

## 🔬 Como o OCR Funciona

```javascript
// ocr.js (simplificado)
const { data } = await Tesseract.recognize(image, 'por');

// Texto extraído: "RECIBO\nValor: R$ 150,00\nData: 08/12/2025"

// Regex para detectar valores
const patterns = [
    /R\$\s*(\d+[.,]\d{2})/gi,
    /valor[:\s]+(\d+[.,]\d{2})/gi,
    /total[:\s]+(\d+[.,]\d{2})/gi
];

// Retorna: 150.00
```

**Funciona com:**

- R$ 150,00
- Valor: 150,00
- Total: R$ 150.00
- 150,00 reais

## 💾 Armazenamento

**IndexedDB** armazena localmente:

- Relatórios (nome, meta, total, status)
- Recibos (foto em base64, valor, data)

**Não sincroniza** entre dispositivos (local apenas).

## 🔒 Privacidade

- ✅ **100% local** - dados não saem do dispositivo
- ✅ **Sem servidor** - não precisa de backend
- ✅ **Sem rastreamento** - zero analytics
- ✅ **Offline first** - funciona sem internet

## 🆚 PWA vs React Native

| Característica | PWA | React Native |
|---|---|---|
| **OCR Funcionando** | ✅ Tesseract.js | ❌ Complexo |
| **Câmera** | ✅ 1 linha HTML | ⚠️ Bibliotecas nativas |
| **Deploy** | ✅ 5 minutos | ❌ Dias (lojas) |
| **Atualização** | ✅ Instantânea | ❌ Aprovação lojas |
| **Debug** | ✅ DevTools | ⚠️ Emuladores |
| **Tamanho** | ✅ ~2MB | ❌ ~50MB |
| **Funciona offline** | ✅ Sim | ✅ Sim |
| **Instalável** | ✅ Sim | ✅ Sim |
| **Acesso hardware** | ⚠️ Limitado | ✅ Total |
| **App Store** | ❌ Não | ✅ Sim |

## 🐛 Problemas Conhecidos

Nenhum! 🎉

O OCR funciona de verdade, a câmera funciona, o PDF funciona!

## 🔮 Melhorias Futuras

- [ ] Sincronização opcional com Supabase
- [ ] Categorias de recibos
- [ ] Filtros por data
- [ ] Exportar para Excel/CSV
- [ ] Tema escuro
- [ ] Múltiplas moedas
- [ ] Compartilhar relatórios

## 📄 Licença

MIT - Livre para uso pessoal e comercial

## 🤝 Contribuindo

Pull requests são bem-vindos!

## 💡 Dicas de Uso

### Para melhores resultados de OCR

1. 📸 Use boa iluminação
2. 📏 Foto centralizada e nítida
3. 🎯 Evite sombras e reflexos
4. 📱 Foto na vertical

### Performance

- OCR processa em ~2-5 segundos
- Primeira execução carrega modelo (~20MB)
- Subsequentes são mais rápidas (cache)

## ❓ FAQ

**Q: Preciso instalar algo?**
A: Não! Apenas abra no navegador.

**Q: Funciona offline?**
A: Sim! Service Worker cacheia tudo.

**Q: O OCR é real?**
A: **SIM!** Tesseract.js detecta valores de verdade.

**Q: Onde os dados são salvos?**
A: IndexedDB do navegador (local no dispositivo).

**Q: Posso usar no iPhone?**
A: Sim! Safari suporta PWA e câmera.

**Q: Como fazer backup?**
A: Exporte PDFs. Sync com Supabase virá no futuro.

**Q: Posso hospedar no meu servidor?**
A: Sim! É só HTML/CSS/JS estático.

---

## **Desenvolvido com 💙 para simplicidade**

Nenhum npm install, nenhum node_modules, nenhuma dor de cabeça! 🎉
