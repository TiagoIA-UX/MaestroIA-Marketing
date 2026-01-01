from maestroia.core.state import MaestroState
from maestroia.services.openai_service import chat as openai_chat

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
    resposta_text = openai_chat(prompt)

    return {"metricas": metricas, "otimizacao": resposta_text}
