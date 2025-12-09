# Code Templates - RelatoRecibo Backend

Templates de código bem documentados para cada camada da aplicação.

---

## 1. Repository (Data Access Layer)

### Template: `app/repositories/report_repository.py`

```python
"""
Report Repository Module

Camada de acesso a dados para relatórios.
Responsável APENAS por operações CRUD no Supabase.
Não contém lógica de negócio.

Author: RelatoRecibo Team
Created: 2025-12-08
"""

from typing import List, Optional
from uuid import UUID
from loguru import logger

from app.repositories.base import BaseRepository
from app.core.exceptions.report import ReportNotFoundError


class ReportRepository(BaseRepository):
    """
    Repositório de Relatórios.

    Gerencia persistência de dados de relatórios no Supabase.
    Usa Row Level Security (RLS) para garantir isolamento por usuário.
    """

    TABLE_NAME = "reports"

    async def find_by_id(self, report_id: UUID, user_id: UUID) -> Optional[dict]:
        """
        Busca um relatório por ID.

        Args:
            report_id: UUID do relatório
            user_id: UUID do usuário (para RLS)

        Returns:
            Dict com dados do relatório ou None se não encontrado

        Raises:
            Exception: Se houver erro na comunicação com Supabase
        """
        try:
            # RLS garante que apenas o dono do relatório pode acessá-lo
            response = (
                self.client
                .table(self.TABLE_NAME)
                .select("*")
                .eq("id", str(report_id))
                .eq("user_id", str(user_id))
                .single()
                .execute()
            )

            logger.debug(f"Report {report_id} found for user {user_id}")
            return response.data

        except Exception as e:
            # Se não encontrou, retorna None ao invés de erro
            if "not found" in str(e).lower():
                logger.warning(f"Report {report_id} not found")
                return None

            logger.error(f"Error fetching report {report_id}: {e}")
            raise

    async def find_all_by_user(
        self,
        user_id: UUID,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[dict]:
        """
        Busca todos os relatórios de um usuário.

        Args:
            user_id: UUID do usuário
            status: Filtro opcional de status (draft, completed, archived)
            limit: Número máximo de resultados (default: 20)
            offset: Offset para paginação (default: 0)

        Returns:
            Lista de dicts com relatórios

        Examples:
            >>> reports = await repo.find_all_by_user(
            ...     user_id=uuid.uuid4(),
            ...     status="draft",
            ...     limit=10
            ... )
        """
        try:
            query = (
                self.client
                .table(self.TABLE_NAME)
                .select("*")
                .eq("user_id", str(user_id))
                .order("created_at", desc=True)
                .range(offset, offset + limit - 1)
            )

            # Filtro opcional por status
            if status:
                query = query.eq("status", status)

            response = query.execute()

            logger.info(f"Found {len(response.data)} reports for user {user_id}")
            return response.data

        except Exception as e:
            logger.error(f"Error fetching reports for user {user_id}: {e}")
            raise

    async def create(self, report_data: dict) -> dict:
        """
        Cria um novo relatório.

        Args:
            report_data: Dict com dados do relatório (name, user_id, etc)

        Returns:
            Dict com relatório criado (incluindo ID gerado)

        Raises:
            Exception: Se houver erro na criação

        Note:
            - O campo 'created_at' é gerado automaticamente pelo banco
            - O campo 'total_value' é inicializado como 0
            - O campo 'status' é inicializado como 'draft'
        """
        try:
            response = (
                self.client
                .table(self.TABLE_NAME)
                .insert(report_data)
                .execute()
            )

            created_report = response.data[0]
            logger.info(f"Report created: {created_report['id']}")

            return created_report

        except Exception as e:
            logger.error(f"Error creating report: {e}")
            raise

    async def update(
        self,
        report_id: UUID,
        user_id: UUID,
        update_data: dict
    ) -> Optional[dict]:
        """
        Atualiza um relatório existente.

        Args:
            report_id: UUID do relatório
            user_id: UUID do usuário (para RLS)
            update_data: Dict com campos a atualizar

        Returns:
            Dict com relatório atualizado ou None se não encontrado

        Note:
            - O campo 'updated_at' é atualizado automaticamente via trigger
            - RLS previne atualização de relatórios de outros usuários
        """
        try:
            response = (
                self.client
                .table(self.TABLE_NAME)
                .update(update_data)
                .eq("id", str(report_id))
                .eq("user_id", str(user_id))
                .execute()
            )

            if not response.data:
                logger.warning(f"Report {report_id} not found for update")
                return None

            updated_report = response.data[0]
            logger.info(f"Report updated: {report_id}")

            return updated_report

        except Exception as e:
            logger.error(f"Error updating report {report_id}: {e}")
            raise

    async def delete(self, report_id: UUID, user_id: UUID) -> bool:
        """
        Deleta um relatório.

        Args:
            report_id: UUID do relatório
            user_id: UUID do usuário (para RLS)

        Returns:
            True se deletado com sucesso, False se não encontrado

        Note:
            - Recibos associados são deletados em CASCADE
            - Imagens do storage devem ser deletadas via trigger
        """
        try:
            response = (
                self.client
                .table(self.TABLE_NAME)
                .delete()
                .eq("id", str(report_id))
                .eq("user_id", str(user_id))
                .execute()
            )

            success = len(response.data) > 0

            if success:
                logger.info(f"Report deleted: {report_id}")
            else:
                logger.warning(f"Report {report_id} not found for deletion")

            return success

        except Exception as e:
            logger.error(f"Error deleting report {report_id}: {e}")
            raise
```

