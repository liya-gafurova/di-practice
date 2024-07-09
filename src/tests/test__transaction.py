import random
import uuid
from decimal import Decimal

import pytest
import pytest_asyncio

from domain.transaction.commands import create_transaction, CreateTransactionDTO
from domain.transaction.queries import get_user_transactions, GetUserTransactionsDTO, get_account_transactions, \
    GetAccountTransactionsDTO
from shared.exceptions import EntityNotFoundException, IncorrectData


@pytest.mark.skip('Duplicate of test "test__create_transaction__transfer_tx"')
@pytest.mark.asyncio
async def test__create_transaction(
        clean_db,
        container,
        user_accounts
):
    user, accounts = user_accounts
    credit_account = accounts[0]
    debit_account = accounts[1]
    amount = credit_account.balance * Decimal(0.4)

    tx = await create_transaction(
        CreateTransactionDTO(
            user_id=user.id,
            credit_account_id=credit_account.id,
            debit_account_id=debit_account.id,
            amount=amount
        )
    )

    assert tx.amount == Decimal(amount).quantize(Decimal('.01'))
    assert tx.debit_account == debit_account.id
    assert tx.credit_account == credit_account.id


@pytest.mark.asyncio
async def test__create_transaction__same_credit_debit_account(
        clean_db,
        container,
        user_account
):
    user, account = user_account
    amount = account.balance * Decimal(0.1)

    with pytest.raises(IncorrectData):
        tx = await create_transaction(
            CreateTransactionDTO(
                user_id=user.id,
                credit_account_id=account.id,
                debit_account_id=account.id,
                amount=amount
            )
        )


@pytest.mark.asyncio
async def test__create_transaction__account_not_found(
        clean_db,
        container,
        user_accounts
):
    user, accounts = user_accounts
    credit_account = accounts[0]
    debit_account = uuid.uuid4()
    amount = credit_account.balance * Decimal(0.1)

    with pytest.raises(EntityNotFoundException):
        tx = await create_transaction(
            CreateTransactionDTO(
                user_id=user.id,
                credit_account_id=credit_account.id,
                debit_account_id=debit_account,
                amount=amount
            )
        )


@pytest.mark.asyncio
async def test__create_transaction__another_user_account__debit(
        clean_db,
        container,
        user_account,
        another_user_account
):
    # will be deleted lately

    user, account = user_account
    _, another_user_account = another_user_account
    amount = account.balance * Decimal(0.1)

    with pytest.raises(EntityNotFoundException):
        tx = await create_transaction(
            CreateTransactionDTO(
                user_id=user.id,
                credit_account_id=account.id,
                debit_account_id=another_user_account.id,
                amount=amount
            )
        )


@pytest.mark.asyncio
async def test__create_transaction__another_user_account__credit(
        clean_db,
        container,
        user_account,
        another_user_account
):
    # will be deleted lately

    user, account = user_account
    _, another_user_account = another_user_account
    amount = another_user_account.balance * Decimal(0.1)

    with pytest.raises(EntityNotFoundException):
        tx = await create_transaction(
            CreateTransactionDTO(
                user_id=user.id,
                credit_account_id=another_user_account.id,
                debit_account_id=account.id,
                amount=amount
            )
        )


@pytest.mark.asyncio
async def test__create_transaction__credit_acc_is_null(
        clean_db,
        container,
        user_account
):
    """
    Income transaction

    :param clean_db:
    :param container:
    :param user_account:
    :return:
    """
    user, account = user_account
    amount = random.uniform(10, 1000)

    tx = await create_transaction(
        CreateTransactionDTO(
            user_id=user.id,
            credit_account_id=None,
            debit_account_id=account.id,
            amount=amount
        )
    )

    assert tx.amount == Decimal(amount).quantize(Decimal('.01'))
    assert tx.debit_account == account.id
    assert tx.credit_account is None


@pytest.mark.asyncio
async def test__create_transaction__debit_acc_is_null(
        clean_db,
        container,
        user_account
):
    """
    Outcome transaction

    :param clean_db:
    :param container:
    :param user_account:
    :return:
    """
    user, account = user_account
    amount = account.balance * Decimal(0.1)

    tx = await create_transaction(
        CreateTransactionDTO(
            user_id=user.id,
            credit_account_id=account.id,
            debit_account_id=None,
            amount=amount
        )
    )

    assert tx.amount == Decimal(amount).quantize(Decimal('.01'))
    assert tx.credit_account == account.id
    assert tx.debit_account is None


