from datetime import datetime
from decimal import Decimal

from sqlalchemy import String, ForeignKey, Numeric, DateTime, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship

from shared.database import Base


class UserModel(Base):
    __tablename__ = 'user'
    username: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=True)


class AccountModel(Base):
    __tablename__ = 'account'
    name: Mapped[str] = mapped_column(String(128), unique=False, index=True, nullable=True)
    owner_id: Mapped[str] = mapped_column(ForeignKey('user.id'))
    number: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)


class AccountAccessModel(Base):
    __tablename__ = 'account_access'
    account_id: Mapped[str] = mapped_column(ForeignKey('account.id'), nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey('user.id'), nullable=False)


class AccountBalanceModel(Base):
    __tablename__ = 'account_balance'

    account_id: Mapped[str] = mapped_column(ForeignKey('account.id'), unique=True)
    balance: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CategoryModel(Base):
    __tablename__ = 'category'
    __table_args__ = (
        UniqueConstraint('name', 'user_id', 'deleted_at', name='unique_category_for_user'),
    )
    name: Mapped[str] = mapped_column(String(128), index=True, unique=False, nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey('user.id'), nullable=True)


class TransactionModel(Base):
    __tablename__ = 'transaction'
    user_id: Mapped[str] = mapped_column(ForeignKey('user.id'))
    credit_account: Mapped[str] = mapped_column(String(128), index=True, unique=False, nullable=True)
    debit_account: Mapped[str] = mapped_column(String(128), index=True, unique=False, nullable=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    category_id: Mapped['str'] = mapped_column(ForeignKey('category.id'), nullable=True)
    type: Mapped[str] = mapped_column(String(128), nullable=True, index=True, unique=False)

    category: Mapped["CategoryModel"] = relationship(lazy='joined')