---

## 2. Service (Business Logic)

### Template: `app/services/report/calculator.py`

```python
"""
Report Calculator Service

Módulo responsável por cálculos relacionados a relatórios.
Focado APENAS em lógica de cálculo, sem acesso a dados.

Author: RelatoRecibo Team
Created: 2025-12-08
"""

from decimal import Decimal
from typing import List
from loguru import logger


class ReportCalculator:
    """
    Calculadora de métricas de relatórios.

    Realiza cálculos como:
    - Progresso em relação à meta
    - Totais e médias
    - Estatísticas
    """

    @staticmethod
    def calculate_progress(total_value: Decimal, target_value: Decimal) -> Decimal:
        """
        Calcula o progresso percentual de um relatório.

        Formula: (total_value / target_value) * 100
        Limitado a máximo de 100% mesmo se exceder a meta.

        Args:
            total_value: Valor total acumulado
            target_value: Meta de valor definida

        Returns:
            Percentual de 0.00 a 100.00

        Raises:
            ValueError: Se target_value for <= 0

        Examples:
            >>> ReportCalculator.calculate_progress(
            ...     Decimal("75.00"),
            ...     Decimal("100.00")
            ... )
            Decimal('75.00')

            >>> ReportCalculator.calculate_progress(
            ...     Decimal("120.00"),
            ...     Decimal("100.00")
            ... )
            Decimal('100.00')
        """
        # Validação de entrada
        if target_value <= 0:
            logger.error(f"Invalid target_value: {target_value}")
            raise ValueError("Meta deve ser maior que zero")

        # Cálculo do percentual
        percentage = (total_value / target_value) * Decimal("100")

        # Limita a 100% (não permite overflow)
        # Útil para UIs que mostram barras de progresso
        percentage = min(percentage, Decimal("100.00"))

        # Arredonda para 2 casas decimais
        result = round(percentage, 2)

        logger.debug(
            f"Progress calculated: {total_value}/{target_value} = {result}%"
        )

        return result

    @staticmethod
    def calculate_average_receipt_value(
        receipts: List[dict]
    ) -> Decimal:
        """
        Calcula o valor médio dos recibos.

        Args:
            receipts: Lista de dicts com recibos (cada um com campo 'value')

        Returns:
            Valor médio ou Decimal("0.00") se lista vazia

        Examples:
            >>> receipts = [
            ...     {"value": Decimal("10.00")},
            ...     {"value": Decimal("20.00")},
            ...     {"value": Decimal("30.00")}
            ... ]
            >>> ReportCalculator.calculate_average_receipt_value(receipts)
            Decimal('20.00')
        """
        if not receipts:
            logger.warning("Empty receipts list for average calculation")
            return Decimal("0.00")

        # Extrai valores e converte para Decimal
        values = [Decimal(str(r["value"])) for r in receipts]

        # Calcula média
        total = sum(values)
        count = len(values)
        average = total / count

        # Arredonda para 2 casas decimais
        result = round(average, 2)

        logger.debug(f"Average receipt value: {result} ({count} receipts)")

        return result

    @staticmethod
    def is_target_achieved(total_value: Decimal, target_value: Decimal) -> bool:
        """
        Verifica se a meta foi atingida ou superada.

        Args:
            total_value: Valor total acumulado
            target_value: Meta de valor

        Returns:
            True se meta atingida, False caso contrário

        Examples:
            >>> ReportCalculator.is_target_achieved(
            ...     Decimal("100.00"),
            ...     Decimal("100.00")
            ... )
            True

            >>> ReportCalculator.is_target_achieved(
            ...     Decimal("99.99"),
            ...     Decimal("100.00")
            ... )
            False
        """
        achieved = total_value >= target_value

        logger.debug(
            f"Target achieved: {achieved} ({total_value} >= {target_value})"
        )

        return achieved
```

