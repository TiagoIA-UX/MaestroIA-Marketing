import sys
sys.path.append('.')

from maestroia.graphs.marketing_graph import build_marketing_graph

if __name__ == "__main__":
    graph = build_marketing_graph()
    initial_state = {
        "objetivo": "Lançar produto X para público feminino 25-40 anos",
        "publico_alvo": "Mulheres 25-40 anos",
        "canais": ["Instagram", "Google Ads"],
        "orcamento": 10000.0
    }
    result = graph.invoke(initial_state)
    print("Resultado da Campanha:", result)
