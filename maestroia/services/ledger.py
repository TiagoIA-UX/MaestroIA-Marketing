from decimal import Decimal
from maestroia.core.database import SessionLocal
from maestroia.models.finance import Transaction, Entry, Wallet
from sqlalchemy.orm import Session
import uuid


def create_transaction(description: str, postings: list, metadata: dict = None) -> dict:
    """Create a transaction with double-entry postings.

    postings: list of dict {wallet_id, amount (Decimal), is_debit (bool)}
    """
    db: Session = SessionLocal()
    try:
        tx = Transaction(reference=str(uuid.uuid4()), description=description, metadata=metadata)
        db.add(tx)
        db.flush()

        total = Decimal('0')
        for p in postings:
            amt = Decimal(p['amount'])
            total += amt if p.get('is_debit', False) else -amt
            entry = Entry(transaction_id=tx.id, wallet_id=p['wallet_id'], amount=amt, is_debit=p.get('is_debit', False))
            db.add(entry)
            # update wallet balance
            wallet = db.query(Wallet).filter(Wallet.id == p['wallet_id']).with_for_update().first()
            if not wallet:
                db.rollback()
                return {"status": "error", "message": f"Wallet {p['wallet_id']} not found"}
            # debit reduces balance
            if p.get('is_debit', False):
                wallet.balance = wallet.balance - amt
            else:
                wallet.balance = wallet.balance + amt

        if total != 0:
            db.rollback()
            return {"status": "error", "message": "Transaction not balanced"}

        db.commit()
        return {"status": "ok", "transaction_id": tx.id}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()