@pytest.mark.asyncio
async def test__create_transaction__transfer_tx(
        clean_db,
        container,
        user_accounts
):
    """
    Transfer between user accounts transaction

    :param clean_db:
    :param container:
    :param user_account:
    :return:
    """
    user, accounts = user_accounts
    debit_account = accounts[0]
    credit_account = accounts[1]
    amount = credit_account.balance * Decimal('0.1')

    tx = await create_transaction(
        CreateTransactionDTO(
            user_id=user.id,
            credit_account_id=credit_account.id,
            debit_account_id=debit_account.id,
            amount=amount
        )
    )

    assert tx.amount == Decimal(amount).quantize(Decimal('.01'))
    assert tx.credit_account == credit_account.id
    assert tx.debit_account == debit_account.id


@pytest.mark.asyncio
async def test__create_transaction__both_accounts_is_null(
        clean_db,
        container,
        user_account
):
    """
    Negative case

    :param clean_db:
    :param container:
    :param user_account:
    :return:
    """
    user, account = user_account
    amount = random.uniform(10, 1000)

    with pytest.raises(IncorrectData):
        tx = await create_transaction(
            CreateTransactionDTO(
                user_id=user.id,
                credit_account_id=None,
                debit_account_id=None,
                amount=amount
            )
        )


@pytest.mark.asyncio
async def test__create_transaction__not_enough_money_on_credit_acc(
        clean_db,
        container,
        user_accounts
):
    user, accounts = user_accounts
    credit_account = accounts[0]
    amount = credit_account.balance + Decimal(10.00)

    with pytest.raises(IncorrectData):
        tx = await create_transaction(
            CreateTransactionDTO(
                user_id=user.id,
                credit_account_id=credit_account.id,
                debit_account_id=None,
                amount=amount
            )
        )


#############################################################
# Get Transactions

@pytest_asyncio.fixture
async def user_accounts_transactions(
        clean_db, container,
        user_accounts
):
    user, accounts = user_accounts

    transactions = []
    for i in range(10):
        idxs = random.sample(list(range(0, len(accounts))), k=2)
        credit_account = accounts[idxs[0]]
        debit_account = accounts[idxs[1]]

        amount = credit_account.balance * Decimal(0.1)

        tx = await create_transaction(
            CreateTransactionDTO(
                user_id=user.id,
                credit_account_id=credit_account.id,
                debit_account_id=debit_account.id,
                amount=amount
            )
        )
        transactions.append(tx)

    return user, accounts, transactions


@pytest_asyncio.fixture
async def another_user_transactions(
        clean_db,
        container,
        another_user_accounts
):
    another_user, accounts = another_user_accounts
    transactions = []
    for i in range(10):
        idxs = random.sample(list(range(0, len(accounts))), k=2)
        credit_account = accounts[idxs[0]]
        debit_account = accounts[idxs[1]]

        amount = credit_account.balance * Decimal(0.1)

        tx = await create_transaction(
            CreateTransactionDTO(
                user_id=another_user.id,
                credit_account_id=credit_account.id,
                debit_account_id=debit_account.id,
                amount=amount
            )
        )
        transactions.append(tx)

    return another_user, accounts, transactions


@pytest.mark.asyncio
async def test__get_user_transactions(
        clean_db,
        container,
        user_accounts_transactions,
        another_user_transactions
):
    user, accounts, transactions = user_accounts_transactions
    db_transactions = await get_user_transactions(
        GetUserTransactionsDTO(
            user_id=user.id
        )
    )

    sorted_transactions = sorted(transactions, key=lambda tx: tx.id)
    sorted_db_transactions = sorted(db_transactions, key=lambda tx: tx.id)

    assert len(transactions) == len(db_transactions)
    assert sorted_transactions == sorted_db_transactions


@pytest.mark.asyncio
async def test__get_user_transactions(
        clean_db,
        container,
        user_accounts_transactions,
        another_user_transactions
):
    """
    Test getting account transactions

    :param clean_db:
    :param container:
    :param user_accounts_transactions:
    :param another_user_transactions:
    :return:
    """
    user, accounts, transactions = user_accounts_transactions
    account = accounts[0]
    account_txs_filter = lambda tx: tx.debit_account == account.id or tx.credit_account == account.id
    account_transactions = list(filter(account_txs_filter, transactions))
    sorted_account_txs = sorted(account_transactions, key=lambda tx: tx.id)

    db_account_txs = await get_account_transactions(GetAccountTransactionsDTO(user.id, account.id))
    sorted_db_account_txs = sorted(db_account_txs, key=lambda tx: tx.id)

    assert sorted_account_txs == sorted_db_account_txs


@pytest.mark.asyncio
async def test__get_user_transactions__another_user(
        clean_db,
        container,
        user_accounts_transactions,
        another_user_transactions
):
    """
    Test getting account transactions
    account of another user

    :param clean_db:
    :param container:
    :param user_accounts_transactions:
    :param another_user_transactions:
    :return:
    """
    another_user, _, _ = another_user_transactions
    user, accounts, transactions = user_accounts_transactions
    account = accounts[0]

    with pytest.raises(EntityNotFoundException):
        await get_account_transactions(GetAccountTransactionsDTO(another_user.id, account.id))



