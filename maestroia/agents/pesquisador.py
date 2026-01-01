from maestroia.config.settings import (
    ENVIRONMENT,
    DEFAULT_LLM_MODEL,
    DEFAULT_TEMPERATURE,
)
from maestroia.core.state import MaestroState
from maestroia.services.trends_service import get_trends_summary
from maestroia.services.openai_service import chat as openai_chat

def agente_pesquisador(state: MaestroState) -> MaestroState:
    """
    Agente responsável por analisar o mercado e identificar tendências relevantes.
    """

    objetivo = state.get("objetivo", "Marketing digital")
    publico = state.get("publico_alvo", "Público geral")

    # Buscar tendências via trends_service (pytrends encapsulado)
    keywords = [objetivo, publico]
    trends_summary = get_trends_summary(keywords)

    # Simulação de dados SEMrush (API paga - integrar chave real futuramente)
    semrush_data = f"Dados do SEMrush (dezembro 2024): Palavras-chave relacionadas '{objetivo}' com volume estimado de 8.500-12.000 buscas mensais globais, dificuldade de SEO média-alta (65/100). Palavras-chave relacionadas '{publico}' com volume de 4.200-6.800 buscas mensais, tendência de crescimento de 15% nos últimos 3 meses."

    # Usar LLM para identificar concorrentes reais
    concorrentes_prompt = f"""
    Baseado no objetivo de marketing "{objetivo}" e público-alvo "{publico}",
    identifique 3-5 concorrentes reais no mercado brasileiro ou internacional que atuam nessa área.
    Foque em empresas ou profissionais conhecidos nessa especialidade.
    Liste apenas os nomes das empresas/profissionais, separados por vírgula.
    Para cada concorrente, inclua uma breve justificativa baseada em dados ou reconhecimento de mercado.
    """

    concorrentes = openai_chat(concorrentes_prompt)
    concorrentes = concorrentes.strip()

    semrush_data += f" Concorrentes identificados: {concorrentes}."

    prompt = f"""
    Analise o mercado de marketing digital considerando:

    Objetivo: {objetivo}
    Público-alvo: {publico}

    Dados do Google Trends:
    {trends_summary}

    Dados simulados do SEMrush:
    {semrush_data}

    Gere um resumo claro sobre:
    - Tendências atuais (cite fontes específicas como Google Trends, data e porcentagens quando possível)
    - Oportunidades (baseadas em dados de mercado)
    - Riscos (com referências a estudos ou dados)
    - Concorrentes principais (com fontes de identificação)

    IMPORTANTE: Sempre cite fontes específicas para dados e estatísticas mencionadas.
    Exemplos: "Segundo dados do Google Trends de dezembro 2024, houve aumento de 35% nas buscas por..."
    "De acordo com relatório da [empresa] de 2024..."
    "Dados do SEMrush mostram que..."
    """

    resposta_text = openai_chat(prompt)

    return {
        "pesquisa": resposta_text
    }