---

## 3. API Endpoint (Controller)

### Template: `app/api/v1/reports/endpoints.py`

```python
"""
Reports API Endpoints

Endpoints para gerenciamento de relatórios.
Camada de apresentação - recebe requests, valida, chama services.

Author: RelatoRecibo Team
Created: 2025-12-08
"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from loguru import logger

from app.core.security.dependencies import get_current_user
from app.models.user import User
from app.models.report.create import ReportCreate
from app.models.report.update import ReportUpdate
from app.models.report.response import ReportResponse, ReportDetailResponse
from app.services.report.crud import ReportCRUDService
from app.core.exceptions.report import ReportNotFoundError


# Router para este módulo
router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("", response_model=List[ReportResponse])
async def list_reports(
    status: str | None = Query(
        None,
        description="Filtrar por status (draft, completed, archived)"
    ),
    limit: int = Query(20, ge=1, le=100, description="Número de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginação"),
    current_user: User = Depends(get_current_user)
):
    """
    Lista todos os relatórios do usuário autenticado.

    **Filtros opcionais:**
    - status: draft, completed ou archived
    - limit: 1-100 (padrão: 20)
    - offset: para paginação (padrão: 0)

    **Retorna:**
    - Lista de relatórios ordenados por data de criação (mais recente primeiro)
    """
    try:
        logger.info(
            f"Listing reports for user {current_user.id} "
            f"(status={status}, limit={limit}, offset={offset})"
        )

        # Delega lógica para service
        reports = await ReportCRUDService.list_reports(
            user_id=current_user.id,
            status=status,
            limit=limit,
            offset=offset
        )

        logger.info(f"Found {len(reports)} reports")
        return reports

    except Exception as e:
        logger.error(f"Error listing reports: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao listar relatórios"
        )


@router.get("/{report_id}", response_model=ReportDetailResponse)
async def get_report(
    report_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """
    Busca um relatório específico por ID.

    **Retorna:**
    - Relatório completo com estatísticas (total, média, etc)

    **Errors:**
    - 404: Relatório não encontrado ou não pertence ao usuário
    """
    try:
        logger.info(f"Fetching report {report_id} for user {current_user.id}")

        # Delega para service
        report = await ReportCRUDService.get_report_detail(
            report_id=report_id,
            user_id=current_user.id
        )

        logger.info(f"Report {report_id} fetched successfully")
        return report

    except ReportNotFoundError:
        # Exceção customizada vinda do service
        logger.warning(f"Report {report_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relatório não encontrado"
        )

    except Exception as e:
        logger.error(f"Error fetching report {report_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar relatório"
        )


@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    report_data: ReportCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Cria um novo relatório.

    **Body:**
    ```json
    {
      "name": "Viagem SP - Dez/2025",
      "description": "Despesas da viagem",
      "target_value": 5000.00
    }
    ```

    **Retorna:**
    - Relatório criado com status 'draft'
    - total_value = 0.00 (inicial)
    - receipts_count = 0 (inicial)
    """
    try:
        logger.info(f"Creating report for user {current_user.id}: {report_data.name}")

        # Delega para service
        report = await ReportCRUDService.create_report(
            user_id=current_user.id,
            report_data=report_data
        )

        logger.info(f"Report created: {report.id}")
        return report

    except Exception as e:
        logger.error(f"Error creating report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar relatório"
        )


@router.put("/{report_id}", response_model=ReportResponse)
async def update_report(
    report_id: UUID,
    report_data: ReportUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Atualiza um relatório existente.

    **Campos atualizáveis:**
    - name
    - description
    - target_value
    - status

    **Note:**
    - total_value e receipts_count são calculados automaticamente
    """
    try:
        logger.info(f"Updating report {report_id} for user {current_user.id}")

        # Delega para service
        report = await ReportCRUDService.update_report(
            report_id=report_id,
            user_id=current_user.id,
            report_data=report_data
        )

        logger.info(f"Report {report_id} updated successfully")
        return report

    except ReportNotFoundError:
        logger.warning(f"Report {report_id} not found for update")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relatório não encontrado"
        )

    except Exception as e:
        logger.error(f"Error updating report {report_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar relatório"
        )


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """
    Deleta um relatório e todos os recibos associados.

    **Atenção:**
    - Esta ação é IRREVERSÍVEL
    - Todos os recibos do relatório serão deletados
    - Imagens do storage serão removidas
    """
    try:
        logger.info(f"Deleting report {report_id} for user {current_user.id}")

        # Delega para service
        await ReportCRUDService.delete_report(
            report_id=report_id,
            user_id=current_user.id
        )

        logger.info(f"Report {report_id} deleted successfully")
        # 204 No Content não retorna body

    except ReportNotFoundError:
        logger.warning(f"Report {report_id} not found for deletion")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relatório não encontrado"
        )

    except Exception as e:
        logger.error(f"Error deleting report {report_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao deletar relatório"
        )
```

