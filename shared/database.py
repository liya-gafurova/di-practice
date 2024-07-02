import uuid
from datetime import datetime

from sqlalchemy import MetaData, UUID, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy_easy_softdelete.mixin import generate_soft_delete_mixin_class
from sqlalchemy_utils import force_auto_coercion

force_auto_coercion()


class SoftDeleteMixin(generate_soft_delete_mixin_class()):
    # type hint for autocomplete IDE support
    deleted_at: datetime


class Base(DeclarativeBase, SoftDeleteMixin):
    metadata = MetaData(
        naming_convention={
            "ix": "%(column_0_label)s_idx",
            "uq": "%(table_name)s_%(column_0_name)s_key",
            "ck": "%(table_name)s_%(constraint_name)s_check",
            "fk": "%(table_name)s_%(column_0_name)s_%(referred_table_name)s_fkey",
            "pk": "%(table_name)s_pkey"
        }
    )
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow())