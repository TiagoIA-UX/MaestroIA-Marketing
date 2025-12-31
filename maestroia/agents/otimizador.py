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

def agente_otimizador(state: MaestroState) -> MaestroState:
    """
    Agente responsável por otimizar campanhas com base em métricas simuladas.
    """
    publicacoes = state.get("publicacoes", [])
    if not publicacoes:
        return {"erros": ["Publicações não encontradas no estado."]}

    # Simulação de otimização (integrar analytics reais futuramente)
    metricas = {"cliques": 150, "conversoes": 10, "roi": 2.5}
    prompt = f"Otimize com base em métricas: {metricas} para publicações: {publicacoes}"
    resposta = llm.invoke(prompt)

    return {"metricas": metricas, "otimizacao": resposta.content}
