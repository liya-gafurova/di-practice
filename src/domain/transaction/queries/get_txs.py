import uuid
from dataclasses import dataclass

from dependency_injector.wiring import Provide, inject
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import Container
from domain.account.entities import AccountNumber
from domain.account.repositories import AccountRepository
from domain.transaction.repositories import TransactionRepository
from shared.exceptions import EntityNotFoundException
from shared.interfaces import Query


@dataclass
class GetUserTransactionsDTO(Query):
    user_id: uuid.UUID


@inject
async def get_user_transactions(
        query: GetUserTransactionsDTO,
        session: AsyncSession,
        tx_repo: TransactionRepository = Provide[Container.tx_repo]
):
    tx_repo.session = session

    user_txs = await tx_repo.get_user_transactions(query.user_id)

    return user_txs


@dataclass
class GetAccountTransactionsDTO(Query):
    user_id: uuid.UUID
    account_number: AccountNumber


@inject
async def get_account_transactions(
        query: GetAccountTransactionsDTO,
        session: AsyncSession,
        tx_repo: TransactionRepository = Provide[Container.tx_repo],
        account_repo:AccountRepository=Provide[Container.account_repo]
):
    tx_repo.session = session
    account_repo.session = session

    account = await account_repo.get_by_number(query.account_number, query.user_id)

    account_txs = await tx_repo.get_account_transactions(account.number)

    return account_txs
