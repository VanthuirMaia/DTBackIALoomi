"""
Script para testar o serviço de chat completo (RAG + LLM).

Uso: python scripts/test_chat.py
"""

import sys
from pathlib import Path

# Bootstrap
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

# Carrega .env
from dotenv import load_dotenv
env_path = backend_dir / ".env"
load_dotenv(dotenv_path=env_path, override=True)

from app.services.agent_service import get_agent_service


def test_chat():
    print("=" * 70)
    print("TESTE DO ASSISTENTE DE TINTAS (RAG + LLM)")
    print("=" * 70)

    agent = get_agent_service(session_id="test-session")

    # Queries baseadas nos exemplos do desafio
    queries = [
        "Quero pintar meu quarto, mas prefiro algo que seja fácil de limpar e sem cheiro forte.",
        "Preciso pintar a fachada da minha casa. Bate muito sol e chove bastante por aqui.",
        "Você tem alguma tinta para madeira que seja resistente ao calor?",
        "Quero pintar meu escritório com um tom de cinza moderno.",
        "Preciso de uma tinta anti-mofo para o banheiro.",
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n{'='*70}")
        print(f"[PERGUNTA {i}]")
        print(f"Usuário: {query}")
        print("-" * 70)

        result = agent.process_query(query)

        print(f"\nAssistente: {result['response']}")
        print(f"\n[Produtos encontrados: {len(result['products'])}]")
        for j, p in enumerate(result['products'][:3], 1):
            print(f"  {j}. {p['nome']} (relevância: {p['relevancia']})")

    print(f"\n{'='*70}")
    print("TESTE CONCLUÍDO COM SUCESSO!")
    print(f"{'='*70}")


if __name__ == "__main__":
    test_chat()
