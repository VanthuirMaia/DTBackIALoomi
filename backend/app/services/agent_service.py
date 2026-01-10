"""
Serviço de orquestração do Agente de IA.

Coordena o fluxo entre RAG (busca semântica) e LLM (geração de resposta).
"""

from typing import Optional

from app.services.rag_service import get_rag_service
from app.services.llm_service import get_llm_service


class AgentService:
    """Orquestrador do agente de recomendação de tintas."""

    def __init__(self):
        self.rag = get_rag_service()
        self.llm = get_llm_service()
        self.conversation_history: list[dict] = []

    def process_query(self, user_query: str, top_k: int = 5) -> dict:
        """
        Processa uma pergunta do usuário.

        Fluxo:
        1. Busca produtos relevantes via RAG
        2. Gera resposta contextualizada via LLM
        3. Atualiza histórico da conversa

        Args:
            user_query: Pergunta do usuário
            top_k: Número de produtos a buscar no RAG

        Returns:
            Dict com resposta e produtos relacionados
        """
        # 1. Busca semântica
        relevant_products = self.rag.search(user_query, top_k=top_k)

        # 2. Geração de resposta
        response = self.llm.generate_response(
            user_query=user_query,
            context=relevant_products,
            conversation_history=self.conversation_history
        )

        # 3. Atualiza histórico
        self.conversation_history.append({"role": "user", "content": user_query})
        self.conversation_history.append({"role": "assistant", "content": response})

        # Limita histórico para evitar contexto muito grande
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]

        return {
            "response": response,
            "products": relevant_products,
            "query": user_query
        }

    def clear_history(self) -> None:
        """Limpa o histórico da conversa."""
        self.conversation_history = []

    def get_history(self) -> list[dict]:
        """Retorna o histórico da conversa."""
        return self.conversation_history.copy()


# Armazena sessões de agentes por session_id
_agent_sessions: dict[str, AgentService] = {}


def get_agent_service(session_id: Optional[str] = None) -> AgentService:
    """
    Retorna instância do AgentService.

    Args:
        session_id: ID da sessão (opcional). Se fornecido, mantém histórico.

    Returns:
        Instância do AgentService
    """
    if session_id is None:
        return AgentService()

    if session_id not in _agent_sessions:
        _agent_sessions[session_id] = AgentService()

    return _agent_sessions[session_id]


def clear_session(session_id: str) -> bool:
    """Remove uma sessão do cache."""
    if session_id in _agent_sessions:
        del _agent_sessions[session_id]
        return True
    return False
