from dependency_injector import providers, containers
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from core.settings import settings
from storage.user import InMemoryUserRepository, UserSqlAlchemyRepository


def _default(val):
    import uuid

    if isinstance(val, uuid.UUID):
        return str(val)
    raise TypeError()


def dumps(d):
    import json

    return json.dumps(d, default=_default)


def create_engine_once():
    engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI, json_serializer=dumps)
    from shared.database import Base
    Base.metadata.bind = engine
    return engine


class Container(containers.DeclarativeContainer):
    engine = providers.Singleton(create_engine_once)
    db_session = providers.Dependency(instance_of=AsyncSession)

    user_storage = providers.Singleton(UserSqlAlchemyRepository, db_session=db_session)


class TransactionContainer(containers.DeclarativeContainer):
    pass