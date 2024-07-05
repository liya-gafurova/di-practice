import uuid
from dataclasses import dataclass
from decimal import Decimal

from dependency_injector.wiring import inject, Provide

from core.dependencies import Container
from domain.transaction.entities import Transaction
from shared.exceptions import EntityNotFoundException, IncorrectData


@dataclass
class CreateTransactionDTO:
    user_id: uuid.UUID
    credit_account_id: uuid.UUID
    debit_account_id: uuid.UUID
    amount: int | float | Decimal


@inject
async def create_transaction(
        command: CreateTransactionDTO,
        session_maker=Provide[Container.db_session],
        tx_repo=Provide[Container.tx_repo],
        account_repo=Provide[Container.account_repo]
):
    session = session_maker()
    account_repo.session = session
    tx_repo.session = session

    if command.debit_account_id == command.credit_account_id:
        raise IncorrectData('Credit and Debit accounts cannot be the same.')

    credit_account = await account_repo.get_by_id(command.credit_account_id)
    debit_account = await account_repo.get_by_id(command.debit_account_id)

    # yet only between user accounts
    if credit_account.owner_id != command.user_id \
        or debit_account.owner_id != command.user_id:
        account_id = credit_account.id if credit_account.owner_id != command.user_id else debit_account.owner_id
        print('User tries to create transaction with account, which does no owned by user.')
        raise EntityNotFoundException(account_id)

    tx = Transaction(
        id=Transaction.next_id(),
        credit_account=credit_account.id,
        debit_account=debit_account.id,
        amount=command.amount,
        user_id=command.user_id
    )

    await tx_repo.add(tx)

    return tx
