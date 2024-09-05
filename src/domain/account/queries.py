import uuid
from dataclasses import dataclass

from dependency_injector.wiring import Provide, inject

from core.dependencies import Container
from domain.account.entities import AccountNumber
from domain.account.repositories import AccountRepository
from shared.exceptions import EntityNotFoundException


@dataclass
class GetAccountByIdDTO:
    user_id: uuid.UUID
    account_id: uuid.UUID


@inject
async def get_account_by_id(
        query: GetAccountByIdDTO,
        session_maker=Provide[Container.db_session],
        account_repo: AccountRepository = Provide[Container.account_repo]
):
    account_repo.session = session_maker()

    account = await account_repo.get_user_account_by_id(query.account_id, query.user_id)

    return account


@dataclass
class GetAccountByNumberDTO:
    user_id: uuid.UUID
    account_number: str


@inject
async def get_account_by_number(
        query: GetAccountByNumberDTO,
        session_maker=Provide[Container.db_session],
        account_repo: AccountRepository = Provide[Container.account_repo]
):
    account_repo.session = session_maker()

    account = await account_repo.get_by_number(query.account_number, query.user_id)

    return account


@dataclass
class GetAllUserAccountsDTO:
    user_id: uuid.UUID


@inject
async def get_all_user_accounts(
        query: GetAllUserAccountsDTO,
        session_maker=Provide[Container.db_session],
        account_repo: AccountRepository = Provide[Container.account_repo]
):
    account_repo.session = session_maker()

    accounts = await account_repo.get_all__user(query.user_id)

    return accounts
