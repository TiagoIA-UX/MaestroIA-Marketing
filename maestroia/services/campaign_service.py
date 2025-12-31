from maestroia.graphs.marketing_graph import build_marketing_graph

def run_campaign(state):
    graph = build_marketing_graph()
    return graph.invoke(state)
