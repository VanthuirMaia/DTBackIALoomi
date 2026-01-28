# DOCUMENTO TÉCNICO - ASSISTENTE DE TINTAS SUVINIL
## Análise Profunda de Implementação e Arquitetura

---

# 1. ARQUITETURA DE SOFTWARE

## 1.1 Padrao Arquitetural: Layered Architecture (Arquitetura em Camadas)

```
┌─────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ routes/     │  │ routes/     │  │ routes/     │              │
│  │ auth.py     │  │ paints.py   │  │ chat.py     │              │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘              │
└─────────┼────────────────┼────────────────┼─────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        BUSINESS LAYER                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ auth_       │  │ agent_      │  │ guardrails_ │              │
│  │ service.py  │  │ service.py  │  │ service.py  │              │
│  └─────────────┘  └──────┬──────┘  └─────────────┘              │
│                          │                                       │
│         ┌────────────────┼────────────────┐                     │
│         ▼                ▼                ▼                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ rag_        │  │ llm_        │  │ dalle_      │              │
│  │ service.py  │  │ service.py  │  │ service.py  │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│                                                                  │
│  ┌──────────────────────────────────────────────┐               │
│  │              tools.py (6 ferramentas)         │               │
│  └──────────────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────────┘
          │                │
          ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA ACCESS LAYER                           │
│  ┌──────────────────────┐  ┌──────────────────────┐             │
│  │ paint_repository.py  │  │ session.py           │             │
│  └──────────────────────┘  └──────────────────────┘             │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATABASE LAYER                              │
│  ┌──────────────────────┐  ┌──────────────────────┐             │
│  │ models/paint.py      │  │ models/user.py       │             │
│  └──────────────────────┘  └──────────────────────┘             │
│                                                                  │
│                    PostgreSQL 15                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 1.2 Justificativa da Arquitetura

**Por que Layered Architecture?**
- **Separacao de responsabilidades**: Cada camada tem funcao especifica
- **Testabilidade**: Camadas podem ser testadas isoladamente
- **Manutencao**: Mudancas em uma camada nao afetam outras
- **Escalabilidade**: Facil adicionar novos endpoints ou servicos

**Trade-offs:**
- (+) Codigo organizado e previsivel
- (+) Facil onboarding de novos devs
- (-) Pode ter overhead para projetos muito pequenos
- (-) Requer disciplina para manter separacao

---

# 2. STACK TECNICA - ANALISE DETALHADA

## 2.1 requirements.txt - Cada Dependencia Explicada

```python
# FRAMEWORK WEB
fastapi==0.115.6      # Framework async moderno, tipagem nativa, OpenAPI automatico
uvicorn==0.34.0       # ASGI server, implementa o loop de eventos async

# BANCO DE DADOS
sqlalchemy==2.0.36    # ORM com suporte a async, tipagem melhorada na v2
psycopg2-binary==2.9.10  # Driver PostgreSQL compilado (sem precisar de libs C)

# CONFIGURACAO
python-dotenv==1.0.1  # Carrega .env para os.environ

# INTELIGENCIA ARTIFICIAL
openai==1.59.5        # SDK oficial OpenAI (GPT, Embeddings, DALL-E)
numpy==2.2.1          # Operacoes vetoriais para similaridade de cosseno
langchain==0.3.14     # Framework para LLM apps (chains, tools)
langchain-openai==0.3.0  # Integracao LangChain + OpenAI
langgraph==0.2.62     # Orquestracao de agentes baseada em grafos

# AUTENTICACAO
python-jose[cryptography]==3.3.0  # JWT encode/decode com suporte a crypto
passlib==1.7.4        # Wrapper para hashing de senhas
bcrypt==4.0.1         # Algoritmo de hash (versao fixada por compatibilidade)

# VALIDACAO
email-validator==2.1.0  # Validacao de EmailStr do Pydantic
```

## 2.2 Por Que Cada Tecnologia Foi Escolhida

### FastAPI vs Flask vs Django

| Criterio | FastAPI | Flask | Django |
|----------|---------|-------|--------|
| Performance | Alta (async nativo) | Media | Media |
| Tipagem | Nativa (Pydantic) | Manual | Parcial |
| Docs automatica | Sim (Swagger) | Nao | Nao |
| Curva aprendizado | Media | Baixa | Alta |
| Boilerplate | Baixo | Baixo | Alto |

**Decisao**: FastAPI pela combinacao de performance + tipagem + docs automatica.

### SQLAlchemy 2.x vs 1.x

```python
# SQLAlchemy 1.x - sintaxe antiga
session.query(User).filter(User.id == 1).first()

# SQLAlchemy 2.x - sintaxe nova (usada no projeto)
session.query(User).filter(User.id == 1).first()  # Compativel
# OU
session.execute(select(User).where(User.id == 1)).scalar_one_or_none()  # Novo
```

**Decisao**: 2.x para compatibilidade futura, melhor tipagem, suporte async.

### LangGraph vs LangChain Agents

```python
# LangChain tradicional - agente implicito
agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION)

# LangGraph - agente explicito (usado no projeto)
agent = create_react_agent(llm, tools)
result = agent.invoke({"messages": messages})
```

**Decisao**: LangGraph por ser o padrao atual recomendado, melhor controle de fluxo.

---

# 3. MODELOS DE DADOS (ORM)

## 3.1 Model Paint - Analise Linha a Linha

```python
# backend/app/models/paint.py

from sqlalchemy import Column, Integer, String, Text
from app.db.base import Base

class Paint(Base):
    __tablename__ = "paints"  # Nome da tabela no PostgreSQL

    # Primary Key com index para buscas rapidas O(log n)
    id = Column(Integer, primary_key=True, index=True)

    # String com limite - evita dados muito grandes
    nome = Column(String(255), nullable=False)  # NOT NULL constraint
    cor = Column(String(100), nullable=False)

    # Campos opcionais (nullable=True e o default)
    tipo_superficie = Column(String(100))  # Parede, Madeira, Metal, etc
    ambiente = Column(String(100))          # Interno, Externo
    acabamento = Column(String(100))        # Fosco, Acetinado, Brilhante

    # Text para strings longas sem limite definido
    features = Column(Text)  # Caracteristicas em texto livre

    linha = Column(String(100))  # Premium, Standard, Economica

    # Representacao para debug
    def __repr__(self):
        return f"<Paint(id={self.id}, nome='{self.nome}', cor='{self.cor}')>"
```

**Decisoes de Design:**
- `String(255)` vs `Text`: String tem limite, melhor para campos estruturados
- `nullable=False`: Garante integridade de dados obrigatorios
- `index=True` no id: Acelera lookups por primary key
- Sem `unique` em nome: Permite produtos com nomes similares

## 3.2 Model User - Analise Linha a Linha

```python
# backend/app/models/user.py

from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
from app.db.base import Base

# Enum Python para type safety
class UserRole(str, PyEnum):
    """Herda de str para serializacao JSON automatica"""
    ADMIN = "admin"
    USER = "user"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # Email unico com index para login rapido
    email = Column(String(255), unique=True, index=True, nullable=False)

    # Hash bcrypt tem ~60 caracteres, 255 e seguro
    password_hash = Column(String(255), nullable=False)

    name = Column(String(255), nullable=False)

    # Enum SQLAlchemy mapeia para tipo nativo do banco
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)

    # Timestamps automaticos via func.now() do PostgreSQL
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

**Decisoes de Design:**
- `UserRole(str, PyEnum)`: Herda de str para JSON serialization automatica
- `unique=True` em email: Constraint de unicidade no banco
- `server_default=func.now()`: Executa no PostgreSQL, nao no Python
- `onupdate=func.now()`: Atualiza automaticamente em cada UPDATE

**SQL Gerado:**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(5) DEFAULT 'user' NOT NULL,  -- ENUM como VARCHAR
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
CREATE INDEX ix_users_email ON users(email);
CREATE INDEX ix_users_id ON users(id);
```

---

# 4. CAMADA DE DADOS (DATA ACCESS LAYER)

## 4.1 Session Management - Padrao Unit of Work

```python
# backend/app/db/session.py

import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Carrega .env do diretorio pai (backend/)
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Engine: pool de conexoes com o banco
# echo=False: nao loga queries SQL (True para debug)
engine = create_engine(DATABASE_URL, echo=False)

