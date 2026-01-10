"""
Debug da API Key - verifica se está sendo lida corretamente.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

print("=" * 60)
print("DEBUG API KEY")
print("=" * 60)

if not api_key:
    print("[ERRO] API key não encontrada no .env")
else:
    print(f"Comprimento: {len(api_key)} caracteres")
    print(f"Início: {api_key[:20]}...")
    print(f"Final: ...{api_key[-10:]}")
    print(f"Tem espaços no início/fim: {api_key != api_key.strip()}")
    print(f"Tem quebra de linha: {chr(10) in api_key or chr(13) in api_key}")

print("\n" + "=" * 60)
print("TESTE DIRETO COM OPENAI")
print("=" * 60)

from openai import OpenAI

try:
    client = OpenAI(api_key=api_key.strip() if api_key else None)

    # Teste simples com chat (mais barato)
    print("\n1. Testando GPT (chat)...")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Diga apenas: OK"}],
        max_tokens=5
    )
    print(f"   [OK] GPT funcionando: {response.choices[0].message.content}")

    # Teste com DALL-E
    print("\n2. Testando DALL-E 2...")
    response = client.images.generate(
        model="dall-e-2",
        prompt="A simple blue square",
        size="256x256",
        n=1,
    )
    print(f"   [OK] DALL-E funcionando!")
    print(f"   URL: {response.data[0].url[:60]}...")

except Exception as e:
    print(f"   [ERRO] {e}")
