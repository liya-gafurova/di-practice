import uuid
from dataclasses import dataclass

from dependency_injector.wiring import inject, Provide

from core.dependencies import Container
from domain.account.entities import AccountNumber
from domain.account.repositories import AccountRepository
from domain.user.repositories import UserRepository
from shared.exceptions import IncorrectData


@dataclass
class ShareAccountAccessDTO:
    account_number: AccountNumber
    account_owner_id: uuid.UUID
    share_access_with_id: uuid.UUID


@inject
async def share_account_access(
        command: ShareAccountAccessDTO,
        session_maker=Provide[Container.db_session],
        account_repo: AccountRepository = Provide[Container.account_repo],
        user_repo: UserRepository = Provide[Container.user_repo]
):
    session = session_maker()
    account_repo.session = session
    user_repo.session = session
    # check account and user are present in db
    shared_account = await account_repo.get_by_number(command.account_number, command.account_owner_id)
    account_accessor = await user_repo.get_by_id(command.share_access_with_id)

    # check account already accessed by target user
    target_user_accounts = await account_repo.get_all__user(command.share_access_with_id)
    if command.account_number in [account.number for account in target_user_accounts]:
        raise IncorrectData(message='This account already accessed by User.')

    # share access
    await account_repo.share_access(shared_account.id, account_accessor.id)

    return shared_account