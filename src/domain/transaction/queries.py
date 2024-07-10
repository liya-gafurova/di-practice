import uuid
from dataclasses import dataclass

from dependency_injector.wiring import Provide, inject

from core.dependencies import Container
from domain.account.entities import AccountNumber
from domain.account.repositories import AccountRepository
from domain.transaction.repositories import TransactionRepository
from shared.exceptions import EntityNotFoundException


@dataclass
class GetUserTransactionsDTO:
    user_id: uuid.UUID


@inject
async def get_user_transactions(
        query: GetUserTransactionsDTO,
        session_maker=Provide[Container.db_session],
        tx_repo: TransactionRepository = Provide[Container.tx_repo]
):
    tx_repo.session = session_maker()

    user_txs = await tx_repo.get_user_transactions(query.user_id)

    return user_txs


@dataclass
class GetAccountTransactionsDTO:
    user_id: uuid.UUID
    account_number: AccountNumber


@inject
async def get_account_transactions(
        query: GetAccountTransactionsDTO,
        session_maker=Provide[Container.db_session],
        tx_repo: TransactionRepository = Provide[Container.tx_repo],
        account_repo:AccountRepository=Provide[Container.account_repo]
):
    session = session_maker()
    tx_repo.session = session
    account_repo.session = session

    account = await account_repo.get_by_number(query.account_number)
    if account.owner_id != query.user_id:
        raise EntityNotFoundException(query.account_number)

    account_txs = await tx_repo.get_account_transactions(account.number)

    return account_txs
