
# Rota para buscar histórico de campanhas do usuário autenticado
@app.get("/campaign/history")
def get_campaign_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    campaigns = db.query(Campaign).filter(Campaign.user_id == current_user.id).all()
    history = []
    for c in campaigns:
        history.append({
            "id": c.id,
            "objetivo": c.objetivo,
            "publico_alvo": c.publico_alvo,
            "canais": c.canais.split(",") if c.canais else [],
            "orcamento": c.orcamento,
            "resultado": json.loads(c.resultado) if c.resultado else None
        })
    return {"history": history}

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from maestroia.graphs.marketing_graph import build_marketing_graph
from maestroia.core.state import MaestroState
from maestroia.core.database import get_db, User, hash_password, verify_password
from maestroia.core.auth import create_access_token, get_current_user
import json
import mercadopago
from maestroia.config.settings import MERCADOPAGO_ACCESS_TOKEN
from maestroia.services.meta_service import get_meta_oauth_url, exchange_code_for_token
from maestroia.services.token_store import save_token
from maestroia.config.settings import META_REDIRECT_URI
@app.post("/webhook/mercadopago")
async def webhook_mercadopago(request: Request, db: Session = Depends(get_db)):
    """
    Webhook Mercado Pago: ativa plano conforme valor pago e status aprovado.
    """
    try:
        data = await request.json()
        # Mercado Pago pode enviar diferentes formatos, mas sempre envie o payment_id
        topic = data.get("topic") or data.get("type")
        payment_id = None
        if topic == "payment":
            payment_id = data.get("data", {}).get("id") or data.get("id")
        elif "id" in data:
            payment_id = data["id"]
        if not payment_id:
            return {"error": "payment_id não encontrado"}

        # Consulta o pagamento na API Mercado Pago para garantir status e valor
        sdk = mercadopago.SDK(MERCADOPAGO_ACCESS_TOKEN)
        payment = sdk.payment().get(payment_id)["response"]
        status = payment.get("status")
        payer_email = payment.get("payer", {}).get("email")
        amount = float(payment.get("transaction_amount", 0))

        # Só ativa se o pagamento estiver aprovado
        if status == "approved" and payer_email:
            user = db.query(User).filter(User.email == payer_email).first()
            if user:
                # Define plano conforme valor pago (ajuste os valores conforme seus planos)
                if amount >= 499.90:
                    user.plano = "enterprise"
                elif amount >= 149.90:
                    user.plano = "professional"
                elif amount >= 49.90:
                    user.plano = "starter"
                else:
                    user.plano = "free"
                user.pago = True
                db.commit()
                return {"status": f"Plano '{user.plano}' ativado para {payer_email}"}
            else:
                return {"error": f"Usuário com email {payer_email} não encontrado."}
        return {"status": f"Pagamento recebido, status: {status}"}
    except Exception as e:
        return {"error": str(e)}


@app.get("/auth/meta/start")
def meta_auth_start(user_email: str):
    """Iniciar fluxo OAuth Meta; retorna URL de autorização para o client seguir."""
    redirect = META_REDIRECT_URI
    url = get_meta_oauth_url(redirect)
    # Passar user_email via state poderia ser melhor; aqui retornamos URL e espera-se que o client inclua state param
    return {"auth_url": url, "note": "Inclua parâmetro 'state' com user_email no client para vincular token."}


@app.get("/auth/meta/callback")
def meta_auth_callback(code: str, state: str = None, request: Request = None):
    """Callback para Meta OAuth; troca código por token e persiste usando `token_store`.

    Expects 'state' to contain the user_email to link token to. Returns stored token info.
    """
    redirect = META_REDIRECT_URI
    result = exchange_code_for_token(code, redirect)
    if result.get("status") != "ok":
        raise HTTPException(status_code=400, detail=result.get("message", "Erro ao trocar código"))

    user_key = state or "anonymous"
    # Persistir o token para o usuário
    save_token("meta", user_key, result.get("data"))
    return {"status": "ok", "user": user_key, "data": result.get("data")}

app = FastAPI(title="MaestroIA API")

graph = build_marketing_graph()

@app.post("/register")
def register(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = hash_password(password)
    new_user = User(email=email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    return {"message": "User created"}

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

from maestroia.core.database import Campaign

@app.post("/campaign/run")
async def run_campaign(state: MaestroState, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        result = graph.invoke(state)
        # Salva a campanha no banco de dados
        campaign = Campaign(
            user_id=current_user.id,
            objetivo=state.objetivo if hasattr(state, 'objetivo') else str(getattr(state, 'objetivo', '')),
            publico_alvo=state.publico_alvo if hasattr(state, 'publico_alvo') else str(getattr(state, 'publico_alvo', '')),
            canais=','.join(state.canais) if hasattr(state, 'canais') and isinstance(state.canais, list) else str(getattr(state, 'canais', '')),
            orcamento=str(state.orcamento) if hasattr(state, 'orcamento') else str(getattr(state, 'orcamento', '')),
            resultado=json.dumps(result)
        )
        db.add(campaign)
        db.commit()
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
