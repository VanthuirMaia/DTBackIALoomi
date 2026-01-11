"""
Schemas Pydantic para o endpoint de chat.
"""

from typing import Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request para o endpoint de chat."""

    message: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Mensagem do usuário",
        json_schema_extra={"example": "Quero pintar meu quarto, algo fácil de limpar e sem cheiro forte"}
    )
    session_id: Optional[str] = Field(
        default=None,
        description="ID da sessão para manter histórico da conversa"
    )


class ProductResponse(BaseModel):
    """Produto retornado na resposta."""

    id: int
    nome: str
    cor: str
    tipo_superficie: str
    ambiente: str
    acabamento: str
    features: str
    linha: str
    relevancia: float = Field(description="Score de relevância (0-1)")


class ImageResponse(BaseModel):
    """Imagem gerada pelo DALL-E."""

    url: str = Field(description="URL da imagem gerada")
    ambiente: str = Field(description="Tipo de ambiente visualizado")
    cor: str = Field(description="Cor utilizada na visualização")


class ChatResponse(BaseModel):
    """Response do endpoint de chat."""

    response: str = Field(description="Resposta do assistente")
    products: list[ProductResponse] = Field(description="Produtos relacionados")
    query: str = Field(description="Pergunta original do usuário")
    session_id: Optional[str] = Field(default=None, description="ID da sessão")
    images: list[ImageResponse] = Field(default=[], description="Imagens geradas")


class ClearSessionRequest(BaseModel):
    """Request para limpar sessão."""

    session_id: str = Field(..., description="ID da sessão a ser limpa")


class ClearSessionResponse(BaseModel):
    """Response da limpeza de sessão."""

    success: bool
    message: str
