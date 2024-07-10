import uuid
from dataclasses import dataclass
from decimal import Decimal

from dependency_injector.wiring import inject, Provide

from core.dependencies import Container
from domain.account.commands.add_transaction import add_correction_transaction, AddCorrectionTransactionDTO
from domain.account.commands.shared import INCORRECT_BALANCE__MSG
from domain.account.entities import AccountNumber
from domain.account.repositories import AccountRepository

from shared.exceptions import EntityNotFoundException, IncorrectData


@dataclass
class UpdateAccountDTO:
    user_id: uuid.UUID
    account_number: AccountNumber
    name: None | str
    balance: None | Decimal


@inject
async def update_account(
        command: UpdateAccountDTO,
        session_maker=Provide[Container.db_session],
        account_repo:AccountRepository=Provide[Container.account_repo]
):
    account_repo.session = session_maker()

    account = await account_repo.get_by_number(command.account_number)

    if command.user_id != account.owner_id:
        print('User tries to update account, which does no owned by user.')
        raise EntityNotFoundException(command.account_number)

    if command.name:
        account.name = command.name
        await account_repo.update(account)

    if command.balance and command.balance != account.balance:
        if command.balance < Decimal(0.00):
            raise IncorrectData(INCORRECT_BALANCE__MSG)

        await add_correction_transaction(
            command=AddCorrectionTransactionDTO(
                user_id=command.user_id,
                account_number=command.account_number,
                new_balance=command.balance,
                current_balance=account.balance
            )
        )

    return account


