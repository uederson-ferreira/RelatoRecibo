# Arquitetura Modular - RelatoRecibo

## Princípios de Design

### 1. **Single Responsibility Principle (SRP)**

Cada módulo/classe tem UMA única responsabilidade bem definida.

### 2. **Separation of Concerns**

- **Controllers**: Recebem requests, validam, chamam services
- **Services**: Lógica de negócio pura
- **Repositories**: Acesso a dados (Supabase)
- **Utils**: Funções auxiliares reutilizáveis
- **Models**: Schemas de validação (Pydantic)

### 3. **Tamanho Máximo de Arquivo**

- ❌ Evitar arquivos com > 300 linhas
- ✅ Quebrar em módulos menores e específicos

### 4. **Documentação Obrigatória**

- Docstrings em TODAS as funções/classes
- Comentários explicativos em lógica complexa
- README.md em cada módulo importante
- Type hints SEMPRE

---

## Estrutura de Diretórios Completa

```bash
backend/
├── README.md                           # Documentação principal do backend
├── requirements.txt                    # Dependências de produção
├── requirements-dev.txt                # Dependências de desenvolvimento
├── .env.example                        # Template de variáveis de ambiente
├── Dockerfile                          # Container para deploy
├── pytest.ini                          # Configuração de testes
│
├── app/
│   ├── __init__.py
│   ├── main.py                         # Entry point - FastAPI app (< 100 linhas)
│   ├── config.py                       # Configurações centralizadas
│   ├── dependencies.py                 # Dependency injection
│   │
│   ├── api/                            # 🌐 Camada de API (Controllers)
│   │   ├── __init__.py
│   │   ├── README.md                   # Doc: Como criar endpoints
│   │   │
│   │   └── v1/                         # Versão 1 da API
│   │       ├── __init__.py
│   │       ├── router.py               # Router principal (agrega todos)
│   │       │
│   │       ├── auth/                   # Módulo de autenticação
│   │       │   ├── __init__.py
│   │       │   ├── README.md           # Doc: Autenticação
│   │       │   ├── endpoints.py        # Endpoints: login, signup, logout
│   │       │   └── schemas.py          # Pydantic models específicos de auth
│   │       │
│   │       ├── reports/                # Módulo de relatórios
│   │       │   ├── __init__.py
│   │       │   ├── README.md           # Doc: CRUD de relatórios
│   │       │   ├── endpoints.py        # GET, POST, PUT, DELETE
│   │       │   ├── schemas.py          # Request/Response models
│   │       │   └── dependencies.py     # Deps específicas (validações)
│   │       │
│   │       ├── receipts/               # Módulo de recibos
│   │       │   ├── __init__.py
│   │       │   ├── README.md           # Doc: Upload e OCR
│   │       │   ├── endpoints.py        # Upload, GET, PUT, DELETE
│   │       │   ├── schemas.py          # Receipt models
│   │       │   └── file_handlers.py    # Upload de arquivos
│   │       │
│   │       └── profile/                # Módulo de perfil do usuário
│   │           ├── __init__.py
│   │           ├── README.md
│   │           ├── endpoints.py
│   │           └── schemas.py
│   │
│   ├── core/                           # 🔧 Núcleo da aplicação
│   │   ├── __init__.py
│   │   ├── README.md                   # Doc: Core utilities
│   │   │
│   │   ├── security/                   # Segurança
│   │   │   ├── __init__.py
│   │   │   ├── README.md               # Doc: JWT, hashing
│   │   │   ├── jwt.py                  # Criação/validação JWT
│   │   │   ├── password.py             # Hash de senha
│   │   │   └── dependencies.py         # get_current_user, etc
│   │   │
│   │   ├── middleware/                 # Middlewares
│   │   │   ├── __init__.py
│   │   │   ├── README.md
│   │   │   ├── cors.py                 # CORS config
│   │   │   ├── logging.py              # Request logging
│   │   │   └── error_handler.py        # Error handling
│   │   │
│   │   └── exceptions/                 # Exceções customizadas
│   │       ├── __init__.py
│   │       ├── README.md
│   │       ├── base.py                 # AppException base
│   │       ├── auth.py                 # Auth exceptions
│   │       ├── report.py               # Report exceptions
│   │       └── receipt.py              # Receipt exceptions
│   │
│   ├── models/                         # 📋 Schemas Pydantic
│   │   ├── __init__.py
│   │   ├── README.md                   # Doc: Como criar models
│   │   │
│   │   ├── base.py                     # Base schemas (timestamps, etc)
│   │   ├── user.py                     # User schemas
│   │   │
│   │   ├── report/                     # Report schemas (modularizado)
│   │   │   ├── __init__.py
│   │   │   ├── base.py                 # ReportBase
│   │   │   ├── create.py               # ReportCreate
│   │   │   ├── update.py               # ReportUpdate
│   │   │   ├── response.py             # ReportResponse
│   │   │   └── enums.py                # ReportStatus enum
│   │   │
│   │   └── receipt/                    # Receipt schemas (modularizado)
│   │       ├── __init__.py
│   │       ├── base.py                 # ReceiptBase
│   │       ├── create.py               # ReceiptCreate
│   │       ├── update.py               # ReceiptUpdate
│   │       ├── response.py             # ReceiptResponse
│   │       └── enums.py                # ReceiptStatus enum
│   │
│   ├── services/                       # 💼 Lógica de Negócio
│   │   ├── __init__.py
│   │   ├── README.md                   # Doc: Services pattern
│   │   │
│   │   ├── auth/                       # Auth service
│   │   │   ├── __init__.py
│   │   │   ├── README.md
│   │   │   ├── login.py                # Login logic
│   │   │   ├── signup.py               # Signup logic
│   │   │   └── token.py                # Token management
│   │   │
│   │   ├── report/                     # Report service
│   │   │   ├── __init__.py
│   │   │   ├── README.md
│   │   │   ├── crud.py                 # CRUD operations
│   │   │   ├── calculator.py           # Cálculos (totais, progresso)
│   │   │   └── validator.py            # Validações de negócio
│   │   │
│   │   ├── receipt/                    # Receipt service
│   │   │   ├── __init__.py
│   │   │   ├── README.md
│   │   │   ├── crud.py                 # CRUD operations
│   │   │   ├── upload_handler.py       # Upload logic
│   │   │   └── validator.py            # Validações
│   │   │
│   │   ├── ocr/                        # OCR service (modularizado)
│   │   │   ├── __init__.py
│   │   │   ├── README.md               # Doc: OCR processing
│   │   │   ├── extractor.py            # Text extraction
│   │   │   ├── value_parser.py         # Parse valores monetários
│   │   │   ├── confidence.py           # Cálculo de confiança
│   │   │   └── preprocessor.py         # Preprocessamento de imagem
│   │   │
│   │   ├── pdf/                        # PDF service (modularizado)
│   │   │   ├── __init__.py
│   │   │   ├── README.md               # Doc: PDF generation
│   │   │   ├── generator.py            # Main PDF generator
│   │   │   ├── templates/              # PDF templates
│   │   │   │   ├── report_template.py  # Template de relatório
│   │   │   │   └── styles.py           # Estilos PDF
│   │   │   └── utils.py                # Utilidades PDF
│   │   │
│   │   └── storage/                    # Storage service (Supabase)
│   │       ├── __init__.py
│   │       ├── README.md               # Doc: Storage operations
│   │       ├── uploader.py             # Upload files
│   │       ├── downloader.py           # Download files
│   │       ├── deleter.py              # Delete files
│   │       └── url_generator.py        # Generate signed URLs
│   │
│   ├── repositories/                   # 🗄️ Data Access Layer
│   │   ├── __init__.py
│   │   ├── README.md                   # Doc: Repository pattern
│   │   │
│   │   ├── base.py                     # BaseRepository (métodos comuns)
│   │   ├── supabase_client.py          # Cliente Supabase configurado
│   │   │
│   │   ├── user_repository.py          # User data access
│   │   ├── report_repository.py        # Report data access
│   │   └── receipt_repository.py       # Receipt data access
│   │
│   └── utils/                          # 🛠️ Utilidades
│       ├── __init__.py
│       ├── README.md                   # Doc: Utilities
│       │
│       ├── image/                      # Image utilities
│       │   ├── __init__.py
│       │   ├── README.md
│       │   ├── validator.py            # Validação de imagem
│       │   ├── optimizer.py            # Otimização/compressão
│       │   ├── resizer.py              # Resize
│       │   └── converter.py            # Conversão de formato
│       │
│       ├── formatters/                 # Formatadores
│       │   ├── __init__.py
│       │   ├── currency.py             # Format BRL
│       │   ├── date.py                 # Format dates
│       │   └── text.py                 # Text utils
│       │
│       ├── validators/                 # Validadores customizados
│       │   ├── __init__.py
│       │   ├── file.py                 # File validators
│       │   ├── uuid.py                 # UUID validators
│       │   └── date.py                 # Date validators
│       │
│       └── constants.py                # Constantes globais
│
├── tests/                              # 🧪 Testes
│   ├── __init__.py
│   ├── README.md                       # Doc: Como escrever testes
│   ├── conftest.py                     # Fixtures globais
│   │
│   ├── fixtures/                       # Test data
│   │   ├── images/                     # Imagens de teste
│   │   └── data.py                     # Mock data
│   │
│   ├── unit/                           # Testes unitários
│   │   ├── services/
│   │   │   ├── test_ocr_extractor.py
│   │   │   ├── test_pdf_generator.py
│   │   │   └── test_report_calculator.py
│   │   ├── utils/
│   │   │   ├── test_image_validator.py
│   │   │   └── test_currency_formatter.py
│   │   └── repositories/
│   │       ├── test_report_repository.py
│   │       └── test_receipt_repository.py
│   │
│   └── integration/                    # Testes de integração
│       ├── test_auth_flow.py
│       ├── test_report_crud.py
│       └── test_receipt_upload.py
│
├── scripts/                            # 📜 Scripts utilitários
│   ├── setup_db.py                     # Setup database
│   ├── seed_data.py                    # Popular com dados de teste
│   └── migrate_data.py                 # Migração de dados
│
└── docs/                               # 📚 Documentação adicional
    ├── api_examples.md                 # Exemplos de uso da API
    ├── development.md                  # Guia de desenvolvimento
    └── testing.md                      # Guia de testes
```

