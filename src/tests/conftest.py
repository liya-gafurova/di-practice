import pytest
import pytest_asyncio
from dependency_injector import providers
from dependency_injector.wiring import inject, Provide
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine

import domain
from core.dependencies import create_engine_once, Container
from core.settings import settings
from domain.user.entities import User
from shared.database import Base


def create_engine_for_tests(db_url):
    # https://stackoverflow.com/questions/73613457/runtimeerror-task-running-at-at-got-future-future-pending-cb-protocol
    engine = create_async_engine(db_url.unicode_string(), poolclass=NullPool)
    from shared.database import Base
    Base.metadata.bind = engine
    return engine


@pytest.fixture(scope='session')
def container():
    container = Container()
    container.engine.override(providers.Singleton(create_engine_for_tests, db_url=container.config.SQLALCHEMY_DATABASE_URI))
    container.config.from_dict(settings.__dict__)
    container.wire(modules=[
        __name__,
        'domain.user.commands',
        'domain.user.queries',
        'domain.account.commands',
        'domain.account.queries'
    ])

    return container


@pytest_asyncio.fixture
async def clean_db(container):
    engine = container.engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
@inject
async def user(clean_db, container, db_session=Provide[Container.db_session], repo=Provide[Container.user_repo]):
    repo.session = db_session()

    user = User(id=User.next_id(), name='user name', email='example@test.com')

    await repo.add(user)

    return user
