import uuid
from dataclasses import dataclass
from decimal import Decimal

from dependency_injector.wiring import inject, Provide

from core.dependencies import Container
from domain.account.commands.add_transaction import add_correction_transaction, AddCorrectionTransactionDTO
from domain.account.commands.shared import INCORRECT_BALANCE__MSG

from domain.account.entities import Account
from domain.account.repositories import AccountRepository
from domain.user.repositories import UserRepository
from shared.exceptions import IncorrectData


@dataclass
class CreateAccountDTO:
    user_id: uuid.UUID
    name: None | str
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

    command.balance = command.balance if isinstance(command.balance, Decimal) \
        else Decimal(command.balance).quantize(Decimal('0.01'))

    # create account
    if command.balance < Decimal(0.00):
        raise IncorrectData(INCORRECT_BALANCE__MSG)

    init_balance = Decimal(0.00)
    new_account = Account(
        id=Account.next_id(),
        owner_id=user.id,
        name=command.name,
        number=Account.generate_number(),
        balance=init_balance
    )

    await account_repo.add(new_account)

    if command.balance > init_balance:
        await add_correction_transaction(
            command=AddCorrectionTransactionDTO(
                user_id=command.user_id,
                account_number=new_account.number,
                new_balance=command.balance,
                current_balance=init_balance
            )
        )
        new_account.balance = command.balance

    return new_account
