from typing import Optional
from maestroia.config import settings

def get_oauth_authorize_url(redirect_uri: str, scope: str = "https://www.googleapis.com/auth/adwords") -> str:
    """Retorna URL de autorização OAuth para Google Ads (scaffolding).

    O fluxo real requer configuração de credenciais e endpoints. Aqui retornamos uma URL exemplo
    ou message de fallback quando não configurado.
    """
    client_id = settings.GOOGLE_ADS_CLIENT_ID
    if not client_id:
        return "[FALLBACK] GOOGLE_ADS_CLIENT_ID não configurado"
    # Scaffold URL (o formato real usa Google OAuth endpoints)
    return f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope={scope}"


def exchange_code_for_tokens(code: str, redirect_uri: str) -> dict:
    """Troca código OAuth por tokens (scaffolding)."""
    # Implementar troca via requests para https://oauth2.googleapis.com/token
    return {"status": "scaffold", "message": "Implement token exchange using Google OAuth endpoints"}


def create_campaign(customer_id: str, campaign_body: dict) -> dict:
    """Scaffold para criação de campanha no Google Ads.

    Retorna fallback quando credenciais não estiverem presentes.
    """
    if not settings.GOOGLE_ADS_CLIENT_ID:
        return {"status": "fallback", "message": "Google Ads não configurado"}
    return {"status": "scaffold", "campaign": campaign_body}
