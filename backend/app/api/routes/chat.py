"""
Endpoints do chatbot de recomendação de tintas.
"""

import uuid
from fastapi import APIRouter, HTTPException

from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ClearSessionRequest,
    ClearSessionResponse,
)
from app.services.agent_service import get_agent_service, clear_session

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post(
    "",
    response_model=ChatResponse,
    summary="Enviar mensagem para o assistente",
    description="Envia uma pergunta sobre tintas e recebe uma recomendação personalizada."
)
def chat(request: ChatRequest) -> ChatResponse:
    """
    Processa uma mensagem do usuário e retorna recomendação.

    - Busca produtos relevantes via RAG
    - Gera resposta contextualizada via LLM
    - Mantém histórico se session_id fornecido
    """
    try:
        session_id = request.session_id or str(uuid.uuid4())
        agent = get_agent_service(session_id)

        result = agent.process_query(request.message)

        return ChatResponse(
            response=result["response"],
            products=result["products"],
            query=result["query"],
            session_id=session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar mensagem: {str(e)}")


@router.post(
    "/clear",
    response_model=ClearSessionResponse,
    summary="Limpar histórico da sessão",
    description="Remove o histórico de conversa de uma sessão."
)
def clear_chat_session(request: ClearSessionRequest) -> ClearSessionResponse:
    """Limpa o histórico de uma sessão específica."""
    success = clear_session(request.session_id)

    if success:
        return ClearSessionResponse(
            success=True,
            message=f"Sessão {request.session_id} limpa com sucesso."
        )
    else:
        return ClearSessionResponse(
            success=False,
            message=f"Sessão {request.session_id} não encontrada."
        )
