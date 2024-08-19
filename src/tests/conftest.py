import random
from decimal import Decimal

import pytest
import pytest_asyncio
from dependency_injector import providers
from dependency_injector.wiring import inject, Provide
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine

from core.dependencies import Container
from core.settings import settings
from domain.account.commands import create_account, CreateAccountDTO, AddTransactionDTO, add_transaction_for_user
from domain.account.entities import Account
from domain.account.queries import get_account_by_id, GetAccountByIdDTO
from domain.transaction.entities import Transaction, TransactionType
from domain.user.entities import User
from shared.database import Base


def create_engine_for_tests(db_url):
    # https://stackoverflow.com/questions/73613457/runtimeerror-task-running-at-at-got-future-future-pending-cb-protocol
    # to review db requests , echo=True
    engine = create_async_engine(db_url.unicode_string(), poolclass=NullPool, echo=True)
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
async def user_account(clean_db, container, user):
    # if balance > 0, account is created with balance = 0.0,
    # then correction tx is created to fix "income"

    balance = Decimal(random.uniform(10, 100))
    account = await create_account(CreateAccountDTO(
        user.id,
        'fixture_account',
        balance=balance
    ))

    return user, account


@pytest_asyncio.fixture
async def user_accounts(clean_db, container, user):
    accounts = []
    for i in range(5):
        balance = random.uniform(10, 100)
        account = await create_account(CreateAccountDTO(user.id, f'fixture_account_{i}', balance))
        accounts.append(account)

    return user, accounts


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
    balance = Decimal(random.uniform(10, 100))
    account = await create_account(CreateAccountDTO(
        another_user.id,
        'fixture_account',
        balance=balance
    ))

    return another_user, account


@pytest_asyncio.fixture
async def another_user_accounts(clean_db, container, another_user):
    accounts = []
    for i in range(5):
        balance = Decimal(random.uniform(10, 100))
        account = await create_account(CreateAccountDTO(
            another_user.id,
            f'fixture_account_{i}',
            balance=balance
        ))
        accounts.append(account)

    return another_user, accounts


async def add_txs_to_user_accounts(
        user: User,
        accounts: list[Account],
        txs_count: int = 10
):
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
            credit_acc = await get_account_by_id(GetAccountByIdDTO(user.id, credit_and_debit_accounts[0].id))
            amount = credit_acc.balance * Decimal(0.5)

        tx = await add_transaction_for_user(
            AddTransactionDTO(
                user_id=user.id,
                credit_account=credit_and_debit_accounts[0].number if credit_and_debit_accounts[0] else None,
                debit_account=credit_and_debit_accounts[1].number if credit_and_debit_accounts[1] else None,
                amount=amount
            )
        )
        transactions.append(tx)

    return transactions


@pytest_asyncio.fixture
async def user_accounts_transactions(
        clean_db, container,
        user_accounts
):
    user, accounts = user_accounts

    transactions = await add_txs_to_user_accounts(user, accounts, 10)

    return user, accounts, transactions


@pytest_asyncio.fixture
async def another_user_transactions(
        clean_db,
        container,
        another_user_accounts
):
    another_user, accounts = another_user_accounts

    transactions = await add_txs_to_user_accounts(another_user, accounts, 5)

    return another_user, accounts, transactions