---

## Regras de Modularização

### ✅ Arquivo BOM (< 200 linhas, responsabilidade única)

```python
# app/services/ocr/value_parser.py
"""
OCR Value Parser Module

Responsável por extrair valores monetários de texto OCR.
Focado APENAS em parsing de valores, não faz OCR nem validação de negócio.

Author: RelatoRecibo Team
Created: 2025-12-08
"""

import re
from decimal import Decimal
from typing import Optional
from loguru import logger


class ValueParser:
    """
    Parser de valores monetários em Real Brasileiro.

    Identifica padrões como:
    - R$ 123,45
    - R$ 1.234,56
    - Total: R$ 123,45
    """

    # Padrões de regex para valores BRL
    PATTERNS = [
        r'R\$\s*(\d{1,3}(?:\.\d{3})*,\d{2})',  # R$ 1.234,56
        r'total[:\s]+R\$\s*(\d{1,3}(?:\.\d{3})*,\d{2})',  # Total: R$ 1.234,56
        r'valor[:\s]+(\d{1,3}(?:\.\d{3})*,\d{2})',  # Valor: 1.234,56
    ]

    @classmethod
    def parse(cls, text: str) -> Optional[Decimal]:
        """
        Extrai o primeiro valor monetário encontrado no texto.

        Args:
            text: Texto extraído do OCR

        Returns:
            Decimal com o valor encontrado, ou None se não encontrar

        Examples:
            >>> ValueParser.parse("Total: R$ 123,45")
            Decimal('123.45')

            >>> ValueParser.parse("Sem valores aqui")
            None
        """
        if not text:
            logger.warning("Texto vazio fornecido para parsing")
            return None

        for pattern in cls.PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value_str = match.group(1)
                logger.debug(f"Padrão encontrado: {pattern} -> {value_str}")

                # Converte formato BR (1.234,56) para Decimal (1234.56)
                return cls._convert_br_to_decimal(value_str)

        logger.warning(f"Nenhum valor encontrado no texto: {text[:50]}...")
        return None

    @staticmethod
    def _convert_br_to_decimal(value_str: str) -> Decimal:
        """
        Converte string no formato brasileiro para Decimal.

        Args:
            value_str: String no formato "1.234,56"

        Returns:
            Decimal equivalente

        Examples:
            >>> ValueParser._convert_br_to_decimal("1.234,56")
            Decimal('1234.56')
        """
        # Remove pontos de milhar e substitui vírgula por ponto
        normalized = value_str.replace('.', '').replace(',', '.')

        try:
            return Decimal(normalized)
        except Exception as e:
            logger.error(f"Erro ao converter '{value_str}': {e}")
            raise ValueError(f"Formato inválido: {value_str}")
```

