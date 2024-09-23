import random
import uuid
from decimal import Decimal

import pytest

from domain.transaction.commands import CreateTransactionDTO
from domain.transaction.queries import GetUserTransactionsDTO, GetAccountTransactionsDTO
from shared.exceptions import EntityNotFoundException, IncorrectData
from tests.conftest import user_accounts_transactions, another_user_transactions


@pytest.mark.skip('Duplicate of test "test__create_transaction__transfer_tx"')
@pytest.mark.asyncio
async def test__create_transaction(
        clean_db,
        container,
        user_accounts
):
    app = container.app()
    user, accounts = user_accounts
    credit_account = accounts[0]
    debit_account = accounts[1]
    amount = credit_account.balance * Decimal(0.4)

    tx = await app.execute(
        CreateTransactionDTO(
            user_id=user.id,
            credit_account=credit_account.number,
            debit_account=debit_account.number,
            amount=amount
        ),
        container.db_session()
    )

    assert tx.amount == Decimal(amount).quantize(Decimal('.01'))
    assert tx.debit_account == debit_account.number
    assert tx.credit_account == credit_account.number


@pytest.mark.asyncio
async def test__create_transaction__same_credit_debit_account(
        clean_db,
        container,
        user_account
):
    app = container.app()
    user, account = user_account
    amount = account.balance * Decimal(0.1)

    with pytest.raises(IncorrectData):
        tx = await app.execute(
            CreateTransactionDTO(
                user_id=user.id,
                credit_account=account.number,
                debit_account=account.number,
                amount=amount
            ),
            container.db_session()
        )


@pytest.mark.asyncio
async def test__create_transaction__account_not_found(
        clean_db,
        container,
        user_accounts
):
    app = container.app()
    user, accounts = user_accounts
    credit_account = accounts[0]
    debit_account = uuid.uuid4()
    amount = credit_account.balance * Decimal(0.1)

    with pytest.raises(EntityNotFoundException):
        tx = await app.execute(
            CreateTransactionDTO(
                user_id=user.id,
                credit_account=credit_account.number,
                debit_account='some number',
                amount=amount
            ),
            container.db_session()
        )


@pytest.mark.asyncio
async def test__create_transaction__another_user_account__debit(
        clean_db,
        container,
        user_account,
        another_user_account
):
    app = container.app()
    # will be deleted lately

    user, account = user_account
    _, another_user_account = another_user_account
    amount = account.balance * Decimal(0.1)

    with pytest.raises(EntityNotFoundException):
        tx = await app.execute(
            CreateTransactionDTO(
                user_id=user.id,
                credit_account=account.number,
                debit_account=another_user_account.number,
                amount=amount
            ),
            container.db_session()
        )


