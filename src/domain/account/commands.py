import uuid
from dataclasses import dataclass
from decimal import Decimal

from dependency_injector.wiring import inject, Provide

from core.dependencies import Container
from domain.account.entities import Account
from domain.account.repositories import AccountRepository
from domain.transaction.commands import CreateTransactionDTO, create_transaction
from domain.transaction.entities import TransactionType
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

    command.balance = Decimal(command.balance).quantize(Decimal('0.01')) if not isinstance(command.balance, Decimal) else command.balance

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
        await add_correction_transaction_for_user(
            command=AddCorrectionTransactionDTO(
                user_id=command.user_id,
                account_id=new_account.id,
                new_balance=command.balance,
                current_balance=init_balance
            )
        )
        new_account.balance = command.balance

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
        await account_repo.update(account)

    if command.balance and command.balance != account.balance:
        if command.balance < Decimal(0.00):
            raise IncorrectData(INCORRECT_BALANCE__MSG)

        await add_correction_transaction_for_user(
            command=AddCorrectionTransactionDTO(
                user_id=command.user_id,
                account_id=command.account_id,
                new_balance=command.balance,
                current_balance=account.balance
            )
        )

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


@dataclass
class UpdateAccountBalanceDTO:
    account_id: uuid.UUID


@inject
async def update_account_balance(
        command: UpdateAccountBalanceDTO,
        session_maker=Provide[Container.db_session],
        account_repo: AccountRepository = Provide[Container.account_repo]
):
    session = session_maker()
    account_repo.session = session

    account = await account_repo.get_by_id(command.account_id)
    balance_delta = await account_repo.calculate_balance(account.id)

    # if balance changes since last calculation
    if balance_delta > Decimal(0.00):
        account.balance = account.balance + balance_delta

        await account_repo.update_balance(account)

    return account


@dataclass
class AddTransactionDTO(CreateTransactionDTO):
    pass


@inject
async def add_transaction_for_user(
        command: AddTransactionDTO
):
    await create_transaction(
        CreateTransactionDTO(
            command.user_id,
            command.credit_account_id,
            command.debit_account_id,
            command.amount
        )
    )

    if command.credit_account_id:
        await update_account_balance(
            UpdateAccountBalanceDTO(command.credit_account_id)
        )

    if command.debit_account_id:
        await update_account_balance(
            UpdateAccountBalanceDTO(command.debit_account_id)
        )


@dataclass
class AddCorrectionTransactionDTO:
    user_id: uuid.UUID
    account_id: uuid.UUID
    current_balance: Decimal
    new_balance: Decimal


@inject
async def add_correction_transaction_for_user(
        command: AddCorrectionTransactionDTO
):
    assert isinstance(command, AddCorrectionTransactionDTO)

    balance_delta = command.new_balance - command.current_balance

    debit_account, credit_account = None, None
    if balance_delta < Decimal(0.00):
        # balances decreases
        credit_account = command.account_id
    else:
        # balance increases
        debit_account = command.account_id

    await create_transaction(
        CreateTransactionDTO(
            command.user_id,
            credit_account_id=credit_account,
            debit_account_id=debit_account,
            amount=abs(balance_delta),
            type=TransactionType.CORRECTION
        )
    )

    await update_account_balance(
        UpdateAccountBalanceDTO(command.account_id)
    )