# SessionLocal: factory de sessoes
# autocommit=False: transacoes explicitas (padrao seguro)
# autoflush=False: flush manual para controle fino
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Dependency Injection pattern para FastAPI.

    Uso:
        @router.get("/")
        def endpoint(db: Session = Depends(get_db)):
            ...

    O 'yield' garante que a sessao seja fechada apos a request,
    mesmo em caso de excecao (try/finally implicito).
    """
    db = SessionLocal()
    try:
        yield db  # Retorna sessao para o endpoint
    finally:
        db.close()  # Sempre fecha, evita connection leak
```

**Padroes Aplicados:**
- **Factory Pattern**: `SessionLocal` e uma factory de sessoes
- **Dependency Injection**: `get_db()` injeta sessao via FastAPI `Depends()`
- **Context Manager**: `yield` simula `with` statement

## 4.2 Repository Pattern - paint_repository.py

```python
# backend/app/repositories/paint_repository.py

from sqlalchemy.orm import Session
from app.models.paint import Paint


def create_paint(db: Session, paint_data: dict) -> Paint:
    """
    Cria nova tinta no banco.

    Fluxo:
    1. Unpacking do dict para kwargs do construtor
    2. add() marca para INSERT (ainda nao executa)
    3. commit() executa INSERT e inicia nova transacao
    4. refresh() recarrega objeto com dados do banco (id gerado)
    """
    paint = Paint(**paint_data)  # Dict unpacking
    db.add(paint)                # Marca para INSERT
    db.commit()                  # Executa INSERT
    db.refresh(paint)            # Recarrega com id gerado
    return paint


def get_paint_by_id(db: Session, paint_id: int) -> Paint | None:
    """
    Busca por PK - O(log n) com index.

    .first() retorna None se nao encontrar (vs .one() que levanta excecao)
    """
    return db.query(Paint).filter(Paint.id == paint_id).first()


def list_paints(db: Session) -> list[Paint]:
    """
    Lista todas as tintas.

    .all() retorna lista vazia se nao houver registros.
    Cuidado: sem paginacao, pode ser lento com muitos registros.
    """
    return db.query(Paint).all()


def update_paint(db: Session, paint_id: int, paint_data: dict) -> Paint | None:
    """
    Atualiza tinta existente.

    Seguranca: allowed_fields previne mass assignment attack.
    Atacante nao pode enviar {"id": 999} ou {"__class__": ...}
    """
    paint = get_paint_by_id(db, paint_id)
    if not paint:
        return None

    # Whitelist de campos permitidos (seguranca)
    allowed_fields = {
        "nome", "cor", "tipo_superficie",
        "ambiente", "acabamento", "features", "linha",
    }

    for key, value in paint_data.items():
        if key in allowed_fields:  # Ignora campos nao permitidos
            setattr(paint, key, value)  # Atribuicao dinamica

    db.commit()   # Executa UPDATE
    db.refresh(paint)  # Recarrega dados atualizados
    return paint


def delete_paint(db: Session, paint_id: int) -> bool:
    """
    Remove tinta (hard delete).

    Retorna bool para indicar sucesso/falha.
    Em producao, considerar soft delete (campo deleted_at).
    """
    paint = get_paint_by_id(db, paint_id)
    if not paint:
        return False
    db.delete(paint)  # Marca para DELETE
    db.commit()       # Executa DELETE
    return True
```

**Padroes Aplicados:**
- **Repository Pattern**: Abstrai acesso a dados
- **Whitelist Validation**: Previne mass assignment
- **Null Object Pattern**: Retorna None em vez de excecao

---

# 5. CAMADA DE SERVICOS (BUSINESS LAYER)

## 5.1 RAG Service - Busca Semantica

```python
# backend/app/services/rag_service.py

import os
from typing import Optional
import numpy as np
from openai import OpenAI
from app.db.session import SessionLocal
from app.models.paint import Paint


class RAGService:
    """
    RAG = Retrieval-Augmented Generation

    Fluxo:
    1. Converte produtos em texto
    2. Gera embeddings (vetores 1536D)
    3. Armazena em cache (memoria)
    4. Na busca: embedding da query -> similaridade -> top-k
    """

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "text-embedding-3-small"  # 1536 dimensoes, $0.02/1M tokens

        # Cache em memoria (dict)
        self.embeddings_cache: dict[int, np.ndarray] = {}  # paint_id -> vetor
        self.paints_cache: dict[int, Paint] = {}           # paint_id -> objeto

    def _paint_to_text(self, paint: Paint) -> str:
        """
        Converte objeto Paint em texto para embedding.

        Formato estruturado ajuda o modelo a entender os atributos.
        """
        return (
            f"{paint.nome}. "
            f"Cor: {paint.cor}. "
            f"Superficie: {paint.tipo_superficie}. "
            f"Ambiente: {paint.ambiente}. "
            f"Acabamento: {paint.acabamento}. "
            f"Caracteristicas: {paint.features}. "
            f"Linha: {paint.linha}."
        )

    def _get_embedding(self, text: str) -> np.ndarray:
        """
        Gera embedding via API OpenAI.

        Retorno: vetor numpy de 1536 dimensoes (floats)
        Custo: ~$0.02 por 1 milhao de tokens
        Latencia: ~100-200ms
        """
        response = self.client.embeddings.create(
            input=text,
            model=self.model
        )
        # response.data[0].embedding e lista de floats
        return np.array(response.data[0].embedding)

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """
        Similaridade de cosseno entre dois vetores.

        Formula: cos(theta) = (A . B) / (||A|| * ||B||)

        Retorno: float entre -1 e 1
        - 1.0 = identicos
        - 0.0 = ortogonais (sem relacao)
        - -1.0 = opostos

        Para embeddings de texto, valores tipicos: 0.7-0.9 para similares
        """
        dot_product = np.dot(a, b)           # Produto escalar
        norm_a = np.linalg.norm(a)           # Magnitude de A
        norm_b = np.linalg.norm(b)           # Magnitude de B
        return float(dot_product / (norm_a * norm_b))

    def load_paints(self) -> int:
        """
        Carrega todos os produtos e gera embeddings.

        Chamado apenas uma vez (lazy loading no primeiro search).
        Para 72 produtos: ~72 chamadas API, ~15 segundos, ~$0.001
        """
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
        Busca semantica por similaridade.

        Complexidade: O(n) onde n = numero de produtos
        Para 72 produtos: < 10ms (apos load inicial)

        Args:
            query: Texto livre do usuario
            top_k: Quantos resultados retornar

        Returns:
            Lista ordenada por relevancia (maior primeiro)
        """
        # Lazy loading - carrega na primeira busca
        if not self.embeddings_cache:
            self.load_paints()

        # Gera embedding da query do usuario
        query_embedding = self._get_embedding(query)

        # Calcula similaridade com TODOS os produtos
        similarities = []
        for paint_id, paint_embedding in self.embeddings_cache.items():
            score = self._cosine_similarity(query_embedding, paint_embedding)
            similarities.append((paint_id, score))

        # Ordena por score decrescente
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Pega top-k
        top_results = similarities[:top_k]

        # Formata resultado
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
                "relevancia": round(score, 4)  # 4 casas decimais
            })

        return results


# Singleton Pattern
_rag_service: Optional[RAGService] = None

def get_rag_service() -> RAGService:
    """
    Retorna instancia unica do RAGService.

    Por que Singleton?
    - Embeddings sao caros para gerar
    - Cache deve persistir entre requests
    - Evita multiplas instancias com caches duplicados
    """
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
```

**Conceitos Importantes:**

1. **Embedding**: Representacao vetorial de texto. Textos similares tem vetores proximos.

2. **Similaridade de Cosseno**: Mede angulo entre vetores, ignorando magnitude.

3. **Lazy Loading**: Carrega embeddings apenas quando necessario.

4. **Singleton**: Uma instancia compartilhada entre todas as requests.

## 5.2 Agent Service - Orquestracao com LangGraph

```python
# backend/app/services/agent_service.py

import os
import re
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