---

## 4. Pydantic Model (Schema)

### Template: `app/models/report/create.py`

```python
"""
Report Create Schema

Schema Pydantic para criação de relatórios.
Validação automática de dados de entrada.

Author: RelatoRecibo Team
Created: 2025-12-08
"""

from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, validator


class ReportCreate(BaseModel):
    """
    Schema para criação de um relatório.

    **Campos obrigatórios:**
    - name: Nome do relatório

    **Campos opcionais:**
    - description: Descrição detalhada
    - target_value: Meta de valor (se houver)

    **Validações:**
    - name: 3-200 caracteres, não vazio
    - target_value: se fornecido, deve ser > 0
    """

    name: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="Nome do relatório",
        example="Viagem São Paulo - Dezembro 2025"
    )

    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Descrição detalhada do relatório",
        example="Despesas da viagem de negócios para reunião com cliente"
    )

    target_value: Optional[Decimal] = Field(
        None,
        gt=0,
        description="Meta de valor (opcional)",
        example=5000.00
    )

    @validator('name')
    def validate_name(cls, v: str) -> str:
        """
        Valida o campo 'name'.

        Regras:
        - Não pode ser apenas espaços em branco
        - Remove espaços extras no início/fim

        Args:
            v: Valor do campo name

        Returns:
            Nome validado e normalizado

        Raises:
            ValueError: Se nome for inválido
        """
        # Remove espaços extras
        v = v.strip()

        # Valida que não é vazio após strip
        if not v:
            raise ValueError("Nome não pode ser vazio")

        return v

    @validator('target_value')
    def validate_target_value(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """
        Valida o campo 'target_value'.

        Regras:
        - Se fornecido, deve ter no máximo 2 casas decimais
        - Deve ser positivo (validado por Field(gt=0))

        Args:
            v: Valor do campo target_value

        Returns:
            Valor validado

        Raises:
            ValueError: Se formato inválido
        """
        if v is None:
            return v

        # Valida máximo de 2 casas decimais
        if v.as_tuple().exponent < -2:
            raise ValueError(
                "Meta deve ter no máximo 2 casas decimais"
            )

        return v

    class Config:
        """
        Configuração do Pydantic model.
        """
        # Exemplo para documentação automática (Swagger)
        schema_extra = {
            "example": {
                "name": "Viagem São Paulo - Dezembro 2025",
                "description": "Despesas da viagem de negócios",
                "target_value": 5000.00
            }
        }
```

---

## 5. Utility Module

### Template: `app/utils/image/validator.py`

