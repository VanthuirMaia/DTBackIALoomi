"""
Serviço de RAG (Retrieval-Augmented Generation) para busca semântica de tintas.

Utiliza OpenAI Embeddings para gerar vetores e busca por similaridade de cosseno.
"""

import os
from typing import Optional

import numpy as np
from openai import OpenAI

from app.db.session import SessionLocal
from app.models.paint import Paint


class RAGService:
    """Serviço de busca semântica usando embeddings."""

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "text-embedding-3-small"
        self.embeddings_cache: dict[int, np.ndarray] = {}
        self.paints_cache: dict[int, Paint] = {}

    def _paint_to_text(self, paint: Paint) -> str:
        """Converte um produto Paint em texto para embedding."""
        return (
            f"{paint.nome}. "
            f"Cor: {paint.cor}. "
            f"Superfície: {paint.tipo_superficie}. "
            f"Ambiente: {paint.ambiente}. "
            f"Acabamento: {paint.acabamento}. "
            f"Características: {paint.features}. "
            f"Linha: {paint.linha}."
        )

    def _get_embedding(self, text: str) -> np.ndarray:
        """Gera embedding para um texto usando OpenAI."""
        response = self.client.embeddings.create(
            input=text,
            model=self.model
        )
        return np.array(response.data[0].embedding)

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calcula similaridade de cosseno entre dois vetores."""
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    def load_paints(self) -> int:
        """Carrega produtos do banco e gera embeddings."""
        session = SessionLocal()
        try:
            paints = session.query(Paint).all()

            for paint in paints:
                text = self._paint_to_text(paint)
                embedding = self._get_embedding(text)
                self.embeddings_cache[paint.id] = embedding
                self.paints_cache[paint.id] = paint

            return len(paints)
        finally:
            session.close()

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """
        Busca produtos mais relevantes para a query.

        Args:
            query: Pergunta ou descrição do usuário
            top_k: Número de resultados a retornar

        Returns:
            Lista de produtos ordenados por relevância
        """
        if not self.embeddings_cache:
            self.load_paints()

        query_embedding = self._get_embedding(query)

        similarities = []
        for paint_id, paint_embedding in self.embeddings_cache.items():
            score = self._cosine_similarity(query_embedding, paint_embedding)
            similarities.append((paint_id, score))

        similarities.sort(key=lambda x: x[1], reverse=True)
        top_results = similarities[:top_k]

        results = []
        for paint_id, score in top_results:
            paint = self.paints_cache[paint_id]
            results.append({
                "id": paint.id,
                "nome": paint.nome,
                "cor": paint.cor,
                "tipo_superficie": paint.tipo_superficie,
                "ambiente": paint.ambiente,
                "acabamento": paint.acabamento,
                "features": paint.features,
                "linha": paint.linha,
                "relevancia": round(score, 4)
            })

        return results


# Instância singleton do serviço
_rag_service: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    """Retorna instância singleton do RAGService."""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