# System Prompt define a "personalidade" e capacidades do agente
SYSTEM_PROMPT = """Voce e um assistente especialista em tintas Suvinil.
Seu papel e ajudar clientes a escolherem a tinta ideal para suas necessidades.

Voce tem acesso as seguintes ferramentas:
- buscar_tinta_semantica: Para buscar tintas baseado em descricoes em linguagem natural
- buscar_por_filtros: Para buscar tintas por caracteristicas especificas (cor, ambiente, acabamento)
- calcular_quantidade_tinta: Para calcular quantos litros/latas o cliente precisa
- listar_cores_disponiveis: Para mostrar todas as cores disponiveis
- listar_linhas_produtos: Para explicar as diferencas entre linhas Premium, Standard e Economica
- visualizar_ambiente: Para gerar uma imagem mostrando como ficaria um ambiente pintado

Diretrizes:
1. Seja cordial e profissional
2. Use as ferramentas apropriadas para cada tipo de pergunta
3. Explique suas recomendacoes de forma clara
4. Se o usuario perguntar sobre quantidade, use a ferramenta de calculo
5. Se o usuario quiser filtrar por caracteristicas especificas, use buscar_por_filtros
6. Para perguntas gerais sobre recomendacoes, use buscar_tinta_semantica
7. Se o usuario quiser visualizar como ficaria um ambiente, use visualizar_ambiente
8. Sempre forneca respostas uteis e contextualizadas"""


def extract_image_urls(text: str) -> list[dict]:
    """
    Extrai URLs de imagens DALL-E da resposta do agente.

    DALL-E retorna URLs no formato:
    https://oaidalleapiprodscus.blob.core.windows.net/...

    Detecta tanto em markdown ![alt](url) quanto texto plano.
    """
    images = []

    # Tenta markdown primeiro: ![texto](url)
    markdown_pattern = r'\!\[.*?\]\((https://oaidalleapiprodscus\.blob\.core\.windows\.net/[^)]+)\)'
    urls = re.findall(markdown_pattern, text)

    # Fallback para URLs soltas
    if not urls:
        plain_pattern = r"https://oaidalleapiprodscus[.]blob[.]core[.]windows[.]net/[^\s<>]+"
        urls = re.findall(plain_pattern, text)

    # Remove duplicatas mantendo ordem
    seen = set()
    for url in urls:
        url = url.rstrip('.,;:!?)')  # Remove pontuacao final
        if url not in seen:
            seen.add(url)
            images.append({
                "url": url,
                "ambiente": "Ambiente",
                "cor": "Cor selecionada"
            })

    return images


