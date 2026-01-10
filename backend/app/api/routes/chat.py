"""
Endpoints do chatbot de recomendacao de tintas.
"""

import uuid
from fastapi import APIRouter, HTTPException, Depends

from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ClearSessionRequest,
    ClearSessionResponse,
    ImageResponse,
)
from app.services.agent_service import get_agent_service, clear_session
from app.models.user import User
from app.api.deps import get_authenticated_user

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post(
    "",
    response_model=ChatResponse,
    summary="Enviar mensagem para o assistente",
    description="Envia uma pergunta sobre tintas e recebe uma recomendacao personalizada. Requer autenticacao."
)
def chat(
    request: ChatRequest,
    user: User = Depends(get_authenticated_user)
) -> ChatResponse:
    """
    Processa uma mensagem do usuario e retorna recomendacao.

    - Busca produtos relevantes via RAG
    - Gera resposta contextualizada via LLM
    - Mantem historico se session_id fornecido
    - Requer usuario autenticado
    """
    try:
        # Usa user.id como parte do session_id para isolar conversas
        session_id = request.session_id or f"user-{user.id}-{uuid.uuid4()}"
        agent = get_agent_service(session_id)

        result = agent.process_query(request.message)

        # Converte dicts de imagens para ImageResponse
        images = [
            ImageResponse(url=img["url"], ambiente=img["ambiente"], cor=img["cor"])
            for img in result.get("images", [])
        ]

        return ChatResponse(
            response=result["response"],
            products=result["products"],
            query=result["query"],
            session_id=session_id,
            images=images
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar mensagem: {str(e)}")


@router.post(
    "/clear",
    response_model=ClearSessionResponse,
    summary="Limpar historico da sessao",
    description="Remove o historico de conversa de uma sessao. Requer autenticacao."
)
def clear_chat_session(
    request: ClearSessionRequest,
    user: User = Depends(get_authenticated_user)
) -> ClearSessionResponse:
    """Limpa o historico de uma sessao especifica. Requer autenticacao."""
    success = clear_session(request.session_id)

    if success:
        return ClearSessionResponse(
            success=True,
            message=f"Sessao {request.session_id} limpa com sucesso."
        )
    else:
        return ClearSessionResponse(
            success=False,
            message=f"Sessao {request.session_id} nao encontrada."
        )
