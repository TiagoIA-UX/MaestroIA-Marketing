import sys
import os
import warnings

# Suprimir aviso de compatibilidade Pydantic v1 com Python 3.14+
warnings.filterwarnings("ignore", message="Core Pydantic V1 functionality isn't compatible with Python 3.14 or greater")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'maestroia'))

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