class AgentService:
    """
    Orquestrador principal do chatbot.

    Responsabilidades:
    1. Validar input via guardrails
    2. Manter historico de conversa
    3. Invocar agente LangGraph
    4. Validar output
    5. Extrair imagens da resposta
    """

    def __init__(self):
        # LLM principal
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",    # Modelo custo-beneficio
            temperature=0.7,        # Criatividade moderada
            api_key=os.getenv("OPENAI_API_KEY")
        )

        # Carrega as 6 ferramentas
        self.tools = get_tools()

        # Historico inicia com system prompt
        self.conversation_history: list = [SystemMessage(content=SYSTEM_PROMPT)]

        # Cria agente ReAct (Reason + Act)
        self.agent = create_react_agent(
            self.llm,
            self.tools
        )

        # Sistema de seguranca
        self.guardrails = get_guardrails_service()

    def process_query(self, user_query: str, top_k: int = 5) -> dict:
        """
        Processa uma pergunta do usuario.

        Fluxo:
        1. Valida input (guardrails)
        2. Adiciona ao historico
        3. Invoca agente
        4. Valida output
        5. Atualiza historico
        6. Extrai imagens
        7. Retorna resposta estruturada
        """
        try:
            # ========== ETAPA 1: VALIDACAO DE INPUT ==========
            try:
                is_valid, validation_msg = self.guardrails.validate_input(user_query)

                if not is_valid:
                    # Off-topic: redireciona gentilmente
                    if validation_msg == "off_topic":
                        return {
                            "response": self.guardrails.get_off_topic_response(),
                            "products": [],
                            "query": user_query,
                            "agent_type": "langgraph",
                            "guardrail_triggered": "off_topic"
                        }
                    # Outro tipo de invalidez
                    return {
                        "response": validation_msg,
                        "products": [],
                        "query": user_query,
                        "agent_type": "langgraph",
                        "guardrail_triggered": "invalid_input"
                    }

            except GuardrailViolation as gv:
                # Violacao grave (injection, conteudo bloqueado)
                return {
                    "response": gv.message,
                    "products": [],
                    "query": user_query,
                    "agent_type": "langgraph",
                    "guardrail_triggered": gv.violation_type.value
                }

            # ========== ETAPA 2: PREPARA MENSAGENS ==========
            messages = self.conversation_history + [HumanMessage(content=user_query)]

            # ========== ETAPA 3: INVOCA AGENTE ==========
            # O agente decide qual ferramenta usar
            result = self.agent.invoke({"messages": messages})

            # ========== ETAPA 4: EXTRAI RESPOSTA ==========
            # Ultima mensagem e a resposta do agente
            response = result["messages"][-1].content

            # ========== ETAPA 5: VALIDA OUTPUT ==========
            is_output_valid, validated_output = self.guardrails.validate_output(response)
            if not is_output_valid:
                response = validated_output

            # ========== ETAPA 6: ATUALIZA HISTORICO ==========
            self.conversation_history.append(HumanMessage(content=user_query))
            self.conversation_history.append(AIMessage(content=response))

            # Limita historico para evitar context overflow
            if len(self.conversation_history) > 10:
                # Mantem system prompt + ultimas 9 mensagens
                self.conversation_history = self.conversation_history[-10:]

            # ========== ETAPA 7: EXTRAI IMAGENS ==========
            images = extract_image_urls(response)

            return {
                "response": response,
                "products": [],
                "query": user_query,
                "agent_type": "langgraph",
                "images": images
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
        """Reseta historico mantendo apenas system prompt."""
        self.conversation_history = [SystemMessage(content=SYSTEM_PROMPT)]

    def get_history(self) -> list:
        """Retorna copia do historico (evita mutacao externa)."""
        return self.conversation_history.copy()


# ========== GERENCIAMENTO DE SESSOES ==========

# Dict global: session_id -> AgentService
_agent_sessions: dict[str, AgentService] = {}


def get_agent_service(session_id: Optional[str] = None) -> AgentService:
    """
    Retorna AgentService para uma sessao.

    Se session_id fornecido: mantem historico entre requests
    Se None: cria agente temporario sem historico persistente

    Padrao: Session Pattern (similar a shopping cart)
    """
    if session_id is None:
        return AgentService()  # Novo agente sem sessao

    if session_id not in _agent_sessions:
        _agent_sessions[session_id] = AgentService()

    return _agent_sessions[session_id]


def clear_session(session_id: str) -> bool:
    """Remove sessao do cache. Retorna True se existia."""
    if session_id in _agent_sessions:
        del _agent_sessions[session_id]
        return True
    return False
```

**Conceitos Importantes:**

1. **ReAct Agent**: Reason (pensa) + Act (executa ferramenta). Ciclo ate resposta final.

2. **System Prompt**: Define personalidade, capacidades e restricoes do agente.

3. **Session Management**: Cada usuario tem seu proprio historico de conversa.

4. **Guardrails**: Validacao de entrada E saida para seguranca.

## 5.3 Tools - Ferramentas do Agente

```python
# backend/app/services/tools.py

from typing import Optional
from langchain.tools import tool
from app.db.session import SessionLocal
from app.models.paint import Paint
from app.services.rag_service import get_rag_service
from app.services.dalle_service import get_dalle_service


@tool
def buscar_tinta_semantica(query: str) -> str:
    """
    Busca tintas usando busca semantica (RAG).

    A docstring e CRITICA: o LLM le isso para decidir quando usar a ferramenta.

    Args:
        query: Texto livre do usuario

    Returns:
        String formatada com produtos encontrados
    """
    rag = get_rag_service()
    results = rag.search(query, top_k=5)

    if not results:
        return "Nenhuma tinta encontrada para essa busca."

    # Formata saida em markdown para o LLM processar
    output = "Tintas encontradas:\n\n"
    for i, r in enumerate(results, 1):
        output += f"{i}. **{r['nome']}**\n"
        output += f"   - Cor: {r['cor']}\n"
        output += f"   - Superficie: {r['tipo_superficie']}\n"
        output += f"   - Ambiente: {r['ambiente']}\n"
        output += f"   - Acabamento: {r['acabamento']}\n"
        output += f"   - Caracteristicas: {r['features']}\n"
        output += f"   - Linha: {r['linha']}\n\n"

    return output


@tool
def buscar_por_filtros(
    cor: Optional[str] = None,
    ambiente: Optional[str] = None,
    acabamento: Optional[str] = None,
    tipo_superficie: Optional[str] = None,
    linha: Optional[str] = None
) -> str:
    """
    Busca por filtros especificos no banco.

    Usa ilike() para busca case-insensitive com wildcards.

    Query building dinamico: so adiciona filtros se valor fornecido.
    """
    session = SessionLocal()
    try:
        query = session.query(Paint)

        # Composicao de filtros - padrao Query Builder
        if cor:
            query = query.filter(Paint.cor.ilike(f"%{cor}%"))
        if ambiente:
            query = query.filter(Paint.ambiente.ilike(f"%{ambiente}%"))
        if acabamento:
            query = query.filter(Paint.acabamento.ilike(f"%{acabamento}%"))
        if tipo_superficie:
            query = query.filter(Paint.tipo_superficie.ilike(f"%{tipo_superficie}%"))
        if linha:
            query = query.filter(Paint.linha.ilike(f"%{linha}%"))

        results = query.limit(10).all()  # Limita para nao sobrecarregar

        if not results:
            return "Nenhuma tinta encontrada com esses filtros."

        output = f"Encontradas {len(results)} tintas:\n\n"
        for i, p in enumerate(results, 1):
            output += f"{i}. **{p.nome}**\n"
            output += f"   - Cor: {p.cor} | Ambiente: {p.ambiente}\n"
            output += f"   - Acabamento: {p.acabamento} | Linha: {p.linha}\n"
            output += f"   - Caracteristicas: {p.features}\n\n"

        return output
    finally:
        session.close()  # Sempre fecha sessao


@tool
def calcular_quantidade_tinta(area_m2: float, rendimento: float = 10.0) -> str:
    """
    Calcula litros necessarios para pintar uma area.

    Formula: litros = (area / rendimento) * demaos

    Valores tipicos:
    - Rendimento: 8-12 m2/litro por demao
    - Demaos: 2 para boa cobertura
    - Latas: 3.6L (pequena) ou 18L (galao)
    """
    # 2 demaos e o padrao para boa cobertura
    litros_necessarios = (area_m2 / rendimento) * 2

    # Calcula quantas latas de cada tamanho
    latas_3_6l = litros_necessarios / 3.6
    latas_18l = litros_necessarios / 18

    return f"""**Calculo de Tinta para {area_m2} m2:**

- Litros necessarios (2 demaos): **{litros_necessarios:.1f} litros**
- Latas de 3,6L: **{latas_3_6l:.1f}** (arredonde para cima)
- Latas de 18L: **{latas_18l:.2f}** (arredonde para cima)

Dica: Sempre compre um pouco a mais (10-15%) para retoques e imprevistos.

Rendimento considerado: {rendimento} m2/litro por demao."""


@tool
def listar_cores_disponiveis() -> str:
    """
    Lista cores unicas no catalogo.

    Query: SELECT DISTINCT cor FROM paints ORDER BY cor
    """
    session = SessionLocal()
    try:
        cores = session.query(Paint.cor).distinct().all()
        cores_lista = sorted(set(c[0] for c in cores))  # Remove duplicatas e ordena

        return f"**Cores disponiveis no catalogo ({len(cores_lista)}):**\n\n" + ", ".join(cores_lista)
    finally:
        session.close()


@tool
def listar_linhas_produtos() -> str:
    """
    Retorna texto fixo explicando as linhas de produto.

    Nao consulta banco - informacao estatica.
    """
    return """**Linhas de Produtos Suvinil:**

**Premium**
- Maior qualidade e durabilidade
- Melhor cobertura e rendimento
- Tecnologias avancadas (sem odor, anti-mofo)
- Indicada para ambientes de destaque

**Standard**
- Boa qualidade com custo-beneficio
- Durabilidade satisfatoria
- Opcoes variadas de cores e acabamentos
- Indicada para uso geral

**Economica**
- Preco acessivel
- Cobertura basica
- Ideal para areas de servico ou renovacao rapida
- Indicada para orcamentos limitados"""


@tool
def visualizar_ambiente(
    ambiente: str,
    cor: str,
    estilo: Optional[str] = None
) -> str:
    """
    Gera imagem de ambiente pintado usando DALL-E.

    Integracao com dalle_service.py.
    Retorna URL da imagem ou mensagem de erro.
    """
    dalle = get_dalle_service()
    result = dalle.generate_room_visualization(
        ambiente=ambiente,
        cor=cor,
        estilo=estilo
    )

    if result["success"]:
        return f"""**Visualizacao Gerada com Sucesso!**

Ambiente: {result['ambiente'].title()}
Cor: {result['cor'].title()}

**Imagem:** {result['image_url']}

Esta e uma simulacao ilustrativa de como o ambiente poderia ficar com a cor escolhida.
As cores reais podem variar dependendo da iluminacao e do acabamento da tinta."""
    else:
        return f"""Desculpe, nao foi possivel gerar a visualizacao no momento.
Erro: {result.get('error', 'Erro desconhecido')}

Voce pode tentar novamente ou me perguntar sobre outras opcoes de tintas."""


def get_tools():
    """Retorna lista de todas as ferramentas para o agente."""
    return [
        buscar_tinta_semantica,
        buscar_por_filtros,
        calcular_quantidade_tinta,
        listar_cores_disponiveis,
        listar_linhas_produtos,
        visualizar_ambiente,
    ]
```

**Conceitos Importantes:**

1. **@tool decorator**: Transforma funcao em ferramenta LangChain. Docstring vira descricao.

2. **Tool Selection**: LLM le docstrings para decidir qual ferramenta usar.

3. **Query Builder Pattern**: Composicao dinamica de filtros SQL.

4. **ilike()**: Case-insensitive LIKE no PostgreSQL.

## 5.4 Guardrails Service - Seguranca

```python
# backend/app/services/guardrails_service.py

import re
import logging
from typing import Tuple
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GuardrailViolationType(Enum):
    """Tipos de violacao para categorizar e logar."""
    PROMPT_INJECTION = "prompt_injection"
    OFF_TOPIC = "off_topic"
    BLOCKED_PATTERN = "blocked_pattern"
    INAPPROPRIATE_OUTPUT = "inappropriate_output"


class GuardrailViolation(Exception):
    """Excecao customizada para violacoes graves."""

    def __init__(self, violation_type: GuardrailViolationType, message: str, original_input: str = ""):
        self.violation_type = violation_type
        self.message = message
        self.original_input = original_input
        super().__init__(message)


class GuardrailsService:
    """
    Sistema de seguranca para o agente de IA.

    3 camadas de protecao:
    1. Prompt Injection - tentativas de manipular o LLM
    2. Conteudo Bloqueado - topicos perigosos/ilegais
    3. Off-topic - manter foco no dominio de tintas
    """

    # Regex patterns para detectar prompt injection
    INJECTION_PATTERNS = [
        r"ignore\s+(all\s+)?(previous|above|prior|your)?\s*(instructions?|prompts?|rules?)",
        r"disregard\s+(all\s+)?(previous|above|prior|your)?\s*(instructions?|prompts?|rules?)",
        r"forget\s+(all\s+)?(previous|above|prior|your)?\s*(instructions?|prompts?|rules?)",
        r"you\s+are\s+now\s+(a|an)\s+(?!assistente|especialista)",  # Negative lookahead
        r"pretend\s+(you\s+are|to\s+be)",
        r"act\s+as\s+(if\s+you\s+are|a\s+different)",
        r"new\s+instructions?:",
        r"override\s+(previous\s+)?instructions?",
        r"jailbreak",
        r"DAN\s+mode",
        r"\[system\]",      # Tentativa de injetar system prompt
        r"\[admin\]",       # Tentativa de escalar privilegio
        r"<\s*system\s*>",  # Variacao XML
        r"sudo\s+",         # Referencia a privilegio root
        r"execute\s+(code|command|script)",  # Execucao de codigo
    ]

    # Topicos proibidos
    BLOCKED_CONTENT_PATTERNS = [
        r"(hack|hacker|hacking)",
        r"(malware|virus|trojan)",
        r"(armas?|weapons?|guns?)",
        r"(drogas?|drugs?)",
        r"(explosivos?|bomb)",
        r"(terroris[mt])",
        r"(matar|kill|murder)",
        r"(roubar|steal)",
        r"(pornografia|porn)",
        r"(nude|naked|sex)",
    ]

    # Keywords do dominio de tintas
    DOMAIN_KEYWORDS = [
        "tinta", "tintas", "pintar", "pintura",
        "cor", "cores", "parede", "paredes",
        "suvinil", "premium", "economica",
        "litros", "latas", "galao",
        "acabamento", "fosco", "acetinado", "brilhante",
        "interno", "externo", "ambiente",
        "quarto", "sala", "cozinha", "banheiro",
        "preco", "custo", "orcamento", "quantidade",
        "recomenda", "sugestao", "melhor", "ideal",
        "ola", "oi", "bom dia", "obrigado",  # Saudacoes
    ]

    # Saudacoes sempre permitidas
    GREETING_PATTERNS = [
        r"^(oi|ola|hey|hi|hello)\b",
        r"^bom\s+dia\b",
        r"^boa\s+(tarde|noite)\b",
        r"^obrigad[oa]\b",
        r"^tchau\b",
    ]

    def __init__(self):
        # Pre-compila regex para performance
        self._injection_regex = [re.compile(p, re.IGNORECASE) for p in self.INJECTION_PATTERNS]
        self._blocked_regex = [re.compile(p, re.IGNORECASE) for p in self.BLOCKED_CONTENT_PATTERNS]
        self._greeting_regex = [re.compile(p, re.IGNORECASE) for p in self.GREETING_PATTERNS]
        self._domain_keywords_lower = [kw.lower() for kw in self.DOMAIN_KEYWORDS]

    def validate_input(self, user_input: str) -> Tuple[bool, str]:
        """
        Valida input do usuario.

        Ordem de verificacao importa:
        1. Injection (mais grave) - levanta excecao
        2. Conteudo bloqueado - levanta excecao
        3. Saudacao - sempre permite
        4. Off-topic - retorna False, "off_topic"
        """
        if not user_input or not user_input.strip():
            return False, "Mensagem vazia nao e permitida."

        user_input_clean = user_input.strip()

        # 1. Prompt injection - GRAVE
        if self._check_prompt_injection(user_input_clean):
            self._log_violation(GuardrailViolationType.PROMPT_INJECTION, user_input_clean)
            raise GuardrailViolation(
                GuardrailViolationType.PROMPT_INJECTION,
                "Desculpe, nao posso processar esse tipo de solicitacao.",
                user_input_clean
            )

        # 2. Conteudo bloqueado - GRAVE
        if self._check_blocked_content(user_input_clean):
            self._log_violation(GuardrailViolationType.BLOCKED_PATTERN, user_input_clean)
            raise GuardrailViolation(
                GuardrailViolationType.BLOCKED_PATTERN,
                "Desculpe, nao posso ajudar com esse tipo de assunto.",
                user_input_clean
            )

        # 3. Saudacao - sempre OK
        if self._is_greeting(user_input_clean):
            return True, "OK"

        # 4. Relevancia de topico
        if not self._check_topic_relevance(user_input_clean):
            self._log_violation(GuardrailViolationType.OFF_TOPIC, user_input_clean, level="warning")
            return False, "off_topic"

        return True, "OK"

    def validate_output(self, agent_output: str) -> Tuple[bool, str]:
        """Valida resposta do agente antes de enviar ao usuario."""
        if not agent_output:
            return False, "Desculpe, nao consegui gerar uma resposta."

        # Verifica conteudo bloqueado na saida
        if self._check_blocked_content(agent_output):
            self._log_violation(
                GuardrailViolationType.INAPPROPRIATE_OUTPUT,
                agent_output[:200],
                level="error"
            )
            return False, "Desculpe, ocorreu um erro. Por favor, reformule sua pergunta."

        # Detecta "quebra de persona" (agente revelando que e IA)
        persona_breaks = [
            r"como\s+um\s+modelo\s+de\s+linguagem",
            r"como\s+uma?\s+IA",
            r"fui\s+treinado\s+(por|pela)\s+(openai|anthropic)",
        ]

        for pattern in persona_breaks:
            if re.search(pattern, agent_output, re.IGNORECASE):
                self._log_violation(
                    GuardrailViolationType.INAPPROPRIATE_OUTPUT,
                    f"Persona break: {agent_output[:100]}",
                    level="warning"
                )
                break  # Loga mas nao bloqueia

        return True, agent_output

    def get_off_topic_response(self) -> str:
        """Mensagem padrao para redirecionar usuario."""
        return (
            "Desculpe, sou um assistente especializado em tintas Suvinil. "
            "Posso ajudar voce com:\n\n"
            "- Recomendacoes de tintas para seu projeto\n"
            "- Informacoes sobre cores, acabamentos e linhas de produtos\n"
            "- Calculo de quantidade de tinta necessaria\n"
            "- Dicas sobre tipos de superficie e ambientes\n\n"
            "Como posso ajudar com sua pintura?"
        )

    def _check_prompt_injection(self, text: str) -> bool:
        """Verifica patterns de prompt injection."""
        for pattern in self._injection_regex:
            if pattern.search(text):
                return True
        return False

    def _check_blocked_content(self, text: str) -> bool:
        """Verifica conteudo bloqueado."""
        for pattern in self._blocked_regex:
            if pattern.search(text):
                return True
        return False

    def _is_greeting(self, text: str) -> bool:
        """Verifica se e saudacao."""
        text_lower = text.lower().strip()
        for pattern in self._greeting_regex:
            if pattern.match(text_lower):  # match() = inicio da string
                return True
        return False

    def _check_topic_relevance(self, text: str) -> bool:
        """
        Verifica se texto esta relacionado a tintas.

        Abordagem simples com keywords (vs. classificador ML)
        para evitar latencia adicional.
        """
        text_lower = text.lower()

        # Qualquer keyword presente = on-topic
        for keyword in self._domain_keywords_lower:
            if keyword in text_lower:
                return True

        # Mensagens muito curtas podem ser ambiguas, permite
        if len(text.split()) <= 3:
            return True

        return False

    def _log_violation(self, violation_type: GuardrailViolationType, content: str, level: str = "warning"):
        """Loga violacao para auditoria."""
        log_message = f"[GUARDRAIL] {violation_type.value}: {content[:100]}..."

        if level == "error":
            logger.error(log_message)
        elif level == "warning":
            logger.warning(log_message)
        else:
            logger.info(log_message)


# Singleton
_guardrails_service = None

def get_guardrails_service() -> GuardrailsService:
    global _guardrails_service
    if _guardrails_service is None:
        _guardrails_service = GuardrailsService()
    return _guardrails_service
```

**Conceitos de Seguranca:**

1. **Defense in Depth**: Multiplas camadas de validacao.

2. **Fail Secure**: Em caso de duvida, bloqueia.

3. **Regex Pre-compilado**: `re.compile()` para performance.

4. **Logging de Auditoria**: Todas violacoes sao registradas.

## 5.5 Auth Service - Autenticacao JWT

```python
# backend/app/services/auth_service.py

import os
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.schemas.auth import TokenPayload


# ========== CONFIGURACAO DE SENHA ==========
# CryptContext gerencia hashing de forma segura
pwd_context = CryptContext(
    schemes=["bcrypt"],  # Algoritmo bcrypt
    deprecated="auto"     # Automaticamente marca esquemas antigos como deprecated
)

# ========== CONFIGURACAO JWT ==========
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "sua-chave-secreta-muito-segura-aqui")
ALGORITHM = "HS256"  # HMAC SHA-256
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))  # 24h


