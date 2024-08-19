import uuid
from dataclasses import dataclass
from decimal import Decimal

from dependency_injector.wiring import inject, Provide

from core.dependencies import Container
from domain.account.entities import AccountNumber
from domain.account.repositories import AccountRepository
from domain.transaction.entities import Transaction, TransactionType
from shared.exceptions import EntityNotFoundException, IncorrectData


@dataclass
class CreateTransactionDTO:
    user_id: uuid.UUID
    credit_account: AccountNumber | None
    debit_account: AccountNumber | None
    amount: int | float | Decimal
    type: None | TransactionType = None


@inject
async def create_transaction(
        command: CreateTransactionDTO,
        session_maker=Provide[Container.db_session],
        tx_repo=Provide[Container.tx_repo],
        account_repo:AccountRepository=Provide[Container.account_repo]
):
    session = session_maker()
    account_repo.session = session
    tx_repo.session = session

    command.amount = command.amount if isinstance(command.amount, Decimal) \
        else Decimal(command.amount).quantize(Decimal('0.01'))

    if command.debit_account is None and command.credit_account is None:
        raise IncorrectData('Credit and Debit accounts cannot Null')

    if command.debit_account == command.credit_account:
        raise IncorrectData('Credit and Debit accounts cannot be the same.')

    credit_account, debit_account = None, None
    if command.debit_account:
        debit_account = await account_repo.get_by_number(command.debit_account)
    if command.credit_account:
        credit_account = await account_repo.get_by_number(command.credit_account)

    if credit_account and credit_account.owner_id != command.user_id \
            or debit_account and debit_account.owner_id != command.user_id:
        account_number = credit_account.number if credit_account.owner_id != command.user_id else debit_account.number
        print('User tries to create transaction with account, which does no owned by user.')
        raise EntityNotFoundException(account_number)

    if credit_account and credit_account.balance < command.amount:
        raise IncorrectData(f'User tries to transfer from {command.amount} from account with balance {credit_account.balance}')

    if not command.type:
        if credit_account and debit_account:
            command.type = TransactionType.TRANSFER
        elif debit_account:
            command.type = TransactionType.INCOME
        else:
            command.type = TransactionType.EXPENSE

    tx = Transaction(
        id=Transaction.next_id(),
        credit_account=credit_account.number if credit_account else None,
        debit_account=debit_account.number if debit_account else None,
        amount=command.amount,
        user_id=command.user_id,
        type=command.type
    )

    await tx_repo.add(tx)

    return tx


