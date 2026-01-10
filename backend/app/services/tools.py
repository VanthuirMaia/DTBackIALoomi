"""
Ferramentas (Tools) para o agente LangChain.

Cada ferramenta é uma função que o agente pode usar para realizar tarefas específicas.
"""

from typing import Optional
from langchain.tools import tool

from app.db.session import SessionLocal
from app.models.paint import Paint
from app.services.rag_service import get_rag_service


@tool
def buscar_tinta_semantica(query: str) -> str:
    """
    Busca tintas usando busca semântica (RAG).
    Use esta ferramenta quando o usuário fizer perguntas em linguagem natural
    sobre recomendações de tintas, como "qual tinta usar para quarto de bebê"
    ou "tinta resistente para área externa".

    Args:
        query: A pergunta ou descrição do usuário sobre o que precisa.

    Returns:
        Lista de tintas mais relevantes para a necessidade.
    """
    rag = get_rag_service()
    results = rag.search(query, top_k=5)

    if not results:
        return "Nenhuma tinta encontrada para essa busca."

    output = "Tintas encontradas:\n\n"
    for i, r in enumerate(results, 1):
        output += f"{i}. **{r['nome']}**\n"
        output += f"   - Cor: {r['cor']}\n"
        output += f"   - Superfície: {r['tipo_superficie']}\n"
        output += f"   - Ambiente: {r['ambiente']}\n"
        output += f"   - Acabamento: {r['acabamento']}\n"
        output += f"   - Características: {r['features']}\n"
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
    Busca tintas por filtros específicos no banco de dados.
    Use esta ferramenta quando o usuário pedir tintas com características específicas,
    como "tintas na cor branca" ou "tintas para ambiente externo".

    Args:
        cor: Cor da tinta (ex: Branco, Azul, Cinza)
        ambiente: Interno ou Externo
        acabamento: Fosco, Acetinado, Brilhante, Semi-brilho
        tipo_superficie: Parede, Madeira, Metal, Piso, Gesso
        linha: Premium, Standard, Econômica

    Returns:
        Lista de tintas que correspondem aos filtros.
    """
    session = SessionLocal()
    try:
        query = session.query(Paint)

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

        results = query.limit(10).all()

        if not results:
            return "Nenhuma tinta encontrada com esses filtros."

        output = f"Encontradas {len(results)} tintas:\n\n"
        for i, p in enumerate(results, 1):
            output += f"{i}. **{p.nome}**\n"
            output += f"   - Cor: {p.cor} | Ambiente: {p.ambiente}\n"
            output += f"   - Acabamento: {p.acabamento} | Linha: {p.linha}\n"
            output += f"   - Características: {p.features}\n\n"

        return output
    finally:
        session.close()


@tool
def calcular_quantidade_tinta(area_m2: float, rendimento: float = 10.0) -> str:
    """
    Calcula a quantidade de tinta necessária para pintar uma área.
    Use esta ferramenta quando o usuário perguntar quantas latas ou litros
    de tinta precisa para pintar um ambiente.

    Args:
        area_m2: Área total em metros quadrados a ser pintada.
        rendimento: Rendimento da tinta em m²/litro (padrão: 10 m²/L para 2 demãos).

    Returns:
        Cálculo detalhado da quantidade de tinta necessária.
    """
    # Considerando 2 demãos
    litros_necessarios = (area_m2 / rendimento) * 2

    # Tamanhos comuns de latas
    latas_3_6l = litros_necessarios / 3.6
    latas_18l = litros_necessarios / 18

    return f"""**Cálculo de Tinta para {area_m2} m²:**

- Litros necessários (2 demãos): **{litros_necessarios:.1f} litros**
- Latas de 3,6L: **{latas_3_6l:.1f}** (arredonde para cima)
- Latas de 18L: **{latas_18l:.2f}** (arredonde para cima)

💡 **Dica:** Sempre compre um pouco a mais (10-15%) para retoques e imprevistos.

📏 Rendimento considerado: {rendimento} m²/litro por demão."""


@tool
def listar_cores_disponiveis() -> str:
    """
    Lista todas as cores de tintas disponíveis no catálogo.
    Use esta ferramenta quando o usuário perguntar quais cores estão disponíveis.

    Returns:
        Lista de cores únicas disponíveis.
    """
    session = SessionLocal()
    try:
        cores = session.query(Paint.cor).distinct().all()
        cores_lista = sorted(set(c[0] for c in cores))

        return f"**Cores disponíveis no catálogo ({len(cores_lista)}):**\n\n" + ", ".join(cores_lista)
    finally:
        session.close()


@tool
def listar_linhas_produtos() -> str:
    """
    Lista as linhas de produtos disponíveis (Premium, Standard, Econômica).
    Use esta ferramenta quando o usuário perguntar sobre linhas de produto
    ou diferenças entre elas.

    Returns:
        Informações sobre as linhas de produtos.
    """
    return """**Linhas de Produtos Suvinil:**

🏆 **Premium**
- Maior qualidade e durabilidade
- Melhor cobertura e rendimento
- Tecnologias avançadas (sem odor, anti-mofo)
- Indicada para ambientes de destaque

⭐ **Standard**
- Boa qualidade com custo-benefício
- Durabilidade satisfatória
- Opções variadas de cores e acabamentos
- Indicada para uso geral

💰 **Econômica**
- Preço acessível
- Cobertura básica
- Ideal para áreas de serviço ou renovação rápida
- Indicada para orçamentos limitados"""


# Lista de todas as ferramentas disponíveis
def get_tools():
    """Retorna lista de todas as ferramentas disponíveis para o agente."""
    return [
        buscar_tinta_semantica,
        buscar_por_filtros,
        calcular_quantidade_tinta,
        listar_cores_disponiveis,
        listar_linhas_produtos,
    ]
