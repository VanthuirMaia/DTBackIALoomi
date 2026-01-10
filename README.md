# Assistente Inteligente de Tintas Suvinil

API backend para um assistente virtual especializado em tintas, desenvolvido como parte do desafio tecnico da Loomi. O sistema utiliza tecnicas de Inteligencia Artificial para recomendar produtos de forma contextualizada, combinando busca semantica (RAG) com geracao de linguagem natural (LLM).

## Sumario

- [Arquitetura](#arquitetura)
- [Tecnologias](#tecnologias)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Configuracao e Instalacao](#configuracao-e-instalacao)
- [Execucao](#execucao)
- [Endpoints da API](#endpoints-da-api)
- [Exemplos de Uso](#exemplos-de-uso)
- [Decisoes Tecnicas](#decisoes-tecnicas)
- [Ferramentas de IA Utilizadas no Desenvolvimento](#ferramentas-de-ia-utilizadas-no-desenvolvimento)

## Arquitetura

O sistema segue uma arquitetura em camadas com um agente de IA orquestrador:

```
                        +------------------+
                        |   Cliente/API    |
                        +--------+---------+
                                 |
                        +--------v---------+
                        |     FastAPI      |
                        |   (Endpoints)    |
                        +--------+---------+
                                 |
                        +--------v---------+
                        |  Agent Service   |
                        |   (LangGraph)    |
                        +--------+---------+
                                 |
              +------------------+------------------+
              |                  |                  |
     +--------v-------+  +-------v--------+  +-----v------+
     |  RAG Service   |  |  LLM Service   |  |   Tools    |
     |  (Embeddings)  |  |    (GPT)       |  | (5 tools)  |
     +--------+-------+  +----------------+  +-----+------+
              |                                    |
     +--------v-------+                    +-------v--------+
     |   PostgreSQL   |<-------------------+   Repository   |
     |   (72 tintas)  |                    +----------------+
     +----------------+
```

### Fluxo de Processamento

1. Usuario envia pergunta via endpoint `/chat`
2. Agent Service (LangGraph) analisa a intencao
3. Agente seleciona ferramenta apropriada:
   - Busca semantica para recomendacoes
   - Filtros para consultas especificas
   - Calculo para quantidades
4. Ferramenta executa e retorna dados
5. LLM gera resposta contextualizada
6. Resposta retorna ao usuario

## Tecnologias

| Categoria | Tecnologia | Versao |
|-----------|------------|--------|
| Framework Web | FastAPI | 0.115.6 |
| Banco de Dados | PostgreSQL | 15 |
| ORM | SQLAlchemy | 2.0.36 |
| LLM | OpenAI GPT-4o-mini | - |
| Embeddings | OpenAI text-embedding-3-small | - |
| Agente IA | LangChain + LangGraph | 0.3.14 / 0.2.62 |
| Containerizacao | Docker + Docker Compose | - |
| Linguagem | Python | 3.11 |

## Estrutura do Projeto

```
BackIALoomi/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
│
└── backend/
    ├── app/
    │   ├── main.py                 # Ponto de entrada FastAPI
    │   ├── api/
    │   │   └── routes/
    │   │       ├── paints.py       # CRUD de tintas
    │   │       └── chat.py         # Endpoint do chatbot
    │   ├── db/
    │   │   ├── base.py             # Base declarativa SQLAlchemy
    │   │   └── session.py          # Configuracao de sessao
    │   ├── models/
    │   │   └── paint.py            # Modelo ORM de tintas
    │   ├── repositories/
    │   │   └── paint_repository.py # Acesso a dados
    │   ├── schemas/
    │   │   └── chat.py             # Schemas Pydantic
    │   └── services/
    │       ├── agent_service.py    # Orquestrador LangGraph
    │       ├── llm_service.py      # Integracao OpenAI GPT
    │       ├── rag_service.py      # Busca semantica
    │       └── tools.py            # Ferramentas do agente
    │
    ├── scripts/
    │   ├── import_csv.py           # Importacao de dados
    │   ├── test_rag.py             # Teste do RAG
    │   ├── test_chat.py            # Teste do chat
    │   └── test_langchain_agent.py # Teste do agente
    │
    └── data/
        └── Base_de_Dados_de_Tintas_Suvinil.csv
```

## Configuracao e Instalacao

### Pre-requisitos

- Python 3.11+
- PostgreSQL 15+
- Docker e Docker Compose (opcional)
- Chave de API da OpenAI

### Instalacao Local

1. Clone o repositorio:
```bash
git clone https://github.com/VanthuirMaia/DTBackIALoomi.git
cd DTBackIALoomi
```

2. Crie e ative o ambiente virtual:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

3. Instale as dependencias:
```bash
pip install -r requirements.txt
```

4. Configure as variaveis de ambiente:
```bash
cp backend/.env.example backend/.env
```

Edite o arquivo `backend/.env`:
```
DATABASE_URL=postgresql://usuario:senha@localhost:5432/back_ia_loomi
OPENAI_API_KEY=sua-chave-openai
```

5. Crie o banco de dados e a tabela:
```sql
CREATE DATABASE back_ia_loomi;
```

6. Importe os dados iniciais:
```bash
cd backend
python scripts/import_csv.py
```

### Instalacao com Docker

1. Clone o repositorio e configure o `.env` na raiz:
```bash
git clone https://github.com/VanthuirMaia/DTBackIALoomi.git
cd DTBackIALoomi
echo "OPENAI_API_KEY=sua-chave-openai" > .env
```

2. Execute com Docker Compose:
```bash
docker-compose up --build
```

## Execucao

### Local

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker

```bash
docker-compose up
```

### Acesso

- API: http://localhost:8000
- Documentacao Swagger: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## Endpoints da API

### Health Check

```
GET /health
```

Verifica se a API esta funcionando.

### Tintas (CRUD)

| Metodo | Endpoint | Descricao |
|--------|----------|-----------|
| GET | `/paints` | Lista todas as tintas |
| GET | `/paints/{id}` | Busca tinta por ID |
| POST | `/paints` | Cria nova tinta |
| PUT | `/paints/{id}` | Atualiza tinta |
| DELETE | `/paints/{id}` | Remove tinta |

### Chat (Assistente IA)

```
POST /chat
```

Envia mensagem para o assistente e recebe recomendacao.

**Request Body:**
```json
{
  "message": "Quero pintar meu quarto, algo facil de limpar e sem cheiro forte",
  "session_id": "opcional-para-manter-historico"
}
```

**Response:**
```json
{
  "response": "Para o seu quarto, recomendo a Suvinil Toque de Seda...",
  "products": [],
  "query": "Quero pintar meu quarto...",
  "session_id": "uuid-da-sessao"
}
```

```
POST /chat/clear
```

Limpa o historico de uma sessao.

## Exemplos de Uso

### Recomendacao por Necessidade

**Pergunta:** "Preciso pintar a fachada da minha casa. Bate muito sol e chove bastante."

**Resposta:** O agente utiliza a ferramenta `buscar_tinta_semantica` para encontrar tintas para ambiente externo com protecao UV e resistencia a umidade, retornando produtos como Suvinil Fachada Acrilica.

### Consulta por Filtros

**Pergunta:** "Quais tintas na cor branca voces tem?"

**Resposta:** O agente utiliza a ferramenta `buscar_por_filtros` com o parametro cor="Branco", retornando todas as tintas brancas do catalogo.

### Calculo de Quantidade

**Pergunta:** "Preciso pintar uma parede de 20 metros quadrados. Quantas latas vou precisar?"

**Resposta:** O agente utiliza a ferramenta `calcular_quantidade_tinta` e retorna o calculo detalhado de litros e latas necessarias.

### Informacoes sobre Produtos

**Pergunta:** "Qual a diferenca entre as linhas Premium e Economica?"

**Resposta:** O agente utiliza a ferramenta `listar_linhas_produtos` e explica as caracteristicas de cada linha.

## Decisoes Tecnicas

### Escolha do LangGraph

Optou-se pelo LangGraph (evolucao do LangChain) para implementar o agente por:
- Suporte nativo a ferramentas (tools)
- Gerenciamento de estado da conversacao
- Arquitetura baseada em grafos para fluxos complexos
- Melhor observabilidade do raciocinio do agente

### Embeddings em Memoria

Para esta POC, os embeddings sao mantidos em memoria ao inves de usar pgvector por:
- Simplicidade de implementacao
- Base de dados pequena (72 produtos)
- Evita dependencias adicionais no PostgreSQL

### Modelo GPT-4o-mini

Escolhido pelo equilibrio entre custo e qualidade:
- Custo significativamente menor que GPT-4
- Qualidade suficiente para recomendacoes de produtos
- Baixa latencia nas respostas

### Nao Utilizacao do Alembic

Para simplificar a POC, as tabelas sao criadas manualmente. Em producao, recomenda-se adicionar Alembic para controle de migrations.

## Ferramentas de IA Utilizadas no Desenvolvimento

### Claude (Anthropic)

Utilizado como assistente principal de desenvolvimento atraves do Claude Code CLI:
- Planejamento de arquitetura
- Implementacao de codigo
- Revisao e correcao de erros
- Geracao de documentacao

### ChatGPT (OpenAI)

Utilizado como tech leader para:
- Definicao de estrategias de implementacao
- Revisao de decisoes tecnicas
- Brainstorming de solucoes

### Exemplos de Prompts Utilizados

**Planejamento:**
```
"Analise o documento do desafio tecnico e identifique em que fase
do projeto estamos e qual o proximo passo."
```

**Implementacao:**
```
"Criar script import_csv.py que seja idempotente, compativel
com SQLAlchemy 2.x e exiba quantos registros foram inseridos."
```

**Correcao:**
```
"O teste do agente LangChain esta dando erro de import.
Corrija para a versao atual do langgraph."
```

### Decisoes Baseadas em Sugestoes de IA

| Decisao | Sugestao | Resultado |
|---------|----------|-----------|
| Expansao do CSV | Claude sugeriu enriquecer base de 25 para 72 produtos | Melhor cobertura dos cenarios do desafio |
| Uso de LangGraph | Claude identificou incompatibilidade com versao antiga | Migracao para create_react_agent |
| Carregamento do .env | Claude identificou que uvicorn nao carregava variaveis | Adicionado load_dotenv no main.py |

## Autor

Desenvolvido por Vanthuir Maia como parte do processo seletivo Loomi - Janeiro 2026.

## Licenca

Este projeto foi desenvolvido exclusivamente para fins de avaliacao tecnica.
