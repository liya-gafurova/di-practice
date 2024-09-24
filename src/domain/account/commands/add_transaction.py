import uuid
from dataclasses import dataclass
from decimal import Decimal

from dependency_injector.wiring import inject, Provide
from sqlalchemy.ext.asyncio import AsyncSession

from core.app import Application
from core.dependencies import Container
from domain.account.entities import AccountNumber
from domain.account.repositories import AccountRepository

from domain.transaction.commands import CreateTransactionDTO
from domain.transaction.entities import TransactionType


@dataclass
class AddTransactionDTO(CreateTransactionDTO):
    pass


@inject
async def add_transaction_for_user(
        command: AddTransactionDTO,
        session: AsyncSession,
        app:Application=Provide[Container.app],
        session_maker=Provide[Container.async_session_factory]
):
    assert isinstance(command, AddTransactionDTO)

    tx = await app.execute(
        CreateTransactionDTO(
            user_id=command.user_id,
            credit_account=command.credit_account,
            debit_account=command.debit_account,
            amount=command.amount,
            category_id=command.category_id
        ),
        session_maker
    )

    if command.credit_account:
        await app.execute(
            UpdateAccountBalanceDTO(command.user_id, command.credit_account),
            session_maker
        )

    if command.debit_account:
        await app.execute(
            UpdateAccountBalanceDTO(command.user_id, command.debit_account),
            session_maker
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
        command: AddCorrectionTransactionDTO,
        session: AsyncSession,
        app: Application=Provide[Container.app],
        session_maker=Provide[Container.async_session_factory]
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

    tx = await app.execute(
        CreateTransactionDTO(
            command.user_id,
            credit_account=credit_account,
            debit_account=debit_account,
            amount=abs(balance_delta),
            type=TransactionType.CORRECTION
        ),
        session_maker
    )

    await app.execute(
        UpdateAccountBalanceDTO(command.user_id, command.account_number),
        session_maker
    )

    return tx


@dataclass
class UpdateAccountBalanceDTO:
    user_id: uuid.UUID
    account_number: AccountNumber


@inject
async def update_account_balance(
        command: UpdateAccountBalanceDTO,
        session: AsyncSession,
        account_repo: AccountRepository = Provide[Container.account_repo]
):
    account_repo.session = session

    account = await account_repo.get_by_number(command.account_number, command.user_id)
    balance_delta = await account_repo.calculate_balance(account.id)

    # if balance changes since last calculation
    if balance_delta != Decimal(0.00):
        account.balance = account.balance + balance_delta

        await account_repo.update_balance(account)

    return account
