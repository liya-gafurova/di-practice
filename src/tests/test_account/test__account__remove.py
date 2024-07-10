import uuid

import pytest

from domain.account.commands import delete_account, DeleteAccountDTO, add_transaction_for_user, AddTransactionDTO
from domain.account.queries import get_account_by_id, GetAccountByIdDTO
from shared.exceptions import EntityNotFoundException, ThisActionIsForbidden


@pytest.mark.asyncio
async def test__account_delete(clean_db, container, user_account):
    user, account = user_account

    await delete_account(DeleteAccountDTO(user.id, account.number))

    with pytest.raises(EntityNotFoundException):
        account = await get_account_by_id(GetAccountByIdDTO(user.id, account.id))
        print(account)


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

    with pytest.raises(ThisActionIsForbidden):
        await delete_account(DeleteAccountDTO(user.id, accounts[0].number))


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
    await add_transaction_for_user(AddTransactionDTO(
        user_id=user.id,
        credit_account=account_to_be_deleted.number,
        debit_account=another_account.number,
        amount=account_to_be_deleted.balance
    ))

    await delete_account(DeleteAccountDTO(user.id, account_to_be_deleted.number))
