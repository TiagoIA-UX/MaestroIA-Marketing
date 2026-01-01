from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship
from maestroia.core.database import Base
from datetime import datetime


class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)


class Wallet(Base):
    __tablename__ = 'wallets'
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey('accounts.id'))
    currency = Column(String, index=True)  # e.g., BRL, CO2
    balance = Column(Numeric(18, 6), default=0)
    metadata = Column(JSON, nullable=True)
    account = relationship('Account')


class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String, unique=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    description = Column(String)
    metadata = Column(JSON, nullable=True)


class Entry(Base):
    __tablename__ = 'entries'
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey('transactions.id'))
    wallet_id = Column(Integer, ForeignKey('wallets.id'))
    amount = Column(Numeric(18, 6))
    is_debit = Column(Boolean)
    timestamp = Column(DateTime, default=datetime.utcnow)
    transaction = relationship('Transaction')
