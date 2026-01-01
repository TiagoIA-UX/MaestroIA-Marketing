from typing import Optional
from maestroia.config import settings

try:
    import mercadopago
except Exception:
    mercadopago = None


def create_preference(title: str, price: float, quantity: int = 1) -> dict:
    """Cria preferência de pagamento no Mercado Pago. Retorna dicionário com dados da preferência.

    Se a biblioteca `mercadopago` não estiver instalada ou credencial ausente, retorna um dicionário de fallback.
    """
    token = settings.MERCADOPAGO_ACCESS_TOKEN
    if not token or not mercadopago:
        return {"status": "fallback", "init_point": None, "message": "MercadoPago não configurado"}

    try:
        sdk = mercadopago.SDK(token)
        preference_data = {
            "items": [
                {"title": title, "quantity": quantity, "unit_price": float(price)}
            ]
        }
        preference = sdk.preference().create(preference_data)
        return preference
    except Exception as e:
        return {"status": "error", "message": str(e)}


def verify_payment(payment_id: str) -> dict:
    # Implementação simples de verificação (depende da API usada)
    if not mercadopago:
        return {"status": "fallback", "paid": False}
    try:
        sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
        payment = sdk.payment().get(payment_id)
        return payment
    except Exception as e:
        return {"status": "error", "message": str(e)}
