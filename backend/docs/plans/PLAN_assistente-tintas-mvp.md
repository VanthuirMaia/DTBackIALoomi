# PLANEJAMENTO: Assistente Inteligente de Tintas - MVP

## 📝 O que vai ser feito:

Construir um backend completo em Python/FastAPI para um **Assistente Inteligente de Tintas** que:
- Gerencia um catálogo de tintas (CRUD)
- Responde perguntas em linguagem natural via chatbot
- Usa RAG (Retrieval-Augmented Generation) para buscar tintas relevantes
- Integra com LLM externo (OpenAI GPT) para gerar respostas inteligentes

## 🎯 Por que isso é necessário:

POC para demonstrar capacidade técnica em processo seletivo, evidenciando:
- Arquitetura limpa e organizada
- Integração com IA generativa
- Conhecimento de RAG e embeddings
- Boas práticas de desenvolvimento

## 📂 Arquivos que serão criados:

### Estrutura Principal
- [ ] `backend/app/main.py` - Ponto de entrada da aplicação FastAPI
- [ ] `backend/app/core/config.py` - Configurações e variáveis de ambiente
- [ ] `backend/app/db/session.py` - Conexão com PostgreSQL via SQLAlchemy

### Models
- [ ] `backend/app/models/paint.py` - Modelo SQLAlchemy para tintas
- [ ] `backend/app/models/__init__.py` - Exports dos models

### Repositories
- [ ] `backend/app/repositories/paint_repository.py` - Acesso a dados de tintas

### Services
- [ ] `backend/app/services/agent_service.py` - Orquestrador do agente de IA
- [ ] `backend/app/services/rag_service.py` - Serviço de RAG com embeddings
- [ ] `backend/app/services/llm_service.py` - Integração com LLM (OpenAI)

### Routes (API)
- [ ] `backend/app/api/routes/paints.py` - Endpoints CRUD de tintas
- [ ] `backend/app/api/routes/chat.py` - Endpoint do chatbot
- [ ] `backend/app/api/routes/__init__.py` - Router principal

### Schemas (Pydantic)
- [ ] `backend/app/schemas/paint.py` - Schemas de validação para tintas
- [ ] `backend/app/schemas/chat.py` - Schemas para chat

### Dados e Infra
- [ ] `backend/data/paints.csv` - Base de dados inicial de tintas
- [ ] `backend/Dockerfile` - Container da aplicação
- [ ] `backend/docker-compose.yml` - Orquestração dos serviços
- [ ] `backend/requirements.txt` - Dependências Python
- [ ] `backend/.env.example` - Exemplo de variáveis de ambiente

### Documentação
- [ ] `backend/README.md` - Documentação principal do projeto

## 📦 Dependências necessárias:

### Core
- [ ] `fastapi` - Framework web assíncrono
- [ ] `uvicorn` - Servidor ASGI
- [ ] `pydantic` - Validação de dados
- [ ] `pydantic-settings` - Gerenciamento de configurações

### Banco de Dados
- [ ] `sqlalchemy` - ORM
- [ ] `psycopg2-binary` - Driver PostgreSQL
- [ ] `alembic` - Migrations (opcional para MVP)

### IA e Embeddings
- [ ] `openai` - SDK da OpenAI para GPT
- [ ] `sentence-transformers` - Geração de embeddings locais
- [ ] `numpy` - Operações vetoriais para similaridade

### Utilitários
- [ ] `python-dotenv` - Carregar .env
- [ ] `pandas` - Manipulação do CSV inicial

## ⚠️ RISCOS IDENTIFICADOS:

| Risco | Descrição | Mitigação |
|-------|-----------|-----------|
| API Key exposta | Chave da OpenAI pode vazar | Usar .env + .gitignore |
| Embeddings pesados | sentence-transformers pode ser lento | Usar modelo leve (all-MiniLM-L6-v2) |
| PostgreSQL não sobe | Problemas de conexão no Docker | Health checks + retry |
| Rate limit LLM | Muitas requisições à API | Implementar tratamento de erro |

## 🔗 O que depende deste código:

Este é um projeto greenfield (do zero), então não há dependências existentes.
A ordem de implementação deve respeitar:
1. Config → DB → Models → Repositories → Services → Routes → Main

## 📋 PASSOS DE IMPLEMENTAÇÃO:

### Fase 1: Preparação e Estrutura Base
1. [ ] Criar estrutura de diretórios
2. [ ] Criar `requirements.txt` com todas dependências
3. [ ] Criar `backend/app/core/config.py` com Settings
4. [ ] Criar `.env.example`
5. [ ] Validar que estrutura está correta

**⏸️ CHECKPOINT 1 - Validar estrutura**

### Fase 2: Banco de Dados e Models
6. [ ] Criar `backend/app/db/session.py` com engine SQLAlchemy
7. [ ] Criar `backend/app/models/paint.py` com modelo Paint
8. [ ] Criar `backend/data/paints.csv` com dados de exemplo (10-15 tintas)
9. [ ] Criar `backend/app/repositories/paint_repository.py`

**⏸️ CHECKPOINT 2 - Validar conexão DB e models**

