from maestroia.core.state import MaestroState
from maestroia.services.openai_service import chat as openai_chat


def agente_estrategista(state: MaestroState) -> MaestroState:
    """
    Agente responsável por transformar a pesquisa de mercado
    em uma estratégia de marketing prática e estruturada.
    """

    pesquisa = state.get("pesquisa")
    objetivo = state.get("objetivo", "Crescimento de marca")
    publico = state.get("publico_alvo", "Público geral")
    canais = state.get("canais", ["Instagram", "Google"])

    if not pesquisa:
        return {
            "erros": ["Pesquisa de mercado não encontrada no estado."]
        }

    prompt = f"""
    Você é um estrategista de marketing digital sênior.

    Objetivo: {objetivo}
    Público-alvo: {publico}
    Canais: {", ".join(canais)}

    Pesquisa de mercado:
    {pesquisa}

    Com base nisso, crie uma estratégia contendo:
    - Posicionamento
    - Mensagem central
    - Estratégia por canal
    - Indicadores de sucesso (KPIs)

    Seja claro, direto e profissional.
    """

    resposta_text = openai_chat(prompt)

    return {
        "estrategia": resposta_text
    }
