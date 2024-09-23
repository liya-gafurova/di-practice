import random
from decimal import Decimal

import pytest
import pytest_asyncio
from dependency_injector import providers
from dependency_injector.wiring import inject, Provide
from requests import session
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine

from core.dependencies import Container
from core.app import Application
from core.settings import settings
from domain.account.commands import CreateAccountDTO, AddTransactionDTO
from domain.account.entities import Account
from domain.account.queries import GetAccountByIdDTO
from domain.category.commands import CreateGeneralCategoryDTO, CreateCustomCategoryDTO
from domain.user.commands import CreateUserDTO
from domain.user.entities import User
from domain.user.queries import GetUserDTO
from shared.database import Base


def create_engine_for_tests(db_url):
    # https://stackoverflow.com/questions/73613457/runtimeerror-task-running-at-at-got-future-future-pending-cb-protocol
    # to review db requests , echo=True
    engine = create_async_engine(
        db_url.unicode_string(),
        poolclass=NullPool,
        # echo=True
    )
    from shared.database import Base
    Base.metadata.bind = engine
    return engine


@pytest.fixture(scope='session')
def container():
    container = Container()
    container.engine.override(
        providers.Singleton(create_engine_for_tests, db_url=container.config.SQLALCHEMY_DATABASE_URI))
    container.config.from_dict(settings.__dict__)
    container.wire(modules=[
        __name__,
        'domain.user.commands',
        'domain.user.queries',
        'domain.account.commands',
        'domain.account.queries',
        'domain.transaction.commands',
        'domain.transaction.queries',
        'domain.category.commands',
        'domain.category.queries'
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
async def user(
        clean_db,
        container,
        app: Application=Provide[Container.app],
):
    user  = await app.execute(
        CreateUserDTO(name='user name', email='example@test.com'),
        container.db_session()
    )

    return user


@pytest_asyncio.fixture
async def user_account(clean_db, container, user):
    # if balance > 0, account is created with balance = 0.0,
    # then correction tx is created to fix "income"
    app = container.app()
    balance = Decimal(random.uniform(10, 100))
    account = await app.execute(CreateAccountDTO(
        user.id,
        'fixture_account',
        balance=balance
    ),
        container.db_session())

    return user, account


@pytest_asyncio.fixture
async def user_accounts(clean_db, container, user):
    accounts = []
    app = container.app()
    for i in range(5):
        balance = random.uniform(10, 100)
        account = await app.execute(CreateAccountDTO(user.id, f'fixture_account_{i}', balance), container.db_session())
        accounts.append(account)

    return user, accounts


@pytest_asyncio.fixture
async def another_user(clean_db, container):
    app = container.app()

    user = await app.execute(
        CreateUserDTO(name='Another user name', email='example@test.com'),
        container.db_session()
    )

    return user


@pytest_asyncio.fixture
async def another_user_account(clean_db, container, another_user):
    app = container.app()
    balance = Decimal(random.uniform(10, 100))
    account = await app.execute(
        CreateAccountDTO(
            another_user.id,
            'fixture_account',
            balance=balance
        ),
        container.db_session()
    )

    return another_user, account


@pytest_asyncio.fixture
async def another_user_accounts(clean_db, container, another_user):
    app = container.app()
    accounts = []
    for i in range(5):
        balance = Decimal(random.uniform(10, 100))
        account = await app.execute(CreateAccountDTO(
            another_user.id,
            f'fixture_account_{i}',
            balance=balance
        ), container.db_session())
        accounts.append(account)

    return another_user, accounts


async def add_txs_to_user_accounts(
        container,
        user: User,
        accounts: list[Account],
        txs_count: int = 10,
):
    app = container.app()
    transactions = []
    for i in range(txs_count):
        # get two random accounts (credit, debit). One of accounts can be none
        possible_idxs_with_None = list(range(0, len(accounts) + 1))
        idxs = random.sample(possible_idxs_with_None, k=2)
        credit_and_debit_accounts = []
        for idx in idxs:
            try:
                credit_and_debit_accounts.append(accounts[idx])
            except IndexError:
                credit_and_debit_accounts.append(None)

        amount = Decimal(random.uniform(10, 100))
        if credit_and_debit_accounts[0]:
            credit_acc = await app.execute(GetAccountByIdDTO(user.id, credit_and_debit_accounts[0].id), container.db_session())
            amount = credit_acc.balance * Decimal(0.5)

        tx = await app.execute(
            AddTransactionDTO(
                user_id=user.id,
                credit_account=credit_and_debit_accounts[0].number if credit_and_debit_accounts[0] else None,
                debit_account=credit_and_debit_accounts[1].number if credit_and_debit_accounts[1] else None,
                amount=amount
            ),
            container.db_session()
        )
        transactions.append(tx)

    return transactions


@pytest_asyncio.fixture
async def user_accounts_transactions(
        clean_db, container,
        user_accounts
):
    app = container.app()
    session = container.db_session()
    user, accounts = user_accounts

    transactions = await add_txs_to_user_accounts(container, user, accounts, 10)

    return user, accounts, transactions


@pytest_asyncio.fixture
async def another_user_transactions(
        clean_db,
        container,
        another_user_accounts
):
    app = container.app()
    session = container.db_session()
    another_user, accounts = another_user_accounts

    transactions = await add_txs_to_user_accounts(container, another_user, accounts, 5)

    return another_user, accounts, transactions


@pytest_asyncio.fixture
async def existing_general_category(clean_db, container):
    app = container.app()
    new_category = await app.execute(
        CreateGeneralCategoryDTO(name='medicine'),
        container.db_session()
    )
    return new_category


@pytest_asyncio.fixture
async def existing_custom_category(clean_db, container, user):

    app = container.app()
    new_category = await app.execute(
        CreateCustomCategoryDTO(name='jeans', user_id=user.id),
        container.db_session()
    )
    return new_category


@pytest_asyncio.fixture
async def existing_custom_category__another_user(clean_db, container, another_user):
    app = container.app()
    new_category = await app.execute(
        CreateCustomCategoryDTO(name='shirts', user_id=another_user.id),
        container.db_session()
    )
    return new_category
