import unittest
from unittest.mock import patch, MagicMock


class TestMetaOAuth(unittest.TestCase):
    def test_exchange_code_for_token_mocked(self):
        from maestroia.services import meta_service

        dummy_resp = MagicMock()
        dummy_resp.json.return_value = {"access_token": "EAAX...", "expires_in": 5183944}
        dummy_resp.raise_for_status.return_value = None

        from maestroia.config import settings
        # garantir app id/secret temporários para o teste
        settings.META_APP_ID = 'test-app-id'
        settings.META_APP_SECRET = 'test-secret'
        with patch('requests.get', return_value=dummy_resp):
            res = meta_service.exchange_code_for_token('fake-code', 'http://localhost/callback')
            self.assertEqual(res.get('status'), 'ok')
            self.assertIn('data', res)


if __name__ == '__main__':
    unittest.main()
