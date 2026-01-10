"""
Script para testar o sistema de autenticacao JWT com RBAC.

Uso: python scripts/test_auth.py

Requer a API rodando em http://localhost:8000
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"


def print_separator(title: str):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def print_response(response, show_body=True):
    print(f"Status: {response.status_code}")
    if show_body:
        try:
            print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        except:
            print(f"Response: {response.text[:200]}")


def test_register_user():
    """Testa registro de usuario comum."""
    print_separator("1. REGISTRO DE USUARIO")

    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": "usuario@teste.com",
            "password": "senha123",
            "name": "Usuario Teste"
        }
    )
    print_response(response)

    if response.status_code == 201:
        return response.json()["access_token"]
    return None


def test_register_admin():
    """Testa registro de admin."""
    print_separator("2. REGISTRO DE ADMIN")

    response = requests.post(
        f"{BASE_URL}/auth/register-admin",
        json={
            "email": "admin@teste.com",
            "password": "admin123",
            "name": "Admin Teste"
        }
    )
    print_response(response)

    if response.status_code == 201:
        return response.json()["access_token"]
    return None


def test_login():
    """Testa login."""
    print_separator("3. LOGIN")

    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": "usuario@teste.com",
            "password": "senha123"
        }
    )
    print_response(response)

    if response.status_code == 200:
        return response.json()["access_token"]
    return None


def test_login_wrong_password():
    """Testa login com senha errada."""
    print_separator("4. LOGIN COM SENHA ERRADA")

    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": "usuario@teste.com",
            "password": "senhaerrada"
        }
    )
    print_response(response)


def test_public_routes():
    """Testa rotas publicas (sem autenticacao)."""
    print_separator("5. ROTAS PUBLICAS (SEM AUTH)")

    # GET /paints - publico
    print("\n[GET /paints] - Deve funcionar:")
    response = requests.get(f"{BASE_URL}/paints")
    print(f"Status: {response.status_code} (esperado: 200)")

    # GET /health - publico
    print("\n[GET /health] - Deve funcionar:")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code} (esperado: 200)")


def test_protected_routes_no_auth():
    """Testa rotas protegidas sem autenticacao."""
    print_separator("6. ROTAS PROTEGIDAS SEM AUTH (DEVEM FALHAR)")

    # POST /chat - protegido
    print("\n[POST /chat] - Deve falhar (401):")
    response = requests.post(
        f"{BASE_URL}/chat",
        json={"message": "Qual tinta usar?"}
    )
    print(f"Status: {response.status_code} (esperado: 401/403)")

    # POST /paints - admin only
    print("\n[POST /paints] - Deve falhar (401):")
    response = requests.post(
        f"{BASE_URL}/paints",
        json={"nome": "Tinta Teste"}
    )
    print(f"Status: {response.status_code} (esperado: 401/403)")


def test_chat_with_user_token(token: str):
    """Testa chat com token de usuario."""
    print_separator("7. CHAT COM TOKEN DE USUARIO")

    headers = {"Authorization": f"Bearer {token}"}

    response = requests.post(
        f"{BASE_URL}/chat",
        json={"message": "Qual tinta usar para quarto?"},
        headers=headers
    )
    print_response(response)


def test_admin_routes_with_user_token(token: str):
    """Testa rotas admin com token de usuario comum."""
    print_separator("8. ROTAS ADMIN COM TOKEN DE USUARIO (DEVE FALHAR)")

    headers = {"Authorization": f"Bearer {token}"}

    # POST /paints - admin only
    print("\n[POST /paints] - Deve falhar (403 Forbidden):")
    response = requests.post(
        f"{BASE_URL}/paints",
        json={
            "nome": "Tinta Teste",
            "cor": "Azul",
            "tipo_superficie": "Parede",
            "ambiente": "Interno",
            "acabamento": "Fosco",
            "linha": "Standard",
            "features": "Teste"
        },
        headers=headers
    )
    print(f"Status: {response.status_code} (esperado: 403)")
    print_response(response, show_body=True)


def test_admin_routes_with_admin_token(token: str):
    """Testa rotas admin com token de admin."""
    print_separator("9. ROTAS ADMIN COM TOKEN DE ADMIN")

    headers = {"Authorization": f"Bearer {token}"}

    # POST /paints - admin only
    print("\n[POST /paints] - Deve funcionar:")
    response = requests.post(
        f"{BASE_URL}/paints",
        json={
            "nome": "Tinta Teste Auth",
            "cor": "Verde",
            "tipo_superficie": "Parede",
            "ambiente": "Interno",
            "acabamento": "Acetinado",
            "linha": "Premium",
            "features": "Criada via teste de auth"
        },
        headers=headers
    )
    print(f"Status: {response.status_code} (esperado: 201)")

    if response.status_code == 201:
        paint_id = response.json().get("id")
        print(f"Tinta criada com ID: {paint_id}")

        # DELETE /paints/{id} - admin only
        print(f"\n[DELETE /paints/{paint_id}] - Deve funcionar:")
        response = requests.delete(
            f"{BASE_URL}/paints/{paint_id}",
            headers=headers
        )
        print(f"Status: {response.status_code} (esperado: 204)")


def main():
    print("\n")
    print("*" * 60)
    print("*  TESTE DE AUTENTICACAO JWT COM RBAC  *")
    print("*" * 60)
    print(f"\nBase URL: {BASE_URL}")
    print("Certifique-se que a API esta rodando!\n")

    # 1. Registro de usuario
    user_token = test_register_user()

    # 2. Registro de admin
    admin_token = test_register_admin()

    # 3. Login
    test_login()

    # 4. Login com senha errada
    test_login_wrong_password()

    # 5. Rotas publicas
    test_public_routes()

    # 6. Rotas protegidas sem auth
    test_protected_routes_no_auth()

    # 7. Chat com usuario
    if user_token:
        test_chat_with_user_token(user_token)

    # 8. Admin routes com user token
    if user_token:
        test_admin_routes_with_user_token(user_token)

    # 9. Admin routes com admin token
    if admin_token:
        test_admin_routes_with_admin_token(admin_token)

    print_separator("TESTES CONCLUIDOS")
    print("\nResumo esperado:")
    print("- Registro/Login: 200/201")
    print("- Rotas publicas: 200")
    print("- Rotas protegidas sem auth: 401/403")
    print("- Chat com user token: 200")
    print("- Admin routes com user token: 403")
    print("- Admin routes com admin token: 201/204")


if __name__ == "__main__":
    main()
