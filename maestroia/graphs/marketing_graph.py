from langgraph.graph import StateGraph, END
from maestroia.core.state import MaestroState
from maestroia.agents.pesquisador import agente_pesquisador
from maestroia.agents.estrategista import agente_estrategista
from maestroia.agents.criador_conteudo import agente_criador_conteudo
from maestroia.agents.publicador import agente_publicador
from maestroia.agents.otimizador import agente_otimizador
from maestroia.agents.maestro import agente_maestro

def build_marketing_graph():
    graph = StateGraph(MaestroState)

    graph.add_node("pesquisador", agente_pesquisador)
    graph.add_node("estrategista", agente_estrategista)
    graph.add_node("criador_conteudo", agente_criador_conteudo)
    graph.add_node("publicador", agente_publicador)
    graph.add_node("otimizador", agente_otimizador)
    graph.add_node("maestro", agente_maestro)

    graph.set_entry_point("pesquisador")
    graph.add_edge("pesquisador", "estrategista")
    graph.add_edge("estrategista", "criador_conteudo")
    graph.add_edge("criador_conteudo", "publicador")
    graph.add_edge("publicador", "otimizador")
    graph.add_edge("otimizador", "maestro")
    graph.add_edge("maestro", END)

    return graph.compile()
