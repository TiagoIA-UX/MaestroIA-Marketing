from maestroia.config import settings
from typing import Optional


def get_meta_oauth_url(redirect_uri: str, scope: str = "pages_manage_posts,pages_read_engagement") -> str:
    app_id = settings.META_APP_ID
    if not app_id:
        return "[FALLBACK] META_APP_ID não configurado"
    return f"https://www.facebook.com/v16.0/dialog/oauth?client_id={app_id}&redirect_uri={redirect_uri}&scope={scope}"


def exchange_code_for_token(code: str, redirect_uri: str) -> dict:
    # Troca código por access_token via Graph API
    app_id = settings.META_APP_ID
    app_secret = getattr(settings, 'META_APP_SECRET', None)
    if not app_id or not app_secret:
        return {"status": "fallback", "message": "META_APP_ID ou META_APP_SECRET não configurado"}

    token_url = (
        f"https://graph.facebook.com/v16.0/oauth/access_token?client_id={app_id}"
        f"&redirect_uri={redirect_uri}&client_secret={app_secret}&code={code}"
    )
    try:
        import requests
        resp = requests.get(token_url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        # data contém access_token e expires_in
        return {"status": "ok", "data": data}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def create_post(page_id: str, message: str, access_token: Optional[str] = None) -> dict:
    token = access_token or settings.META_ACCESS_TOKEN
    if not token:
        return {"status": "fallback", "message": "Meta access token não configurado"}
    # Implementar chamada POST para /{page_id}/feed
    return {"status": "scaffold", "page_id": page_id, "message": message}