```python
"""
Image Validator Utility

Validação de arquivos de imagem.
Verifica tipo, tamanho, dimensões, etc.

Author: RelatoRecibo Team
Created: 2025-12-08
"""

import imghdr
from pathlib import Path
from typing import BinaryIO
from fastapi import UploadFile
from loguru import logger

from app.config import settings
from app.core.exceptions.receipt import InvalidImageError


class ImageValidator:
    """
    Validador de imagens para upload de recibos.

    Valida:
    - Tipo de arquivo (MIME type)
    - Extensão
    - Tamanho
    - Formato real da imagem (via magic bytes)
    """

    # Formatos permitidos
    ALLOWED_FORMATS = {"jpeg", "jpg", "png", "webp"}

    # MIME types permitidos
    ALLOWED_MIME_TYPES = {
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/webp"
    }

    @classmethod
    async def validate_upload(cls, file: UploadFile) -> None:
        """
        Valida um arquivo de upload.

        Realiza todas as validações:
        - MIME type
        - Extensão
        - Tamanho
        - Formato real (magic bytes)

        Args:
            file: Arquivo enviado via FastAPI

        Raises:
            InvalidImageError: Se alguma validação falhar

        Examples:
            >>> await ImageValidator.validate_upload(upload_file)
            # None se OK, InvalidImageError se falhar
        """
        logger.debug(f"Validating image: {file.filename}")

        # 1. Valida MIME type
        cls._validate_mime_type(file.content_type)

        # 2. Valida extensão
        cls._validate_extension(file.filename)

        # 3. Valida tamanho
        await cls._validate_size(file)

        # 4. Valida formato real (magic bytes)
        # Importante: previne upload de arquivo malicioso com extensão falsa
        await cls._validate_real_format(file)

        logger.info(f"Image validation passed: {file.filename}")

    @staticmethod
    def _validate_mime_type(mime_type: str) -> None:
        """
        Valida MIME type do arquivo.

        Args:
            mime_type: Content-Type do arquivo

        Raises:
            InvalidImageError: Se MIME type não permitido
        """
        if mime_type not in ImageValidator.ALLOWED_MIME_TYPES:
            logger.warning(f"Invalid MIME type: {mime_type}")
            raise InvalidImageError(
                f"Tipo de arquivo não permitido: {mime_type}. "
                f"Permitidos: {', '.join(ImageValidator.ALLOWED_MIME_TYPES)}"
            )

    @staticmethod
    def _validate_extension(filename: str) -> None:
        """
        Valida extensão do arquivo.

        Args:
            filename: Nome do arquivo

        Raises:
            InvalidImageError: Se extensão não permitida
        """
        # Extrai extensão (sem o ponto)
        extension = Path(filename).suffix.lower().lstrip('.')

        if extension not in ImageValidator.ALLOWED_FORMATS:
            logger.warning(f"Invalid extension: {extension}")
            raise InvalidImageError(
                f"Extensão não permitida: .{extension}. "
                f"Permitidas: {', '.join(ImageValidator.ALLOWED_FORMATS)}"
            )

    @staticmethod
    async def _validate_size(file: UploadFile) -> None:
        """
        Valida tamanho do arquivo.

        Lê o arquivo em chunks para não carregar tudo na memória.

        Args:
            file: Arquivo de upload

        Raises:
            InvalidImageError: Se arquivo muito grande

        Note:
            Após a validação, reseta o cursor do arquivo para o início
            para permitir leitura posterior.
        """
        # Lê arquivo em chunks
        size = 0
        chunk_size = 1024 * 1024  # 1MB chunks

        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break

            size += len(chunk)

            # Verifica se excedeu limite
            if size > settings.MAX_UPLOAD_SIZE:
                logger.warning(f"File too large: {size} bytes")
                raise InvalidImageError(
                    f"Arquivo muito grande: {size / (1024*1024):.2f}MB. "
                    f"Máximo permitido: {settings.MAX_UPLOAD_SIZE / (1024*1024):.2f}MB"
                )

        # IMPORTANTE: Reseta cursor para início
        await file.seek(0)

        logger.debug(f"File size OK: {size / (1024*1024):.2f}MB")

    @staticmethod
    async def _validate_real_format(file: UploadFile) -> None:
        """
        Valida formato real do arquivo via magic bytes.

        Previne ataque: arquivo.exe renomeado para arquivo.jpg

        Args:
            file: Arquivo de upload

        Raises:
            InvalidImageError: Se formato real não for imagem válida

        Note:
            Usa biblioteca imghdr para detectar formato via magic bytes.
            Reseta cursor após validação.
        """
        # Lê primeiros bytes para detecção
        header = await file.read(512)
        await file.seek(0)  # Reseta

        # Detecta formato real via magic bytes
        # imghdr retorna None se não for imagem válida
        real_format = imghdr.what(None, h=header)

        if real_format not in ImageValidator.ALLOWED_FORMATS:
            logger.warning(f"Real format mismatch: {real_format}")
            raise InvalidImageError(
                "Arquivo não é uma imagem válida ou está corrompido"
            )

        logger.debug(f"Real format validated: {real_format}")
```

---

## Próximos Passos

Agora você tem templates completos para:

- ✅ Repositories (acesso a dados)
- ✅ Services (lógica de negócio)
- ✅ Endpoints (controllers)
- ✅ Models (schemas Pydantic)
- ✅ Utils (utilitários)

**Cada arquivo:**

- < 300 linhas
- Responsabilidade única
- Bem documentado
- Type hints completos
- Logging apropriado
- Tratamento de erros

Quer que eu crie mais templates ou comece a implementação real?
