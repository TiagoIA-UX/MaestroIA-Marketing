from maestroia.core.database import SessionLocal
from maestroia.models.finance import Account, Wallet
from sqlalchemy.orm import Session


def create_account(email: str, user_id: int = None) -> dict:
    db: Session = SessionLocal()
    try:
        acc = Account(user_id=user_id, email=email)
        db.add(acc)
        db.flush()
        # create default BRL wallet
        brl = Wallet(account_id=acc.id, currency='BRL', balance=0)
        db.add(brl)
        db.commit()
        return {"status": "ok", "account_id": acc.id}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


def get_wallet(account_id: int, currency: str = 'BRL'):
    db: Session = SessionLocal()
    try:
        w = db.query(Wallet).filter(Wallet.account_id == account_id, Wallet.currency == currency).first()
        return w
    finally:
        db.close()


def get_balance(account_id: int, currency: str = 'BRL') -> float:
    w = get_wallet(account_id, currency)
    return float(w.balance) if w else 0.0
