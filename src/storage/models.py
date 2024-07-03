from sqlalchemy import String
from sqlalchemy.orm import mapped_column, Mapped

from shared.database import Base


class UserModel(Base):
    __tablename__ = 'user'
    username: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=True)
