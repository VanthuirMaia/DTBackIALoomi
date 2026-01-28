# Relatorio de Progresso - Desafio Back IA Loomi

**Candidato:** Vanthuir Maia
**Data de Entrega:** 12/01/2026
**Projeto:** Assistente Inteligente de Tintas Suvinil

---

## 1. Plataforma de Gestao de Atividades

**Link do Backlog:** [Trello - Desafio Back IA Loomi POC](https://trello.com/invite/b/67ec9b8048d2d6208c05a023/ATTIe1e8b36859acae616ea80ec568a848667D930EE1/desafio-back-ia-loomi-poc)

---

## 2. Organizacao das Demandas e Atividades

### Metodologia Adotada

Organizei o desenvolvimento em **feature branches**, onde cada funcionalidade foi desenvolvida isoladamente e depois integrada via merge. O arquivo `CLAUDE.md` serviu como diario tecnico, documentando cada sessao de trabalho.

### Estrutura de Branches

| Branch | Funcionalidade |
|--------|----------------|
| `feature/setup-fastapi` | Setup inicial do projeto |
| `feature/paint-crud` | CRUD de tintas |
| `feature/csv-import` | Importacao de dados CSV |
| `feature/rag-service` | Busca semantica com embeddings |
| `feature/llm-service` | Integracao com GPT |
| `feature/langchain-agent` | Agente com 6 ferramentas |
| `feature/docker` | Containerizacao |
| `feature/readme` | Documentacao |
| `feature/guardrails` | Sistema de seguranca |
| `feature/auth-jwt` | Autenticacao JWT + RBAC |
| `feature/dalle-integration` | Geracao de imagens |
| `feature/frontend` | Interface web |

### Cronograma de Execucao

| Data | Sessoes | Entregas |
|------|---------|----------|
| 10/01/2026 | 1-11 | Setup, CRUD, RAG, LLM, Agente, Docker, Guardrails, Auth, DALL-E, Frontend |
| 11/01/2026 | 12 | Revisao final, limpeza de codigo, PR e merge |

---

## 3. Priorizacao das Entregas

### Criterio de Priorizacao

Utilizei a abordagem **MVP First** (Minimum Viable Product), priorizando:

1. **Essencial primeiro:** Funcionalidades obrigatorias do desafio
2. **Diferenciais depois:** Features opcionais que agregam valor
3. **Qualidade sempre:** Cada feature foi testada antes de seguir

### Ordem de Implementacao

| Prioridade | Feature | Justificativa |
|------------|---------|---------------|
| 1 | Setup + CRUD | Base do projeto |
| 2 | RAG + Embeddings | Core da busca semantica |
| 3 | LLM + Agente LangChain | Core do assistente IA |
| 4 | Docker | Facilitar execucao e avaliacao |
| 5 | Autenticacao JWT | Requisito de seguranca |
| 6 | Guardrails | Seguranca do agente (diferencial) |
| 7 | DALL-E | Feature opcional valorizada |
| 8 | Frontend | Plus para demonstracao |

---

## 4. Principais Dificuldades e Solucoes

### 4.1 Incompatibilidade localhost vs 127.0.0.1 (Windows)

**Problema:** Requisicoes para `localhost:8000` falhavam no Windows, mas funcionavam com `127.0.0.1:8000`.

**Solucao:** Padronizei todas as URLs para usar `127.0.0.1` no frontend e scripts de teste.

---

### 4.2 Incompatibilidade passlib/bcrypt

**Problema:** Erro ao usar passlib com versoes recentes do bcrypt para hashing de senhas.

**Solucao:** Fixei a versao `bcrypt==4.0.1` no requirements.txt para garantir compatibilidade.

---

### 4.3 Compatibilidade DALL-E 2 vs DALL-E 3

**Problema:** Parametros `quality` e `revised_prompt` nao existem no DALL-E 2, causando erros.

**Solucao:** Implementei verificacao condicional do modelo antes de enviar parametros, tornando o codigo compativel com ambas versoes.

---

### 4.4 Variavel de Ambiente Duplicada (Windows)

**Problema:** `OPENAI_API_KEY` estava definida tanto em User quanto em Machine no Windows, causando conflito.

**Solucao:** Criei script de debug para identificar o problema e priorizei o carregamento do `.env` com `override=True`.

---

### 4.5 Carregamento do .env no FastAPI

**Problema:** O uvicorn nao carregava automaticamente as variaveis do `.env`.

**Solucao:** Adicionei `load_dotenv()` no inicio do `main.py` antes de qualquer import que use variaveis de ambiente.

---

### 4.6 Versao do LangChain/LangGraph

**Problema:** Exemplos da documentacao usavam APIs descontinuadas.

**Solucao:** Migrei para `create_react_agent` do langgraph.prebuilt, compativel com versoes atuais.

---

## 5. O que Faria Diferente com Mais Tempo

### 5.1 Testes Automatizados com pytest

Implementaria uma suite de testes automatizados cobrindo:
- Testes unitarios para cada service
- Testes de integracao para endpoints
- Testes de seguranca (tentativas de bypass)
- Cobertura minima de 70%

### 5.2 CI/CD com GitHub Actions

Configuraria pipeline automatizado para:
- Rodar testes a cada push
- Verificar linting (black, flake8, mypy)
- Build e push de imagem Docker
- Deploy automatico em ambiente de staging

### 5.3 Rate Limiting

Implementaria limitacao de requisicoes para:
- Proteger contra ataques de forca bruta no login
- Controlar custos da API OpenAI
- Evitar abusos do servico

### 5.4 Cache com Redis

Adicionaria cache para:
- Sessoes de agente (escalabilidade horizontal)
- Embeddings de produtos (reduzir chamadas a API)
- Respostas frequentes

### 5.5 Observabilidade

Implementaria:
- Logs estruturados com contexto de requisicao
- Metricas de uso (Prometheus/Grafana)
- Tracing distribuido (OpenTelemetry)
- Dashboard de monitoramento

### 5.6 Multi-tenancy

Prepararia a aplicacao para multiplos clientes:
- Isolamento de dados por tenant
- Configuracoes personalizadas por cliente
- Limites de uso por plano

---

## 6. Resumo dos Entregaveis Tecnicos

### Requisitos Obrigatorios

| Requisito | Status | Implementacao |
|-----------|--------|---------------|
| Assistente IA para tintas | OK | Agente LangChain com 6 ferramentas |
| Interpretar intencoes | OK | GPT-4o-mini + Prompt Engineering |
| Buscar/recomendar produtos | OK | RAG com embeddings |
| Agente Orquestrador | OK | LangGraph create_react_agent |
| Contexto estruturado | OK | RAG + Busca semantica |
| Chatbot linguagem natural | OK | Endpoint /chat |
| CRUD tintas/usuarios | OK | FastAPI + SQLAlchemy |
| Autenticacao JWT + RBAC | OK | python-jose + bcrypt |
| PostgreSQL | OK | Docker Compose |
| Swagger/OpenAPI | OK | FastAPI automatico |
| Docker + Docker Compose | OK | Dockerfile + docker-compose.yml |
| Fluxo Git | OK | 13 branches + PR |

### Requisitos Opcionais (Diferenciais)

| Requisito | Status | Implementacao |
|-----------|--------|---------------|
| Geracao visual DALL-E | OK | Ferramenta visualizar_ambiente |
| Frontend | OK | HTML/CSS/JS vanilla |
| Sistema de Guardrails | OK | Prompt injection, off-topic, blocked content |

---

## 7. Ferramentas de IA Utilizadas no Desenvolvimento

### Claude (Anthropic) - via Claude Code CLI

- **Uso:** Assistente principal de desenvolvimento
- **Funcoes:** Planejamento, implementacao, debug, documentacao

### ChatGPT (OpenAI)

- **Uso:** Tech leader e brainstorming
- **Funcoes:** Estrategias de implementacao, revisao de decisoes

### Exemplos de Prompts

**Planejamento:**
```
Analise o documento do desafio tecnico e identifique em que fase
do projeto estamos e qual o proximo passo.
```

**Implementacao:**
```
Criar script import_csv.py que seja idempotente, compativel
com SQLAlchemy 2.x e exiba quantos registros foram inseridos.
```

**Debug:**
```
O teste do agente LangChain esta dando erro de import.
Corrija para a versao atual do langgraph.
```

### Decisoes Baseadas em IA

| Decisao | Sugestao da IA | Resultado |
|---------|----------------|-----------|
| Expansao do CSV | Enriquecer de 25 para 72 produtos | Melhor cobertura de cenarios |
| Uso de LangGraph | Identificou incompatibilidade com API antiga | Migracao bem-sucedida |
| Guardrails | Sugeriu regex patterns para seguranca | Sistema robusto implementado |

---

## 8. Conclusao

O projeto foi entregue dentro do prazo, atendendo a todos os requisitos obrigatorios e implementando diferenciais significativos:

- **6 ferramentas** no agente LangChain
- **Sistema de guardrails** para seguranca
- **Integracao DALL-E** para visualizacao
- **Frontend funcional** para demonstracao
- **13 feature branches** documentando evolucao

A organizacao em branches por feature e a documentacao continua no CLAUDE.md permitiram manter o controle do progresso e facilitar a rastreabilidade das decisoes tecnicas.

---

**Repositorio:** [GitHub - DTBackIALoomi](https://github.com/VanthuirMaia/DTBackIALoomi)

**Desenvolvido por:** Vanthuir Maia
**Janeiro 2026**
