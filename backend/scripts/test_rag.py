"""
Script para testar o serviço RAG.

Uso: python scripts/test_rag.py
"""

import sys
from pathlib import Path

# Bootstrap
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

# Carrega .env explicitamente
from dotenv import load_dotenv
env_path = backend_dir / ".env"
load_dotenv(dotenv_path=env_path, override=True)

from app.services.rag_service import get_rag_service


def test_rag():
    print("=" * 60)
    print("TESTE DO SERVIÇO RAG")
    print("=" * 60)

    rag = get_rag_service()

    print("\n[1] Carregando produtos e gerando embeddings...")
    count = rag.load_paints()
    print(f"    {count} produtos carregados com sucesso!")

    # Queries de teste (baseadas nos exemplos do desafio)
    queries = [
        "Quero pintar meu quarto, algo fácil de limpar e sem cheiro forte",
        "Preciso pintar a fachada, bate muito sol e chove bastante",
        "Tinta para madeira resistente ao calor",
        "Quero um tom de cinza moderno para escritório",
        "Tinta para banheiro que não crie mofo",
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n[{i+1}] Query: \"{query}\"")
        print("-" * 60)

        results = rag.search(query, top_k=3)

        for j, r in enumerate(results, 1):
            print(f"    {j}. {r['nome']}")
            print(f"       Cor: {r['cor']} | Acabamento: {r['acabamento']}")
            print(f"       Features: {r['features']}")
            print(f"       Relevância: {r['relevancia']}")
            print()

    print("=" * 60)
    print("TESTE CONCLUÍDO COM SUCESSO!")
    print("=" * 60)


if __name__ == "__main__":
    test_rag()