@pytest.mark.asyncio
async def test__create_transaction__another_user_account__credit(
        clean_db,
        container,
        user_account,
        another_user_account
):
    app = container.app()
    # will be deleted lately

    user, account = user_account
    _, another_user_account = another_user_account
    amount = another_user_account.balance * Decimal(0.1)

    with pytest.raises(EntityNotFoundException):
        tx = await app.execute(
            CreateTransactionDTO(
                user_id=user.id,
                credit_account=another_user_account.number,
                debit_account=account.number,
                amount=amount
            ),
            container.db_session()
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
    app = container.app()
    user, account = user_account
    amount = random.uniform(10, 1000)

    tx = await app.execute(CreateTransactionDTO(
            user_id=user.id,
            credit_account=None,
            debit_account=account.number,
            amount=amount
        ),
        container.db_session()
    )

    assert tx.amount == Decimal(amount).quantize(Decimal('.01'))
    assert tx.debit_account == account.number
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
    app = container.app()
    user, account = user_account
    amount = account.balance * Decimal(0.1)

    tx = await app.execute(
        CreateTransactionDTO(
            user_id=user.id,
            credit_account=account.number,
            debit_account=None,
            amount=amount
        ),
        container.db_session()
    )

    assert tx.amount == Decimal(amount).quantize(Decimal('.01'))
    assert tx.credit_account == account.number
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
    app = container.app()
    user, accounts = user_accounts
    debit_account = accounts[0]
    credit_account = accounts[1]
    amount = credit_account.balance * Decimal('0.1')

    tx = await app.execute(
        CreateTransactionDTO(
            user_id=user.id,
            credit_account=credit_account.number,
            debit_account=debit_account.number,
            amount=amount
        ),
        container.db_session()
    )

    assert tx.amount == Decimal(amount).quantize(Decimal('.01'))
    assert tx.credit_account == credit_account.number
    assert tx.debit_account == debit_account.number


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
    app = container.app()
    user, account = user_account
    amount = random.uniform(10, 1000)

    with pytest.raises(IncorrectData):
        tx = await app.execute(
            CreateTransactionDTO(
                user_id=user.id,
                credit_account=None,
                debit_account=None,
                amount=amount
            ),
            container.db_session()
        )


@pytest.mark.asyncio
async def test__create_transaction__not_enough_money_on_credit_acc(
        clean_db,
        container,
        user_accounts
):
    app = container.app()
    user, accounts = user_accounts
    credit_account = accounts[0]
    amount = credit_account.balance + Decimal(10.00)

    with pytest.raises(IncorrectData):
        tx = await app.execute(
            CreateTransactionDTO(
                user_id=user.id,
                credit_account=credit_account.number,
                debit_account=None,
                amount=amount
            ),
            container.db_session()
        )


@pytest.mark.asyncio
async def test__create_transaction__with_category_id(
        clean_db,
        container,
        user_accounts,
        existing_custom_category,
        existing_general_category
):
    app = container.app()
    user, accounts = user_accounts
    debit_account = accounts[0]
    amount = Decimal(10.00)

    tx = await app.execute(
        CreateTransactionDTO(
            user_id=user.id,
            credit_account=None,
            debit_account=debit_account.number,
            amount=amount,
            category_id=existing_general_category.id
        ),
        container.db_session()
    )

    user_txs = await app.execute(
        GetUserTransactionsDTO(
            user_id=user.id
        ),
        container.db_session()
    )
    last_tx = user_txs[0]

    assert last_tx.category_id == existing_general_category.id
    assert last_tx.user_id == user.id
    assert last_tx.debit_account == debit_account.number
    assert last_tx.amount == amount


@pytest.mark.asyncio
async def test__create_transaction__with_category_id__category_id_does_not_exists(
        clean_db,
        container,
        user_accounts,
        existing_custom_category,
        existing_general_category
):
    app = container.app()
    user, accounts = user_accounts
    debit_account = accounts[0]
    amount = Decimal(10.00)

    with pytest.raises(EntityNotFoundException):
        tx = await app.execute(
            CreateTransactionDTO(
                user_id=user.id,
                credit_account=None,
                debit_account=debit_account.number,
                amount=amount,
                category_id=uuid.uuid4()
            ),
            container.db_session()
        )


@pytest.mark.asyncio
async def test__create_transaction__with_category_id__category_id_of_another_user(
        clean_db,
        container,
        user_accounts,
        existing_custom_category__another_user,
):
    app = container.app()
    user, accounts = user_accounts
    debit_account = accounts[0]
    amount = Decimal(10.00)

    with pytest.raises(EntityNotFoundException):
        tx = await app.execute(
            CreateTransactionDTO(
                user_id=user.id,
                credit_account=None,
                debit_account=debit_account.number,
                amount=amount,
                category_id=existing_custom_category__another_user.id
            ),
            container.db_session()
        )


#############################################################
# Get Transactions


@pytest.mark.asyncio
async def test__get_user_transactions(
        clean_db,
        container,
        user_accounts_transactions,
        another_user_transactions
):
    app = container.app()
    user, accounts, transactions = user_accounts_transactions
    db_transactions = await app.execute(
        GetUserTransactionsDTO(
            user_id=user.id
        ),
        container.db_session()
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
    app = container.app()
    user, accounts, transactions = user_accounts_transactions
    account = accounts[0]
    account_txs_filter = lambda tx: tx.debit_account == account.number or tx.credit_account == account.number
    account_transactions = list(filter(account_txs_filter, transactions))
    sorted_account_txs = sorted(account_transactions, key=lambda tx: tx.id)

    db_account_txs = await app.execute(GetAccountTransactionsDTO(user.id, account.number), container.db_session())
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
    app = container.app()
    another_user, _, _ = another_user_transactions
    user, accounts, transactions = user_accounts_transactions
    account = accounts[0]

    with pytest.raises(EntityNotFoundException):
        await app.execute(GetAccountTransactionsDTO(another_user.id, account.number), container.db_session())