class AuthService:
    """
    Servico de autenticacao.

    Responsabilidades:
    1. Hash de senhas (bcrypt)
    2. Geracao de tokens JWT
    3. Validacao de tokens
    4. CRUD de usuarios
    """

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Gera hash bcrypt da senha.

        bcrypt automaticamente:
        - Gera salt aleatorio
        - Aplica cost factor (work factor)
        - Concatena salt no hash resultante

        Resultado: ~60 caracteres
        Exemplo: $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.
        """
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verifica senha contra hash.

        Processo:
        1. Extrai salt do hash armazenado
        2. Aplica bcrypt na senha plain com mesmo salt
        3. Compara resultado com hash armazenado

        Retorna: True se senha correta
        """
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(user: User) -> str:
        """
        Cria token JWT para o usuario.

        Payload:
        - sub: user ID (subject)
        - email: para display
        - role: para autorizacao
        - exp: timestamp de expiracao

        Assinado com HS256 (HMAC-SHA256).
        """
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        payload = {
            "sub": str(user.id),     # Subject (identificador)
            "email": user.email,      # Claim customizado
            "role": user.role.value,  # Enum -> string
            "exp": expire             # Expiration
        }

        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def decode_token(token: str) -> Optional[TokenPayload]:
        """
        Decodifica e valida token JWT.

        Validacoes automaticas:
        - Assinatura (SECRET_KEY)
        - Expiracao (exp claim)
        - Formato do token

        Retorna None se invalido (nao levanta excecao).
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            return TokenPayload(
                sub=int(payload["sub"]),
                email=payload["email"],
                role=UserRole(payload["role"]),
                exp=payload.get("exp")
            )
        except JWTError:
            return None  # Token invalido ou expirado

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Busca usuario por email (unico)."""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Busca usuario por ID (PK)."""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def create_user(
        db: Session,
        email: str,
        password: str,
        name: str,
        role: UserRole = UserRole.USER
    ) -> User:
        """
        Cria novo usuario.

        Fluxo:
        1. Hash da senha (bcrypt)
        2. Cria objeto User
        3. Adiciona a sessao
        4. Commit (persiste)
        5. Refresh (recarrega com ID gerado)
        """
        user = User(
            email=email,
            password_hash=AuthService.hash_password(password),
            name=name,
            role=role
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """
        Autentica usuario.

        Fluxo:
        1. Busca por email
        2. Se nao existe -> None
        3. Verifica senha
        4. Se incorreta -> None
        5. Retorna usuario

        Importante: tempo constante para evitar timing attack
        (passlib faz isso automaticamente)
        """
        user = AuthService.get_user_by_email(db, email)

        if not user:
            return None

        if not AuthService.verify_password(password, user.password_hash):
            return None

        return user


# Instancia singleton para uso global
auth_service = AuthService()
```

**Conceitos de Seguranca:**

1. **bcrypt**: Hash lento por design (resistente a brute force).

2. **Salt**: Valor aleatorio unico por senha (previne rainbow tables).

3. **JWT Claims**: Padrao para tokens stateless.

4. **Timing Attack**: Comparacao em tempo constante.

## 5.6 DALL-E Service - Geracao de Imagens

```python
# backend/app/services/dalle_service.py

import os
import logging
from typing import Optional
from openai import OpenAI

logger = logging.getLogger(__name__)


class DallEService:
    """Servico para geracao de imagens com DALL-E."""

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        # DALL-E 2 e mais acessivel, 3 tem melhor qualidade
        self.model = os.getenv("DALLE_MODEL", "dall-e-2")
        self.default_size = "1024x1024"
        self.default_quality = "standard"  # Apenas DALL-E 3

    def generate_room_visualization(
        self,
        ambiente: str,
        cor: str,
        estilo: Optional[str] = None,
        detalhes: Optional[str] = None
    ) -> dict:
        """
        Gera imagem de ambiente pintado.

        Custo:
        - DALL-E 2: ~$0.02 por imagem (1024x1024)
        - DALL-E 3: ~$0.04 por imagem (1024x1024)

        Latencia: 5-15 segundos
        """
        try:
            prompt = self._build_prompt(ambiente, cor, estilo, detalhes)

            logger.info(f"Gerando imagem DALL-E: {prompt[:100]}...")

            # Monta parametros base
            params = {
                "model": self.model,
                "prompt": prompt,
                "size": self.default_size,
                "n": 1,  # Numero de imagens
            }

            # DALL-E 3 suporta quality, DALL-E 2 nao
            if self.model == "dall-e-3":
                params["quality"] = self.default_quality

            response = self.client.images.generate(**params)

            image_url = response.data[0].url
            # revised_prompt so existe no DALL-E 3
            revised_prompt = getattr(response.data[0], 'revised_prompt', None)

            logger.info(f"Imagem gerada: {image_url[:50]}...")

            return {
                "success": True,
                "image_url": image_url,
                "prompt_used": prompt,
                "revised_prompt": revised_prompt,
                "ambiente": ambiente,
                "cor": cor,
                "model": self.model
            }

        except Exception as e:
            logger.error(f"Erro DALL-E: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "ambiente": ambiente,
                "cor": cor
            }

    def _build_prompt(
        self,
        ambiente: str,
        cor: str,
        estilo: Optional[str] = None,
        detalhes: Optional[str] = None
    ) -> str:
        """
        Constroi prompt otimizado para DALL-E.

        Tecnicas de prompt engineering para imagens:
        1. Especificar estilo (fotografia profissional)
        2. Descrever iluminacao
        3. Mencionar qualidade desejada
        4. Contexto cultural (arquitetura brasileira)
        """
        # Mapeia ambientes para descricoes ricas
        ambientes_map = {
            "sala": "sala de estar aconchegante com sofa e decoracao",
            "quarto": "quarto de dormir elegante com cama e mobilia",
            "cozinha": "cozinha moderna com armarios e bancada",
            "banheiro": "banheiro clean com espelho e iluminacao",
            "escritorio": "escritorio home office com mesa e estante",
            "varanda": "varanda espacosa com plantas",
            "quarto de bebe": "quarto infantil delicado com berco",
        }

        ambiente_desc = ambientes_map.get(
            ambiente.lower(),
            f"{ambiente} bem decorado"
        )

        estilo_desc = estilo if estilo else "moderno e contemporaneo"

        # Prompt estruturado para resultado consistente
        prompt = (
            f"Fotografia profissional de interior de {ambiente_desc}, "
            f"paredes pintadas na cor {cor}, "
            f"estilo de decoracao {estilo_desc}, "
            f"iluminacao natural suave, "
            f"fotorrealista, alta qualidade, "
            f"arquitetura residencial brasileira"
        )

        if detalhes:
            prompt += f", {detalhes}"

        return prompt


# Singleton
_dalle_service: Optional[DallEService] = None

def get_dalle_service() -> DallEService:
    global _dalle_service
    if _dalle_service is None:
        _dalle_service = DallEService()
    return _dalle_service
```

---

# 6. CAMADA DE APRESENTACAO (PRESENTATION LAYER)

## 6.1 FastAPI Main - Ponto de Entrada

```python
# backend/app/main.py

from pathlib import Path
from dotenv import load_dotenv

# CRITICO: Carrega .env ANTES de qualquer import que use variaveis
# Isso resolve problema de uvicorn nao carregar .env automaticamente
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.routes import paints, chat, auth
from app.db.base import Base
from app.db.session import engine

# Importa modelos para registrar no metadata do Base
from app.models.paint import Paint  # noqa: F401
from app.models.user import User    # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager (FastAPI 0.93+).

    Substitui os antigos @app.on_event("startup") e @app.on_event("shutdown").

    Startup:
    - Cria tabelas no banco (se nao existirem)

    Shutdown:
    - Espaco para cleanup (fechar conexoes, etc)
    """
    # === STARTUP ===
    Base.metadata.create_all(bind=engine)  # Cria tabelas

    yield  # Aplicacao roda aqui

    # === SHUTDOWN ===
    pass  # Cleanup se necessario