### ❌ Arquivo RUIM (monolito, múltiplas responsabilidades)

```python
# ❌ EVITAR: ocr_service.py com 800 linhas
# - Faz OCR
# - Processa imagem
# - Extrai valores
# - Calcula confiança
# - Valida negócio
# - Salva no banco
# - Upload no storage
```

---

## Template de Documentação

### README.md de Módulo

Cada pasta importante deve ter um `README.md`:

```markdown
# Module: OCR Service

## Responsabilidade

Processamento de OCR (Optical Character Recognition) em imagens de recibos.

## Componentes

- `extractor.py`: Extração de texto usando Tesseract
- `value_parser.py`: Parse de valores monetários
- `confidence.py`: Cálculo de score de confiança
- `preprocessor.py`: Preprocessamento de imagens para melhor OCR

## Como Usar

\`\`\`python
from app.services.ocr import OCRService

# Processar recibo
result = await OCRService.process_receipt("path/to/image.jpg")
print(result.text)  # Texto extraído
print(result.value)  # Valor monetário (Decimal)
print(result.confidence)  # Score 0-100
\`\`\`

## Dependências

- pytesseract
- Pillow
- Tesseract OCR (sistema)

## Testes

\`\`\`bash
pytest tests/unit/services/test_ocr_*.py
\`\`\`

## Autor

RelatoRecibo Team

## Última Atualização

2025-12-08
```

