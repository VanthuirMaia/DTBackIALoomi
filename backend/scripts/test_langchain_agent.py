"""
Script para testar o agente LangChain com múltiplas ferramentas.

Uso: python scripts/test_langchain_agent.py
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


def test_langchain_agent():
    print("=" * 70)
    print("TESTE DO AGENTE LANGCHAIN COM FERRAMENTAS")
    print("=" * 70)

    agent = get_agent_service(session_id="test-langchain")

    # Queries que testam diferentes ferramentas
    queries = [
        # Busca semântica
        "Quero pintar meu quarto, algo fácil de limpar e sem cheiro forte.",

        # Filtro específico
        "Quais tintas na cor branca vocês têm?",

        # Cálculo de quantidade
        "Preciso pintar uma parede de 20 metros quadrados. Quantas latas vou precisar?",

        # Listagem de cores
        "Quais cores de tinta vocês têm disponíveis?",

        # Informação sobre linhas
        "Qual a diferença entre as linhas Premium e Econômica?",

        # Busca complexa (ambiente externo)
        "Preciso de uma tinta para a fachada da minha casa que seja resistente ao sol.",
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n{'='*70}")
        print(f"[PERGUNTA {i}]")
        print(f"Usuário: {query}")
        print("-" * 70)

        result = agent.process_query(query)

        print(f"\n📝 RESPOSTA DO AGENTE:")
        print(result['response'])

    print(f"\n{'='*70}")
    print("TESTE CONCLUÍDO!")
    print(f"{'='*70}")


if __name__ == "__main__":
    test_langchain_agent()
