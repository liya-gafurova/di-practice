import uuid
from decimal import Decimal

import pytest

from domain.account.commands import DeleteAccountDTO, AddTransactionDTO
from domain.account.entities import Account
from domain.account.queries import get_account_by_id, GetAccountByIdDTO
from domain.user.entities import User
from shared.exceptions import EntityNotFoundException, ThisActionIsForbidden


@pytest.mark.asyncio
async def test__account_delete__another_user_account(
        clean_db,
        container,
        another_user_account,
        user
):
    app = container.app()
    another_user, another_account = another_user_account

    with pytest.raises(EntityNotFoundException):
        await app.execute(DeleteAccountDTO(user.id, another_account.number), container.db_session())


@pytest.mark.asyncio
async def test__account_delete__account_not_exists(
        clean_db,
        container,
        user
):
    app = container.app()
    with pytest.raises(EntityNotFoundException):
        await app.execute(DeleteAccountDTO(user.id, 'some number'), container.db_session())


@pytest.mark.asyncio
async def test__account_delete__with_txs__not_zero_balance(clean_db, container, user_accounts_transactions):
    """
    Cannot delete account because account.balance != 0
    :param clean_db:
    :param container:
    :param user_accounts_transactions:
    :return:
    """
    app = container.app()
    user, accounts, txs = user_accounts_transactions
    account = await app.execute(GetAccountByIdDTO(user.id, accounts[0].id), container.db_session())
    # check that account balance is not 0 to perform test
    assert account.balance != Decimal(0.0)

    # perform test
    with pytest.raises(ThisActionIsForbidden):
        await app.execute(DeleteAccountDTO(user.id, accounts[0].number), container.db_session())


async def prepare_account_for_removing(container, user: User, account_to_be_deleted: Account, another_user_account: Account):
    app = container.app()
    await app.execute(AddTransactionDTO(
        user_id=user.id,
        credit_account=account_to_be_deleted.number,
        debit_account=another_user_account.number,
        amount=account_to_be_deleted.balance
    ),container.db_session())


@pytest.mark.asyncio
async def test__account_delete__with_txs__zero_balance(clean_db, container, user_accounts_transactions):
    """

    :param clean_db:
    :param container:
    :param user_accounts_transactions:
    :return:
    """
    app = container.app()
    user, accounts, txs = user_accounts_transactions
    another_account = accounts[1]

    # get actual balance value
    account_to_be_deleted = await app.execute(GetAccountByIdDTO(user.id, accounts[0].id), container.db_session())

    # transfer account balance to another user account
    await prepare_account_for_removing(
        container,
        user=user,
        account_to_be_deleted=account_to_be_deleted,
        another_user_account=another_account
    )

    await app.execute(DeleteAccountDTO(user.id, account_to_be_deleted.number),container.db_session())
