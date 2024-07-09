import asyncio
import uuid

import streamlit as st
from dependency_injector import providers
from pydash import find

from client.models import AccountReadModel, TransactionReadModel
from core.dependencies import Container
from core.settings import settings
from domain.account.commands import CreateAccountDTO, create_account, AddTransactionDTO, add_transaction_for_user
from domain.transaction.queries import get_user_transactions, GetUserTransactionsDTO
from src.domain.account.entities import Account
from src.domain.account.queries import GetAllUserAccountsDTO, get_all_user_accounts, get_account_by_number, \
    GetAccountByNumberDTO
from src.domain.user.queries import get_user_by_id, GetUserDTO
from tests.conftest import create_engine_for_tests

st.title('Personal Finance')

DB_USER_ID = '3ddf2e94-1eba-4079-8719-dc9fafa7edde'

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


async def get_accounts_data(user):

    data: list[Account] = await get_all_user_accounts(GetAllUserAccountsDTO(user.id))

    display_data = [AccountReadModel(
        number=account.number,
        name=account.name,
        balance=account.balance
    ).dict() for account in data]

    return display_data


async def get_transactions_data(user):
    user = await get_user_by_id(GetUserDTO(id=uuid.UUID(DB_USER_ID)))
    txs = await get_user_transactions(GetUserTransactionsDTO(user.id))
    user_accounts = await get_all_user_accounts(GetAllUserAccountsDTO(user.id))

    display_data = []
    for tx in txs:
        credit_acc = find(user_accounts, lambda acc: acc.id == tx.credit_account)
        debit_acc = find(user_accounts, lambda acc: acc.id == tx.debit_account)
        display_data.append(
            TransactionReadModel(
                debit_account=debit_acc.name if debit_acc else None,
                amount=tx.amount,
                credit_account=credit_acc.name if credit_acc else None,
                type=tx.type
            ).dict()
        )
    return display_data


async def accounts_page(st):
    user = await get_user_by_id(GetUserDTO(id=uuid.UUID(DB_USER_ID)))
    with st.form('Add account'):
        account_name = st.text_input('Account Name')
        account_balance = st.number_input('Account Balance')

        submitted = st.form_submit_button("Add")
        if submitted:
            await create_account(
                CreateAccountDTO(
                    user_id=uuid.UUID(DB_USER_ID),
                    name=account_name,
                    balance=account_balance
                )
            )
    accounts_data = await get_accounts_data(user)
    st.table(data=accounts_data)

    with st.form('Add Transaction'):
        from_number = st.text_input('From Account', value=None)
        to_number = st.text_input('To Account', value=None)
        amount = st.number_input('Transaction Amount')

        submitted = st.form_submit_button("Add")
        if submitted:
            debit_account, credit_account = None, None
            if to_number:
                debit_account = await get_account_by_number(GetAccountByNumberDTO(
                    user_id=uuid.UUID(DB_USER_ID),
                    account_number=to_number
                ))
            if from_number:
                credit_account = await get_account_by_number(GetAccountByNumberDTO(
                    user_id=uuid.UUID(DB_USER_ID),
                    account_number=from_number
                ))
            await add_transaction_for_user(
                AddTransactionDTO(
                    user_id=uuid.UUID(DB_USER_ID),
                    credit_account_id=credit_account.id if credit_account else None,
                    debit_account_id=debit_account.id if debit_account else None,
                    amount=amount
                )
            )

    txs_data = await get_transactions_data(user)
    st.table(data=txs_data)


if __name__ == '__main__':

    asyncio.run(accounts_page(st))
