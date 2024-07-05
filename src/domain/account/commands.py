import uuid
from dataclasses import dataclass
from decimal import Decimal

from dependency_injector.wiring import inject, Provide

from core.dependencies import Container
from domain.account.entities import Account
from domain.account.repositories import AccountRepository
from domain.user.repositories import UserRepository
from shared.exceptions import EntityNotFoundException, IncorrectData

INCORRECT_BALANCE__MSG = 'Account Balance cannot be less than 0.00'


@dataclass
class CreateAccountDTO:
    name: None | str
    user_id: uuid.UUID
    balance: Decimal | float = Decimal(0.00)


@inject
async def create_account(
        command: CreateAccountDTO,
        session_maker=Provide[Container.db_session],
        account_repo: AccountRepository = Provide[Container.account_repo],
        user_repo: UserRepository = Provide[Container.user_repo]
):
    session = session_maker()
    account_repo.session = session
    user_repo.session = session

    # check user exists
    user = await user_repo.get_by_id(command.user_id)

    # create account
    if command.balance < Decimal(0.00):
        raise IncorrectData(INCORRECT_BALANCE__MSG)

    new_account = Account(
        id=Account.next_id(),
        owner_id=user.id,
        name=command.name,
        number=Account.generate_number(),
        balance=command.balance
    )

    await account_repo.add(new_account)

    return new_account


@dataclass
class UpdateAccountDTO:
    user_id: uuid.UUID
    account_id: uuid.UUID
    name: None | str
    balance: None | Decimal


@inject
async def update_account(
        command: UpdateAccountDTO,
        session_maker=Provide[Container.db_session],
        account_repo=Provide[Container.account_repo]
):
    account_repo.session = session_maker()

    account = await account_repo.get_by_id(command.account_id)

    if command.user_id != account.owner_id:
        print('User tries to update account, which does no owned by user.')
        raise EntityNotFoundException(command.account_id)

    if command.name:
        account.name = command.name
    if command.balance:
        if command.balance < Decimal(0.00):
            raise IncorrectData(INCORRECT_BALANCE__MSG)

        # TODO
        # create correction tx
        # recalculate balance
        # update balance
        # account.balance = command.balance

        await account_repo.update(account)

    return account


@dataclass
class DeleteAccountDTO:
    user_id: uuid.UUID
    account_id: uuid.UUID


@inject
async def delete_account(
        command: DeleteAccountDTO,
        account_repo=Provide[Container.account_repo],
        session_maker=Provide[Container.db_session]
):
    account_repo.session = session_maker()

    account = await account_repo.get_by_id(command.account_id)

    if command.user_id != account.owner_id:
        print('User tries to delete account, which does no owned by user.')
        raise EntityNotFoundException(command.account_id)

    await account_repo.remove(account)

    return account
