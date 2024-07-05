import uuid
from decimal import Decimal

import pytest

from domain.transaction.commands import create_transaction, CreateTransactionDTO
from shared.exceptions import EntityNotFoundException


@pytest.mark.asyncio
async def test__create_transaction(
        clean_db,
        container,
        user_accounts
):
    user, accounts = user_accounts
    credit_account = accounts[0]
    debit_account = accounts[1]
    amount = 156.459

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
async def test__create_transaction__account_not_found(
        clean_db,
        container,
        user_accounts
):
    user, accounts = user_accounts
    credit_account = accounts[0]
    debit_account = uuid.uuid4()
    amount = 156.459

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
    amount = 156.459

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
    amount = 156.459

    with pytest.raises(EntityNotFoundException):
        tx = await create_transaction(
            CreateTransactionDTO(
                user_id=user.id,
                credit_account_id=another_user_account.id,
                debit_account_id=account.id,
                amount=amount
            )
        )