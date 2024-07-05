from dependency_injector import providers, containers
from pydantic_core import MultiHostUrl
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from storage.account import AccountSqlalchemyRepository
from storage.transaction import TransactionSqlAlchemyRepository
from storage.user import UserSqlAlchemyRepository


def _default(val):
    import uuid

    if isinstance(val, uuid.UUID):
        return str(val)
    raise TypeError()


def dumps(d):
    import json

    return json.dumps(d, default=_default)


def create_engine_once(db_url: MultiHostUrl):
    engine = create_async_engine(db_url.unicode_string(), json_serializer=dumps)
    from shared.database import Base
    Base.metadata.bind = engine
    return engine


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    engine = providers.Singleton(create_engine_once, db_url=config.SQLALCHEMY_DATABASE_URI)

    async_session_factory = providers.Singleton(
        async_sessionmaker,
        bind=engine
    )
    db_session = providers.Factory(
        async_session_factory
    )

    user_repo = providers.Factory(UserSqlAlchemyRepository)
    account_repo = providers.Factory(AccountSqlalchemyRepository)
    tx_repo = providers.Factory(TransactionSqlAlchemyRepository)

