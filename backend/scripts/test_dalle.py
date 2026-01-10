"""
Script de teste para a integração com DALL-E.

Testa a geração de imagens de visualização de ambientes.
"""

import sys
import os

# Adiciona o diretório pai ao path para importar os módulos da aplicação
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

from app.services.dalle_service import get_dalle_service


def test_dalle_service():
    """Testa a geração de imagem com DALL-E."""
    print("=" * 60)
    print("TESTE: Integração DALL-E")
    print("=" * 60)

    dalle = get_dalle_service()

    # Teste 1: Sala com azul claro
    print("\n1. Gerando visualização: Sala com azul claro...")
    result = dalle.generate_room_visualization(
        ambiente="sala",
        cor="azul claro",
        estilo="moderno"
    )

    if result["success"]:
        print(f"   [OK] Imagem gerada com sucesso!")
        print(f"   URL: {result['image_url'][:80]}...")
        print(f"   Prompt usado: {result['prompt_used'][:60]}...")
    else:
        print(f"   [ERRO] {result['error']}")

    return result["success"]


def test_agent_with_dalle():
    """Testa o agente usando a ferramenta de visualização."""
    print("\n" + "=" * 60)
    print("TESTE: Agente com ferramenta visualizar_ambiente")
    print("=" * 60)

    from app.services.agent_service import AgentService

    agent = AgentService()

    # Query que deve acionar a ferramenta visualizar_ambiente
    query = "Quero pintar minha sala de azul claro, como ficaria?"

    print(f"\nQuery: {query}")
    print("Processando...\n")

    result = agent.process_query(query)

    print(f"Resposta do agente:")
    print("-" * 40)
    print(result["response"])
    print("-" * 40)

    # Verifica se a URL da imagem está na resposta
    has_image = "http" in result["response"] and "oaidalleapiprodscus" in result["response"]

    if has_image:
        print("\n[OK] Agente gerou visualização com sucesso!")
    else:
        print("\n[INFO] Resposta não contém URL de imagem (pode ser configuração ou erro)")

    return True


def main():
    """Executa todos os testes."""
    print("\n" + "=" * 60)
    print("  TESTES DE INTEGRAÇÃO DALL-E")
    print("=" * 60)

    # Verifica se a API key está configurada
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n[ERRO] OPENAI_API_KEY não configurada!")
        print("Configure a variável de ambiente OPENAI_API_KEY no arquivo .env")
        return

    print(f"\n[OK] OPENAI_API_KEY configurada: {api_key[:8]}...")

    # Teste do serviço DALL-E direto
    dalle_ok = test_dalle_service()

    # Teste do agente com DALL-E
    if dalle_ok:
        test_agent_with_dalle()
    else:
        print("\n[SKIP] Pulando teste do agente devido a erro no DALL-E")

    print("\n" + "=" * 60)
    print("  TESTES FINALIZADOS")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
