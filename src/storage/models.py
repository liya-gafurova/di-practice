from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

from shared.database import Base


class UserModel(Base):
    __tablename__ = 'user'
    username: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=True)


class AccountModel(Base):
    __tablename__ = 'account'
    name: Mapped[str] = mapped_column(String(128), unique=False, index=True, nullable=True)
    owner_id: Mapped[str] = mapped_column(ForeignKey('user.id'))
    number: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
