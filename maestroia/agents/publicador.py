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

def agente_publicador(state: MaestroState) -> MaestroState:
    """
    Agente responsável por publicar conteúdos em plataformas simuladas.
    """
    conteudos = state.get("conteudos", [])
    if not conteudos:
        return {"erros": ["Conteúdos não encontrados no estado."]}

    # Simulação de publicação (integrar APIs reais futuramente)
    publicacoes = []
    for conteudo in conteudos:
        prompt = f"Formate e simule publicação para: {conteudo}"
        resposta = llm.invoke(prompt)
        publicacoes.append(resposta.content)

    return {"publicacoes": publicacoes}
