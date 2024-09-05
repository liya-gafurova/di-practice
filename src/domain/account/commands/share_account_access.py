import uuid
from dataclasses import dataclass

from dependency_injector.wiring import inject, Provide

from core.dependencies import Container
from domain.account.repositories import AccountRepository
from domain.user.repositories import UserRepository


@dataclass
class ShareAccountAccessDTO:
    account_id: uuid.UUID
    account_owner_id: uuid.UUID
    share_access_with_id: uuid.UUID


@inject
async def share_account_access(
        command: ShareAccountAccessDTO,
        session_maker=Provide[Container.db_session],
        account_repo: AccountRepository = Provide[Container.account_repo],
        user_repo: UserRepository = Provide[Container.user_repo]
):
    account_repo.session = session_maker()
