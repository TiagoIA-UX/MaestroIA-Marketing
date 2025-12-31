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


def agente_criador_conteudo(state: MaestroState) -> MaestroState:
    """
    Agente responsável por criar conteúdos de marketing
    com base na estratégia definida.
    """

    estrategia = state.get("estrategia")
    canais = state.get("canais", ["Instagram", "Google"])

    if not estrategia:
        return {
            "erros": ["Estratégia não encontrada no estado."]
        }

    prompt = f"""
    Você é um especialista em criação de conteúdo para marketing digital.

    Estratégia:
    {estrategia}

    Crie conteúdos adequados para os seguintes canais:
    {", ".join(canais)}

    Para cada canal, gere:
    - Uma ideia principal
    - Um texto base de publicação

    Retorne o conteúdo de forma organizada.
    """

    resposta = llm.invoke(prompt)

    return {
        "conteudos": [resposta.content]
    }
