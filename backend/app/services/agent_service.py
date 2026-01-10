"""
Serviço de orquestração do Agente de IA usando LangChain/LangGraph.

O agente decide autonomamente qual ferramenta usar baseado na pergunta do usuário.
Inclui sistema de guardrails para segurança e controle de comportamento.
"""

import os
from typing import Optional

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from app.services.tools import get_tools
from app.services.guardrails_service import (
    get_guardrails_service,
    GuardrailViolation,
    GuardrailViolationType
)


SYSTEM_PROMPT = """Você é um assistente especialista em tintas Suvinil.
Seu papel é ajudar clientes a escolherem a tinta ideal para suas necessidades.

Você tem acesso às seguintes ferramentas:
- buscar_tinta_semantica: Para buscar tintas baseado em descrições em linguagem natural
- buscar_por_filtros: Para buscar tintas por características específicas (cor, ambiente, acabamento)
- calcular_quantidade_tinta: Para calcular quantos litros/latas o cliente precisa
- listar_cores_disponiveis: Para mostrar todas as cores disponíveis
- listar_linhas_produtos: Para explicar as diferenças entre linhas Premium, Standard e Econômica

Diretrizes:
1. Seja cordial e profissional
2. Use as ferramentas apropriadas para cada tipo de pergunta
3. Explique suas recomendações de forma clara
4. Se o usuário perguntar sobre quantidade, use a ferramenta de cálculo
5. Se o usuário quiser filtrar por características específicas, use buscar_por_filtros
6. Para perguntas gerais sobre recomendações, use buscar_tinta_semantica
7. Sempre forneça respostas úteis e contextualizadas"""


class AgentService:
    """Agente LangGraph para recomendação de tintas."""

    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.tools = get_tools()
        self.conversation_history: list = [SystemMessage(content=SYSTEM_PROMPT)]
        self.agent = create_react_agent(
            self.llm,
            self.tools
        )
        self.guardrails = get_guardrails_service()

    def process_query(self, user_query: str, top_k: int = 5) -> dict:
        """
        Processa uma pergunta do usuário usando o agente LangGraph.

        O agente decide autonomamente qual ferramenta usar.
        Inclui validação de guardrails para segurança.

        Args:
            user_query: Pergunta do usuário
            top_k: Não usado nesta versão (mantido para compatibilidade)

        Returns:
            Dict com resposta e metadados
        """
        try:
            # 1. Validação de input via guardrails
            try:
                is_valid, validation_msg = self.guardrails.validate_input(user_query)

                if not is_valid:
                    if validation_msg == "off_topic":
                        return {
                            "response": self.guardrails.get_off_topic_response(),
                            "products": [],
                            "query": user_query,
                            "agent_type": "langgraph",
                            "guardrail_triggered": "off_topic"
                        }
                    return {
                        "response": validation_msg,
                        "products": [],
                        "query": user_query,
                        "agent_type": "langgraph",
                        "guardrail_triggered": "invalid_input"
                    }

            except GuardrailViolation as gv:
                return {
                    "response": gv.message,
                    "products": [],
                    "query": user_query,
                    "agent_type": "langgraph",
                    "guardrail_triggered": gv.violation_type.value
                }

            # 2. Prepara mensagens com histórico
            messages = self.conversation_history + [HumanMessage(content=user_query)]

            # 3. Invoca o agente
            result = self.agent.invoke({"messages": messages})

            # 4. Extrai a última resposta do agente
            response = result["messages"][-1].content

            # 5. Validação de output via guardrails
            is_output_valid, validated_output = self.guardrails.validate_output(response)
            if not is_output_valid:
                response = validated_output  # Usa mensagem de erro sanitizada

            # 6. Atualiza histórico
            self.conversation_history.append(HumanMessage(content=user_query))
            self.conversation_history.append(AIMessage(content=response))

            # 7. Limita histórico
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]

            return {
                "response": response,
                "products": [],
                "query": user_query,
                "agent_type": "langgraph"
            }

        except Exception as e:
            return {
                "response": f"Desculpe, ocorreu um erro ao processar sua pergunta: {str(e)}",
                "products": [],
                "query": user_query,
                "agent_type": "langgraph",
                "error": str(e)
            }

    def clear_history(self) -> None:
        """Limpa o histórico da conversa."""
        self.conversation_history = [SystemMessage(content=SYSTEM_PROMPT)]

    def get_history(self) -> list:
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
