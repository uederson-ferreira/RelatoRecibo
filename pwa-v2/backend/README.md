# RelatoRecibo Backend

## 🚀 Como usar

### 1. Ativar o ambiente virtual

```bash
# Opção 1: Usando source diretamente
source venv/bin/activate

# Opção 2: Usando o script helper
./activate.sh
```

### 2. Instalar dependências (se necessário)

```bash
pip install -r requirements.txt
```

### 3. Configurar variáveis de ambiente

Certifique-se de que o arquivo `.env` está configurado com:

- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `JWT_SECRET_KEY`

### 4. Rodar o servidor

```bash
# Modo desenvolvimento (com reload automático)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Ou usando Python diretamente
python -m app.main
```

### 5. Acessar a documentação

Após iniciar o servidor, acesse:

- **Swagger UI**: <http://localhost:8000/api/docs>
- **ReDoc**: <http://localhost:8000/api/redoc>
- **Health Check**: <http://localhost:8000/health>

## 📝 Comandos úteis

```bash
# Desativar ambiente virtual
deactivate

# Verificar se está ativado
which python  # Deve mostrar o caminho do venv

# Instalar nova dependência
pip install nome-do-pacote
pip freeze > requirements.txt  # Atualizar requirements.txt
```

## 🔧 Troubleshooting

### Problema: "venv/bin/activate: No such file or directory"

**Solução**: Crie o ambiente virtual primeiro:

```bash
python3 -m venv venv
```

### Problema: "Permission denied"

**Solução**: Dê permissão de execução:

```bash
chmod +x venv/bin/activate
```
