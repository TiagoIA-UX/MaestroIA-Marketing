import os
import unittest


class TestIntegrationsFallbacks(unittest.TestCase):
    def setUp(self):
        # Garantir que settings não quebre por ausência de chave real
        os.environ.setdefault("OPENAI_API_KEY", "sk-test-placeholder")

    def test_openai_service_fallback(self):
        from maestroia.services import openai_service

        resp = openai_service.chat("Teste de fallback")
        self.assertIsInstance(resp, str)
        self.assertTrue("FALLBACK" in resp or resp.startswith("[FALLBACK OPENAI]"))

    def test_trends_service_fallback(self):
        from maestroia.services.trends_service import get_trends_summary

        summary = get_trends_summary(["produto X", "mulheres 25-40"])
        self.assertIsInstance(summary, str)
        self.assertTrue("Dados" in summary)

    def test_mercadopago_service_fallback(self):
        from maestroia.services.mercadopago_service import create_preference

        result = create_preference("Teste", 10.0)
        self.assertIsInstance(result, dict)
        # Aceitar várias formas de retorno: status, message, init_point ou campos da API
        self.assertTrue(
            any(k in result for k in ("status", "message", "init_point", "preference"))
        )


if __name__ == "__main__":
    unittest.main()