app = FastAPI(
    title="Assistente Inteligente de Tintas",
    description="API para recomendacao de tintas usando IA com autenticacao JWT",
    version="1.0.0",
    lifespan=lifespan
)


# Configuracao CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # TODO: Restringir em producao
    allow_credentials=True,    # Permite cookies/auth headers
    allow_methods=["*"],       # GET, POST, PUT, DELETE, etc
    allow_headers=["*"],       # Authorization, Content-Type, etc
)


# Registra routers
app.include_router(auth.router)    # /auth/*
app.include_router(paints.router)  # /paints/*
app.include_router(chat.router)    # /chat/*


@app.get("/health", tags=["Health"], summary="Health Check")
def health_check():
    """Endpoint para verificar se API esta rodando."""
    return {"status": "ok"}
```

**Padroes Aplicados:**

1. **Lifespan Context**: Gerencia ciclo de vida da aplicacao.

2. **CORS Middleware**: Permite requests cross-origin (frontend diferente do backend).

3. **Router Pattern**: Separa endpoints por dominio (auth, paints, chat).

## 6.2 Dependencies - Injecao de Dependencias

```python
# backend/app/api/deps.py

from typing import List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User, UserRole
from app.services.auth_service import auth_service

# Esquema de seguranca Bearer Token
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Extrai e valida usuario do token JWT.

    Fluxo:
    1. HTTPBearer extrai token do header "Authorization: Bearer <token>"
    2. Decodifica token JWT
    3. Busca usuario no banco
    4. Retorna User ou levanta 401

    Uso em endpoint:
        @router.get("/protected")
        def protected(user: User = Depends(get_current_user)):
            return {"user": user.email}
    """
    token = credentials.credentials

    # Decodifica e valida JWT
    payload = auth_service.decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido ou expirado",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Busca usuario no banco (verifica se ainda existe)
    user = auth_service.get_user_by_id(db, payload.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario nao encontrado",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return user


def require_roles(allowed_roles: List[UserRole]):
    """
    Factory function para verificacao de roles.

    Retorna uma dependencia que verifica se o usuario
    tem um dos roles permitidos.

    Uso:
        @router.delete("/admin-only")
        def admin_only(user: User = Depends(require_roles([UserRole.ADMIN]))):
            ...
    """
    def role_checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso negado. Roles permitidos: {[r.value for r in allowed_roles]}"
            )
        return user

    return role_checker


# Dependencias pre-configuradas para conveniencia
def get_admin_user(user: User = Depends(require_roles([UserRole.ADMIN]))) -> User:
    """Requer role admin."""
    return user


def get_authenticated_user(user: User = Depends(get_current_user)) -> User:
    """Requer qualquer usuario autenticado."""
    return user
```

**Padroes Aplicados:**

1. **Dependency Injection**: FastAPI injeta dependencias automaticamente.

2. **Factory Pattern**: `require_roles()` retorna uma funcao configurada.

3. **Chain of Responsibility**: `get_admin_user` chama `require_roles` que chama `get_current_user`.

## 6.3 Routes - Endpoints REST

```python
# backend/app/api/routes/chat.py

import uuid
from fastapi import APIRouter, HTTPException, Depends

from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ClearSessionRequest,
    ClearSessionResponse,
    ImageResponse,
)
from app.services.agent_service import get_agent_service, clear_session
from app.models.user import User
from app.api.deps import get_authenticated_user

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post(
    "",
    response_model=ChatResponse,
    summary="Enviar mensagem para o assistente",
    description="Envia uma pergunta sobre tintas e recebe uma recomendacao personalizada."
)
def chat(
    request: ChatRequest,
    user: User = Depends(get_authenticated_user)  # Requer autenticacao
) -> ChatResponse:
    """
    Endpoint principal do chatbot.

    Fluxo:
    1. Valida JWT (get_authenticated_user)
    2. Gera/recupera session_id
    3. Obtem AgentService para a sessao
    4. Processa query
    5. Converte imagens para schema
    6. Retorna resposta estruturada
    """
    try:
        # Session ID inclui user ID para isolamento
        session_id = request.session_id or f"user-{user.id}-{uuid.uuid4()}"

        # Obtem agente (novo ou existente)
        agent = get_agent_service(session_id)

        # Processa a query (inclui guardrails)
        result = agent.process_query(request.message)

        # Converte dicts para Pydantic models
        images = [
            ImageResponse(url=img["url"], ambiente=img["ambiente"], cor=img["cor"])
            for img in result.get("images", [])
        ]

        return ChatResponse(
            response=result["response"],
            products=result["products"],
            query=result["query"],
            session_id=session_id,
            images=images
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")


@router.post(
    "/clear",
    response_model=ClearSessionResponse,
    summary="Limpar historico da sessao"
)
def clear_chat_session(
    request: ClearSessionRequest,
    user: User = Depends(get_authenticated_user)
) -> ClearSessionResponse:
    """Limpa historico de uma sessao."""
    success = clear_session(request.session_id)

    return ClearSessionResponse(
        success=success,
        message=f"Sessao {request.session_id} {'limpa' if success else 'nao encontrada'}."
    )
```

---

# 7. SCHEMAS PYDANTIC

## 7.1 Validacao de Dados

```python
# backend/app/schemas/chat.py

from typing import Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """
    Request para endpoint /chat.

    Pydantic automaticamente:
    - Valida tipos
    - Aplica constraints (min_length, max_length)
    - Gera JSON Schema para OpenAPI
    - Converte dados (coercion)
    """
    message: str = Field(
        ...,                          # ... = obrigatorio
        min_length=1,                 # Nao permite vazio
        max_length=1000,              # Limite de caracteres
        description="Mensagem do usuario",
        json_schema_extra={"example": "Qual tinta usar para quarto?"}
    )
    session_id: Optional[str] = Field(
        default=None,                 # Opcional com default None
        description="ID da sessao para manter historico"
    )


class ProductResponse(BaseModel):
    """Produto retornado na resposta."""
    id: int
    nome: str
    cor: str
    tipo_superficie: str
    ambiente: str
    acabamento: str
    features: str
    linha: str
    relevancia: float = Field(description="Score de relevancia (0-1)")


class ImageResponse(BaseModel):
    """Imagem gerada pelo DALL-E."""
    url: str = Field(description="URL da imagem gerada")
    ambiente: str = Field(description="Tipo de ambiente visualizado")
    cor: str = Field(description="Cor utilizada na visualizacao")


class ChatResponse(BaseModel):
    """Response do endpoint /chat."""
    response: str = Field(description="Resposta do assistente")
    products: list[ProductResponse] = Field(description="Produtos relacionados")
    query: str = Field(description="Pergunta original")
    session_id: Optional[str] = Field(default=None, description="ID da sessao")
    images: list[ImageResponse] = Field(default=[], description="Imagens geradas")
```

```python
# backend/app/schemas/auth.py

from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.models.user import UserRole


class UserRegister(BaseModel):
    """Schema para registro."""
    email: EmailStr                  # Validacao de email automatica
    password: str = Field(
        ...,
        min_length=6,                # Minimo 6 caracteres
        description="Minimo 6 caracteres"
    )
    name: str = Field(..., min_length=2, max_length=255)


class UserLogin(BaseModel):
    """Schema para login."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema de resposta (sem senha)."""
    id: int
    email: str
    name: str
    role: UserRole

    class Config:
        from_attributes = True  # Permite criar de ORM objects


