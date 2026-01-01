import unittest
from unittest.mock import patch, MagicMock


class TestRealIntegrationMocks(unittest.TestCase):
    def test_openai_service_mocked(self):
        # Mock the openai module inside openai_service
        import maestroia.services.openai_service as openai_service

        dummy_resp = MagicMock()
        dummy_choice = MagicMock()
        dummy_choice.message.content = "Resposta mockada da OpenAI"
        dummy_resp.choices = [dummy_choice]

        class DummyOpenAI:
            class ChatCompletion:
                @staticmethod
                def create(model, messages, temperature):
                    return dummy_resp

        with patch.object(openai_service, 'openai', DummyOpenAI):
            out = openai_service.chat("Olá")
            self.assertIn("Resposta mockada da OpenAI", out)

    def test_mercadopago_service_mocked(self):
        import maestroia.services.mercadopago_service as mp_service

        class DummySDK:
            def __init__(self, token):
                self._token = token

            def preference(self):
                class P:
                    @staticmethod
                    def create(data):
                        return {"status": "created", "init_point": "https://mp.test/checkout"}
                return P()

        dummy_module = MagicMock()
        dummy_module.SDK = DummySDK

        # Garantir token temporário para evitar caminho de fallback
        orig_token = getattr(mp_service.settings, 'MERCADOPAGO_ACCESS_TOKEN', None)
        try:
            mp_service.settings.MERCADOPAGO_ACCESS_TOKEN = "test-token"
            with patch.object(mp_service, 'mercadopago', dummy_module):
                res = mp_service.create_preference("Produto Mock", 12.5)
                self.assertIsInstance(res, dict)
                # mocked SDK retorna status 'created'
                self.assertEqual(res.get('status'), 'created')
        finally:
            mp_service.settings.MERCADOPAGO_ACCESS_TOKEN = orig_token


if __name__ == '__main__':
    unittest.main()
