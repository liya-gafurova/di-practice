import uuid
from dataclasses import dataclass

from dependency_injector.wiring import Provide, inject
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import Container
from domain.account.entities import AccountNumber
from domain.account.repositories import AccountRepository
from shared.exceptions import EntityNotFoundException
from shared.interfaces import Query


@dataclass
class GetAccountByIdDTO(Query):
    user_id: uuid.UUID
    account_id: uuid.UUID


@inject
async def get_account_by_id(
        query: GetAccountByIdDTO,
        session: AsyncSession,
        account_repo: AccountRepository = Provide[Container.account_repo]
):
    account_repo.session = session

    account = await account_repo.get_user_account_by_id(query.account_id, query.user_id)

    return account


@dataclass
class GetAccountByNumberDTO(Query):
    user_id: uuid.UUID
    account_number: str


@inject
async def get_account_by_number(
        query: GetAccountByNumberDTO,
        session: AsyncSession,
        account_repo: AccountRepository = Provide[Container.account_repo]
):
    account_repo.session = session

    account = await account_repo.get_by_number(query.account_number, query.user_id)

    return account


@dataclass
class GetAllUserAccountsDTO(Query):
    user_id: uuid.UUID


@inject
async def get_all_user_accounts(
        query: GetAllUserAccountsDTO,
        session: AsyncSession,
        account_repo: AccountRepository = Provide[Container.account_repo]
):
    account_repo.session = session

    accounts = await account_repo.get_all__user(query.user_id)

    return accounts