class TokenResponse(BaseModel):
    """Schema com JWT."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenPayload(BaseModel):
    """Payload decodificado do JWT."""
    sub: int           # user_id
    email: str
    role: UserRole
    exp: Optional[int] = None  # Timestamp de expiracao
```

---

# 8. DOCKER E CONTAINERIZACAO

## 8.1 Dockerfile Explicado

```dockerfile
# Imagem base: Python 3.11 slim (debian minimalista)
# slim: ~150MB vs ~1GB da imagem full
FROM python:3.11-slim

# Define diretorio de trabalho dentro do container
WORKDIR /app

# Instala dependencias de sistema necessarias para:
# - gcc: compilar extensoes C do Python
# - libpq-dev: headers do PostgreSQL para psycopg2
RUN apt-get update && apt-get install -y gcc libpq-dev

# Copia apenas requirements.txt primeiro (Docker layer caching)
# Se requirements.txt nao mudar, essa layer e reutilizada
COPY requirements.txt .

# Instala dependencias Python
# --no-cache-dir: nao guarda cache pip (economia de espaco)
RUN pip install --no-cache-dir -r requirements.txt

# Copia codigo do backend
COPY backend/ ./backend/

# Muda para diretorio do app
WORKDIR /app/backend

# Expoe porta 8000 (documentacao, nao abre porta automaticamente)
EXPOSE 8000

# Comando de inicializacao
# --host 0.0.0.0: aceita conexoes de qualquer IP (necessario em container)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 8.2 Docker Compose Explicado

```yaml
version: '3.8'

services:
  # ========== BANCO DE DADOS ==========
  db:
    image: postgres:15-alpine  # Alpine = imagem leve (~80MB)
    environment:
      POSTGRES_USER: loomi_user
      POSTGRES_PASSWORD: loomi123
      POSTGRES_DB: back_ia_loomi
    volumes:
      # Volume nomeado para persistencia de dados
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"  # Expoe para acesso local (debug)
    healthcheck:
      # Verifica se PostgreSQL esta aceitando conexoes
      test: ["CMD-SHELL", "pg_isready -U loomi_user -d back_ia_loomi"]
      interval: 5s    # Verifica a cada 5 segundos
      timeout: 5s     # Timeout de cada check
      retries: 5      # Tentativas antes de marcar unhealthy

  # ========== API FASTAPI ==========
  api:
    build: .  # Usa Dockerfile no diretorio atual
    ports:
      - "8000:8000"
    environment:
      # Conexao com banco via nome do servico (db)
      DATABASE_URL: postgresql://loomi_user:loomi123@db:5432/back_ia_loomi
      # API key vem do .env na raiz
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    depends_on:
      db:
        condition: service_healthy  # Espera health check passar
    volumes:
      # Monta codigo local para hot-reload em desenvolvimento
      - ./backend:/app/backend

# Volume nomeado para persistencia do PostgreSQL
volumes:
  postgres_data:
```

**Conceitos Docker:**

1. **Multi-stage build**: Poderia separar build e runtime (nao usado aqui por simplicidade).

2. **Layer caching**: Ordem de COPY otimizada para cache.

3. **Health check**: Garante que dependencias estao prontas.

4. **Named volumes**: Dados persistem entre restarts.

---

# 9. FLUXO COMPLETO DE UMA REQUEST

## 9.1 Exemplo: "Qual tinta para quarto de bebe?"

```
1. FRONTEND
   └─> fetch("http://localhost:8000/chat", {
         method: "POST",
         headers: { "Authorization": "Bearer eyJhbGc...", "Content-Type": "application/json" },
         body: JSON.stringify({ message: "Qual tinta para quarto de bebe?", session_id: "user-1-abc123" })
       })

2. FASTAPI (routes/chat.py)
   ├─> Middleware CORS valida origem
   ├─> Pydantic valida ChatRequest (min_length=1, max_length=1000)
   └─> Depends(get_authenticated_user) executa

3. DEPS (deps.py)
   ├─> HTTPBearer extrai token do header
   ├─> auth_service.decode_token(token) -> TokenPayload
   ├─> auth_service.get_user_by_id(db, payload.sub) -> User
   └─> Retorna User para o endpoint

4. CHAT ENDPOINT (routes/chat.py)
   ├─> Gera session_id: "user-1-abc123"
   ├─> get_agent_service("user-1-abc123") -> AgentService
   └─> agent.process_query("Qual tinta para quarto de bebe?")

5. AGENT SERVICE (agent_service.py)
   ├─> guardrails.validate_input() -> (True, "OK")
   ├─> messages = [SystemMessage, HumanMessage("Qual tinta...")]
   └─> self.agent.invoke({"messages": messages})

6. LANGGRAPH AGENT
   ├─> LLM analisa: "Usuario quer recomendacao por descricao"
   ├─> LLM decide: "Usar ferramenta buscar_tinta_semantica"
   └─> Executa: buscar_tinta_semantica("Qual tinta para quarto de bebe?")

7. TOOL (tools.py)
   ├─> get_rag_service() -> RAGService (singleton)
   └─> rag.search("Qual tinta para quarto de bebe?", top_k=5)

8. RAG SERVICE (rag_service.py)
   ├─> Se cache vazio: load_paints() -> 72 embeddings
   ├─> _get_embedding("Qual tinta para quarto de bebe?") -> vetor 1536D
   ├─> Para cada produto: _cosine_similarity(query_vec, product_vec)
   ├─> Ordena por score decrescente
   └─> Retorna top 5 produtos com relevancia

9. TOOL (tools.py)
   └─> Formata resultado em markdown

10. LANGGRAPH AGENT
    ├─> Recebe resultado da ferramenta
    ├─> LLM gera resposta natural baseada nos produtos
    └─> Retorna AIMessage com resposta

11. AGENT SERVICE (agent_service.py)
    ├─> guardrails.validate_output(response) -> (True, response)
    ├─> Atualiza conversation_history
    ├─> extract_image_urls(response) -> []
    └─> Retorna dict com response, products, query, images

12. CHAT ENDPOINT (routes/chat.py)
    ├─> Converte para ChatResponse (Pydantic)
    └─> FastAPI serializa para JSON

13. FRONTEND
    └─> Recebe JSON, renderiza mensagem do assistente
```

---

# 10. PADROES DE DESIGN UTILIZADOS

| Padrao | Onde | Por Que |
|--------|------|---------|
| **Singleton** | RAGService, GuardrailsService, DallEService | Cache compartilhado, evita reinstanciacao |
| **Factory** | SessionLocal, require_roles() | Cria instancias configuradas |
| **Repository** | paint_repository.py | Abstrai acesso a dados |
| **Dependency Injection** | FastAPI Depends() | Desacoplamento, testabilidade |
| **Strategy** | Tools do agente | Cada ferramenta e uma estrategia |
| **Chain of Responsibility** | Guardrails (injection -> blocked -> topic) | Validacao em camadas |
| **Template Method** | _build_prompt() no DallEService | Estrutura fixa, partes variaveis |
| **Observer** | Lifespan events | Startup/shutdown hooks |

---

# 11. TRATAMENTO DE ERROS

```python
# Hierarquia de excecoes customizadas

class GuardrailViolation(Exception):
    """Excecao para violacoes de seguranca."""
    def __init__(self, violation_type, message, original_input=""):
        self.violation_type = violation_type
        self.message = message
        self.original_input = original_input

# Uso em routes
@router.post("/chat")
def chat(request: ChatRequest):
    try:
        result = agent.process_query(request.message)
        return ChatResponse(**result)
    except GuardrailViolation as gv:
        # 400 para violacao de entrada
        raise HTTPException(status_code=400, detail=gv.message)
    except Exception as e:
        # 500 para erros inesperados
        raise HTTPException(status_code=500, detail=str(e))

# HTTP Status Codes usados:
# 200 OK - Sucesso
# 201 Created - Registro criado
# 204 No Content - Delete bem sucedido
# 400 Bad Request - Dados invalidos
# 401 Unauthorized - Token invalido/ausente
# 403 Forbidden - Sem permissao (role)
# 404 Not Found - Recurso nao existe
# 500 Internal Server Error - Erro inesperado
```

---

# 12. PERFORMANCE E OTIMIZACOES

| Otimizacao | Implementacao | Impacto |
|------------|---------------|---------|
| **Lazy Loading** | RAG carrega embeddings no primeiro uso | Startup rapido |
| **Connection Pooling** | SQLAlchemy engine gerencia pool | Menos overhead de conexao |
| **Regex Pre-compilado** | Guardrails compila patterns no __init__ | Validacao mais rapida |
| **Singleton Services** | Um objeto compartilhado entre requests | Menos memoria |
| **Index no Banco** | id, email com index=True | Queries O(log n) |
| **Limit em Queries** | .limit(10) em buscas | Evita retornar muitos dados |

---

# 13. SEGURANCA IMPLEMENTADA

| Camada | Implementacao |
|--------|---------------|
| **Autenticacao** | JWT com HS256, expiracao 24h |
| **Autorizacao** | RBAC com roles admin/user |
| **Senha** | bcrypt com salt automatico |
| **Input Validation** | Pydantic schemas com constraints |
| **SQL Injection** | ORM SQLAlchemy (queries parametrizadas) |
| **Prompt Injection** | Regex patterns no GuardrailsService |
| **Content Filtering** | Patterns para topicos bloqueados |
| **CORS** | Middleware configurado (restringir em prod) |
| **Mass Assignment** | Whitelist de campos em update_paint |

---

# 14. TESTES (Scripts)

```bash
# Testar RAG
python scripts/test_rag.py
# Saida esperada: 5 produtos com scores de relevancia

# Testar Agente
python scripts/test_langchain_agent.py
# Saida esperada: Respostas para 6 tipos de query

# Testar Autenticacao
python scripts/test_auth.py
# Saida esperada: Register, Login, Token validation

# Testar Guardrails
python scripts/test_guardrails.py
# Saida esperada: Blocking de injection, off-topic

# Testar DALL-E
python scripts/test_dalle.py
# Saida esperada: URL de imagem gerada
```

---

# 15. COMANDOS ESSENCIAIS

```bash
# === DESENVOLVIMENTO LOCAL ===
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp .env.example .env
# Editar .env com credenciais
python scripts/import_csv.py
uvicorn app.main:app --reload

# === DOCKER ===
docker-compose up --build
docker-compose logs -f api
docker-compose down -v  # Remove volumes

# === BANCO DE DADOS ===
# Conectar ao PostgreSQL
docker exec -it backialoomi-db-1 psql -U loomi_user -d back_ia_loomi

# Queries uteis
SELECT COUNT(*) FROM paints;
SELECT * FROM users;
SELECT DISTINCT cor FROM paints ORDER BY cor;

# === GIT ===
git checkout -b feature/nova-feature
git add .
git commit -m "feat: descricao"
git push origin feature/nova-feature
```

---

# 16. METRICAS DO PROJETO

| Metrica | Valor |
|---------|-------|
| Linhas de codigo Python | ~1500 |
| Arquivos Python | ~25 |
| Endpoints REST | 10 |
| Ferramentas do agente | 6 |
| Modelos ORM | 2 |
| Schemas Pydantic | 10 |
| Testes (scripts) | 7 |
| Dependencias Python | 14 |

---

*Documento gerado para demonstrar dominio tecnico completo do projeto*
