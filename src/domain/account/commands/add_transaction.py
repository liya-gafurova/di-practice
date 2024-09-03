import uuid
from dataclasses import dataclass
from decimal import Decimal

from dependency_injector.wiring import inject, Provide

from core.dependencies import Container
from domain.account.entities import AccountNumber
from domain.account.repositories import AccountRepository

from domain.transaction.commands import CreateTransactionDTO, create_transaction
from domain.transaction.entities import TransactionType


@dataclass
class AddTransactionDTO(CreateTransactionDTO):
    pass


@inject
async def add_transaction_for_user(
        command: AddTransactionDTO
):
    assert isinstance(command, AddTransactionDTO)

    tx = await create_transaction(
        CreateTransactionDTO(
            user_id=command.user_id,
            credit_account=command.credit_account,
            debit_account=command.debit_account,
            amount=command.amount,
            category_id=command.category_id
        )
    )

    if command.credit_account:
        await update_account_balance(
            UpdateAccountBalanceDTO(command.credit_account)
        )

    if command.debit_account:
        await update_account_balance(
            UpdateAccountBalanceDTO(command.debit_account)
        )

    return tx


@dataclass
class AddCorrectionTransactionDTO:
    user_id: uuid.UUID
    account_number: AccountNumber
    current_balance: Decimal
    new_balance: Decimal


@inject
async def add_correction_transaction(
        command: AddCorrectionTransactionDTO
):
    assert isinstance(command, AddCorrectionTransactionDTO)

    balance_delta = command.new_balance - command.current_balance

    debit_account, credit_account = None, None
    if balance_delta < Decimal(0.00):
        # balances decreases
        credit_account = command.account_number
    else:
        # balance increases
        debit_account = command.account_number

    tx = await create_transaction(
        CreateTransactionDTO(
            command.user_id,
            credit_account=credit_account,
            debit_account=debit_account,
            amount=abs(balance_delta),
            type=TransactionType.CORRECTION
        )
    )

    await update_account_balance(
        UpdateAccountBalanceDTO(command.account_number)
    )

    return tx


@dataclass
class UpdateAccountBalanceDTO:
    account_number: AccountNumber


@inject
async def update_account_balance(
        command: UpdateAccountBalanceDTO,
        session_maker=Provide[Container.db_session],
        account_repo: AccountRepository = Provide[Container.account_repo]
):
    session = session_maker()
    account_repo.session = session

    account = await account_repo.get_by_number(command.account_number)
    balance_delta = await account_repo.calculate_balance(account.id)

    # if balance changes since last calculation
    if balance_delta != Decimal(0.00):
        account.balance = account.balance + balance_delta

        await account_repo.update_balance(account)

    return account
