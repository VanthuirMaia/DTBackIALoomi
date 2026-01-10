"""
Serviço de integração com LLM (OpenAI GPT).

Responsável por gerar respostas em linguagem natural usando o contexto do RAG.
"""

import os
from typing import Optional

from openai import OpenAI


class LLMService:
    """Serviço de geração de respostas com GPT."""

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"

    def generate_response(
        self,
        user_query: str,
        context: list[dict],
        conversation_history: Optional[list[dict]] = None
    ) -> str:
        """
        Gera resposta baseada na query do usuário e contexto do RAG.

        Args:
            user_query: Pergunta do usuário
            context: Lista de produtos relevantes do RAG
            conversation_history: Histórico da conversa (opcional)

        Returns:
            Resposta gerada pelo LLM
        """
        system_prompt = self._build_system_prompt()
        context_text = self._format_context(context)

        messages = [{"role": "system", "content": system_prompt}]

        if conversation_history:
            messages.extend(conversation_history)

        user_message = f"""Contexto (produtos relevantes da base de dados):
{context_text}

Pergunta do cliente: {user_query}"""

        messages.append({"role": "user", "content": user_message})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )

        return response.choices[0].message.content

    def _build_system_prompt(self) -> str:
        """Constrói o prompt de sistema para o assistente."""
        return """Você é um assistente especialista em tintas Suvinil. Seu papel é ajudar clientes a escolherem a tinta ideal para suas necessidades.

Diretrizes:
1. Seja cordial e profissional
2. Baseie suas recomendações APENAS nos produtos fornecidos no contexto
3. Explique por que cada produto é adequado para a necessidade do cliente
4. Mencione características relevantes como acabamento, ambiente e features
5. Se não houver produto adequado no contexto, seja honesto e sugira o mais próximo
6. Respostas devem ser concisas mas informativas (2-4 frases)
7. Use linguagem natural e acessível

Formato de resposta:
- Comece com uma recomendação direta
- Explique brevemente o motivo
- Mencione características relevantes do produto"""

    def _format_context(self, context: list[dict]) -> str:
        """Formata os produtos do contexto para o prompt."""
        if not context:
            return "Nenhum produto encontrado na base de dados."

        lines = []
        for i, product in enumerate(context, 1):
            lines.append(
                f"{i}. {product['nome']}\n"
                f"   Cor: {product['cor']} | Acabamento: {product['acabamento']}\n"
                f"   Superfície: {product['tipo_superficie']} | Ambiente: {product['ambiente']}\n"
                f"   Características: {product['features']}\n"
                f"   Linha: {product['linha']}"
            )
        return "\n".join(lines)


# Instância singleton
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Retorna instância singleton do LLMService."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
