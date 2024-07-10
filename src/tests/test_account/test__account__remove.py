import uuid
from decimal import Decimal

import pytest

from domain.account.commands import delete_account, DeleteAccountDTO, add_transaction_for_user, AddTransactionDTO
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
    another_user, another_account = another_user_account

    with pytest.raises(EntityNotFoundException):
        await delete_account(DeleteAccountDTO(user.id, another_account.number))


@pytest.mark.asyncio
async def test__account_delete__account_not_exists(
        clean_db,
        container,
        user
):
    with pytest.raises(EntityNotFoundException):
        await delete_account(DeleteAccountDTO(user.id, 'some number'))


@pytest.mark.asyncio
async def test__account_delete__with_txs__not_zero_balance(clean_db, container, user_accounts_transactions):
    """
    Cannot delete account because account.balance != 0
    :param clean_db:
    :param container:
    :param user_accounts_transactions:
    :return:
    """
    user, accounts, txs = user_accounts_transactions
    account = await get_account_by_id(GetAccountByIdDTO(user.id, accounts[0].id))
    # check that account balance is not 0 to perform test
    assert account.balance != Decimal(0.0)

    # perform test
    with pytest.raises(ThisActionIsForbidden):
        await delete_account(DeleteAccountDTO(user.id, accounts[0].number))


async def prepare_account_for_removing(user: User, account_to_be_deleted: Account, another_user_account: Account):
    await add_transaction_for_user(AddTransactionDTO(
        user_id=user.id,
        credit_account=account_to_be_deleted.number,
        debit_account=another_user_account.number,
        amount=account_to_be_deleted.balance
    ))


@pytest.mark.asyncio
async def test__account_delete__with_txs__zero_balance(clean_db, container, user_accounts_transactions):
    """

    :param clean_db:
    :param container:
    :param user_accounts_transactions:
    :return:
    """
    user, accounts, txs = user_accounts_transactions
    another_account = accounts[1]

    # get actual balance value
    account_to_be_deleted = await get_account_by_id(GetAccountByIdDTO(user.id, accounts[0].id))

    # transfer account balance to another user account
    await prepare_account_for_removing(
        user=user,
        account_to_be_deleted=account_to_be_deleted,
        another_user_account=another_account
    )

    await delete_account(DeleteAccountDTO(user.id, account_to_be_deleted.number))
