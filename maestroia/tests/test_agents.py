import unittest
from maestroia.graphs.marketing_graph import build_marketing_graph

class TestMaestroIA(unittest.TestCase):
    def test_campaign_flow(self):
        graph = build_marketing_graph()
        state = {"objetivo": "Teste", "publico_alvo": "Teste"}
        result = graph.invoke(state)
        self.assertIn("pesquisa", result)

if __name__ == "__main__":
    unittest.main()