### Fase 3: CRUD de Tintas
10. [ ] Criar `backend/app/schemas/paint.py` com schemas Pydantic
11. [ ] Criar `backend/app/api/routes/paints.py` com endpoints CRUD
12. [ ] Testar CRUD via Swagger

**⏸️ CHECKPOINT 3 - Validar CRUD funcionando**

### Fase 4: Serviço de RAG
13. [ ] Criar `backend/app/services/rag_service.py`
14. [ ] Implementar geração de embeddings
15. [ ] Implementar busca semântica por similaridade

**⏸️ CHECKPOINT 4 - Validar RAG retornando tintas relevantes**

### Fase 5: Integração com LLM
16. [ ] Criar `backend/app/services/llm_service.py`
17. [ ] Criar `backend/app/services/agent_service.py` (orquestrador)
18. [ ] Criar `backend/app/schemas/chat.py`
19. [ ] Criar `backend/app/api/routes/chat.py`

**⏸️ CHECKPOINT 5 - Validar chat funcionando**

### Fase 6: Docker e Finalização
20. [ ] Criar `backend/Dockerfile`
21. [ ] Criar `backend/docker-compose.yml`
22. [ ] Criar script de seed para popular banco inicial
23. [ ] Testar execução completa via Docker
24. [ ] Documentar no README.md

**⏸️ CHECKPOINT 6 - Validar execução Docker**

## ✅ Como validar que funcionou:

### Testes Manuais
1. **CRUD Tintas**: Acessar `http://localhost:8000/docs` e testar todos endpoints
2. **Chat**: POST em `/chat` com pergunta "Qual tinta usar para pintar quarto?"
3. **Docker**: `docker-compose up` deve subir tudo sem erros

### Comportamento Esperado
- Swagger mostra todos endpoints documentados
- CRUD de tintas funciona completamente
- Chat retorna recomendações baseadas na base de dados
- Respostas são contextualizadas e naturais

### Como reverter se der errado
- Código em Git com commits incrementais
- Docker permite rebuild limpo
- Sem dependências externas além do banco

## 🏗️ Arquitetura Proposta

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI (main.py)                     │
├─────────────────────────────────────────────────────────┤
│                      API Routes                          │
│  ┌──────────────┐          ┌──────────────────┐        │
│  │ /api/paints  │          │   /api/chat      │        │
│  │   (CRUD)     │          │  (Assistente)    │        │
│  └──────┬───────┘          └────────┬─────────┘        │
├─────────┼──────────────────────────┼────────────────────┤
│         │         Services          │                    │
│         │    ┌─────────────────────┴───┐               │
│         │    │    agent_service.py     │               │
│         │    │    (Orquestrador)       │               │
│         │    └──────────┬─────────────┘               │
│         │               │                              │
│         │    ┌──────────┴─────────────┐               │
│         │    │                         │               │
│    ┌────┴────┴───┐            ┌───────┴──────┐       │
│    │ rag_service │            │ llm_service  │       │
│    │ (Embeddings)│            │  (OpenAI)    │       │
│    └──────┬──────┘            └──────────────┘       │
├───────────┼─────────────────────────────────────────────┤
│           │         Repository                          │
│    ┌──────┴──────────┐                                 │
│    │ paint_repository │                                │
│    └────────┬─────────┘                                │
├─────────────┼───────────────────────────────────────────┤
│             │         Database                          │
│      ┌──────┴──────┐                                   │
│      │ PostgreSQL  │                                   │
│      │  (paints)   │                                   │
│      └─────────────┘                                   │
└─────────────────────────────────────────────────────────┘
```

## 📊 Modelo de Dados: Paint (Tinta)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | Integer | PK, auto-increment |
| name | String | Nome da tinta |
| brand | String | Marca (Suvinil, Coral, etc) |
| color | String | Cor principal |
| finish | String | Acabamento (fosco, acetinado, brilhante) |
| surface | String | Superfície recomendada (parede, madeira, metal) |
| environment | String | Ambiente (interno, externo, ambos) |
| price | Float | Preço por litro |
| coverage | Float | Rendimento m²/litro |
| description | Text | Descrição detalhada |
| embedding | JSON | Vetor de embedding (para RAG) |

## 🤔 AGUARDANDO APROVAÇÃO

- [ ] Li e entendi o plano
- [ ] Concordo com a abordagem
- [ ] Pode prosseguir

**Status**: ⏸️ AGUARDANDO APROVAÇÃO DO DESENVOLVEDOR

---

## 📌 Decisões Técnicas Importantes

### Por que OpenAI GPT?
- API amplamente documentada e estável
- Grande comunidade e exemplos disponíveis
- Facilidade de uso e integração
- Claude Code auxiliará no desenvolvimento (separação de responsabilidades)

### Por que sentence-transformers ao invés de API de embeddings?
- Funciona offline (sem custos extras)
- Modelo `all-MiniLM-L6-v2` é leve e eficiente
- Suficiente para POC com ~15 tintas

### Por que PostgreSQL?
- Especificado no escopo do desafio
- Robusto e amplamente usado
- Suporta JSON nativo para embeddings

### Por que não usar pgvector?
- Overengineering para POC com poucos registros
- Busca por similaridade em memória é suficiente
- Simplifica setup do Docker

---

**Criado em**: 2025-01-09
**Autor**: Claude Code
**Versão**: 1.0
