from langchain_openai import ChatOpenAI
from maestroia.config.settings import (
    OPENAI_API_KEY,
    DEFAULT_LLM_MODEL,
    DEFAULT_TEMPERATURE,
)
from maestroia.core.state import MaestroState


llm = ChatOpenAI(
    api_key=OPENAI_API_KEY,
    model=DEFAULT_LLM_MODEL,
    temperature=DEFAULT_TEMPERATURE,
)


def agente_pesquisador(state: MaestroState) -> MaestroState:
    """
    Agente responsável por analisar o mercado e identificar tendências relevantes.
    """

    objetivo = state.get("objetivo", "Marketing digital")
    publico = state.get("publico_alvo", "Público geral")

    prompt = f"""
    Analise o mercado de marketing digital considerando:

    Objetivo: {objetivo}
    Público-alvo: {publico}

    Gere um resumo claro sobre:
    - Tendências atuais
    - Oportunidades
    - Riscos
    """

    resposta = llm.invoke(prompt)

    return {
        "pesquisa": resposta.content
    }
