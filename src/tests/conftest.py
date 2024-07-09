import random

import pytest
import pytest_asyncio
from dependency_injector import providers
from dependency_injector.wiring import inject, Provide
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine

import domain
from core.dependencies import create_engine_once, Container
from core.settings import settings
from domain.account.entities import Account
from domain.user.entities import User
from shared.database import Base


def create_engine_for_tests(db_url):
    # https://stackoverflow.com/questions/73613457/runtimeerror-task-running-at-at-got-future-future-pending-cb-protocol
    # to review db requests , echo=True
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
        'domain.account.queries',
        'domain.transaction.commands',
        'domain.transaction.queries'
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


@pytest_asyncio.fixture
async def user_accounts(clean_db, container, user):
    session_maker = container.db_session()
    account_repo = container.account_repo()
    account_repo.session = session_maker()

    accounts = []
    for i in range(5):
        account = Account(
            id=Account.next_id(),
            name=f'fixture_account_{i}',
            number=Account.generate_number(),
            owner_id=user.id,
            balance=random.uniform(10, 100)
        )

        await account_repo.add(account)
        accounts.append(account)

    return user, accounts


@pytest_asyncio.fixture
async def user_account(clean_db, container, user):
    session_maker = container.db_session()
    account_repo = container.account_repo()
    account_repo.session = session_maker()

    # TODO: not completely correct to create account via repo.
    # if balance > 0, account is created with balance = 0.0, then correction tx is created to fix "income"

    account = Account(
        id=Account.next_id(),
        name='fixture_account',
        number=Account.generate_number(),
        owner_id=user.id,
        balance=random.uniform(10, 100)
    )

    await account_repo.add(account)

    return user, account


@pytest_asyncio.fixture
async def another_user(clean_db, container):
    session_maker = container.db_session()
    user_repo = container.user_repo()
    user_repo.session = session_maker()

    user = User(id=User.next_id(), name='Another user name', email='example@test.com')

    await user_repo.add(user)

    return user


@pytest_asyncio.fixture
async def another_user_account(clean_db, container, another_user):
    session_maker = container.db_session()
    account_repo = container.account_repo()
    account_repo.session = session_maker()

    account = Account(
        id=Account.next_id(),
        name='fixture_account__another',
        number=Account.generate_number(),
        owner_id=another_user.id,
        balance=random.uniform(10, 100)
    )

    await account_repo.add(account)

    return another_user, account


@pytest_asyncio.fixture
async def another_user_accounts(clean_db, container, another_user):
    session_maker = container.db_session()
    account_repo = container.account_repo()
    account_repo.session = session_maker()

    accounts = []
    for i in range(5):
        account = Account(
            id=Account.next_id(),
            name=f'fixture_account_{i}',
            number=Account.generate_number(),
            owner_id=another_user.id,
            balance=random.uniform(10, 100)
        )

        await account_repo.add(account)
        accounts.append(account)

    return another_user, accounts