---

## Padrão de Comentários

### Docstrings (Google Style)

```python
def calculate_report_progress(total_value: Decimal, target_value: Decimal) -> Decimal:
    """
    Calcula o progresso percentual de um relatório.

    Compara o valor total acumulado com a meta definida e retorna
    a porcentagem de conclusão, limitada a 100%.

    Args:
        total_value: Valor total acumulado dos recibos
        target_value: Meta de valor definida no relatório

    Returns:
        Percentual de progresso (0.00 a 100.00)

    Raises:
        ValueError: Se target_value for zero ou negativo

    Examples:
        >>> calculate_report_progress(Decimal("75.00"), Decimal("100.00"))
        Decimal('75.00')

        >>> calculate_report_progress(Decimal("120.00"), Decimal("100.00"))
        Decimal('100.00')

    Note:
        O resultado é sempre arredondado para 2 casas decimais.
    """
    if target_value <= 0:
        raise ValueError("Meta deve ser maior que zero")

    # Calcula percentual
    percentage = (total_value / target_value) * 100

    # Limita a 100% (não permite > 100%)
    percentage = min(percentage, Decimal("100.00"))

    # Arredonda para 2 casas decimais
    return round(percentage, 2)
```

### Comentários Inline

```python
# ✅ BOM: Explica o PORQUÊ
# Precisamos converter para grayscale porque o Tesseract
# tem melhor precisão com imagens monocromáticas
image = image.convert('L')

# ❌ RUIM: Explica o QUE (código já é auto-explicativo)
# Converte imagem para L (grayscale)
image = image.convert('L')
```

---

## Convenções de Nomenclatura

### Arquivos

- `snake_case.py` - sempre minúsculo
- Nome descritivo: `value_parser.py` não `parser.py`

### Classes

- `PascalCase` - primeira letra maiúscula
- Nome substantivo: `ReceiptValidator` não `ValidateReceipt`

### Funções/Métodos

- `snake_case` - sempre minúsculo
- Nome verbo: `calculate_total()` não `total()`

### Constantes

- `UPPER_SNAKE_CASE` - maiúsculo
- Exemplo: `MAX_FILE_SIZE = 5_000_000`

---

## Checklist para Novo Módulo

Ao criar um novo módulo, certifique-se de:

- [ ] Arquivo tem < 300 linhas
- [ ] Responsabilidade única e clara
- [ ] README.md documentado
- [ ] Todas funções têm docstrings
- [ ] Type hints em TODAS assinaturas
- [ ] Comentários explicam PORQUÊ, não O QUÊ
- [ ] Testes unitários escritos
- [ ] Exemplos de uso no README
- [ ] Logging adequado (debug, info, error)
- [ ] Tratamento de erros específico

---

## Próximos Passos

1. Implementar estrutura de diretórios
2. Criar templates de código para cada camada
3. Implementar módulos um por um
4. Testes para cada módulo
5. Integração gradual

Veja `backend-code-templates.md` para templates prontos de cada tipo de módulo.
