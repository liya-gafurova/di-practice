import uuid

import pytest

from domain.account.commands import delete_account, DeleteAccountDTO, add_transaction_for_user, AddTransactionDTO
from domain.account.queries import get_account_by_id, GetAccountByIdDTO
from shared.exceptions import EntityNotFoundException, ThisActionIsForbidden


@pytest.mark.asyncio
async def test__account_delete(clean_db, container, user_account):
    user, account = user_account

    await delete_account(DeleteAccountDTO(user.id, account.id))

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
        await delete_account(DeleteAccountDTO(user.id, another_account.id))


@pytest.mark.asyncio
async def test__account_delete__account_not_exists(
        clean_db,
        container,
        user
):
    with pytest.raises(EntityNotFoundException):
        await delete_account(DeleteAccountDTO(user.id, uuid.uuid4()))


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
        await delete_account(DeleteAccountDTO(user.id, accounts[0].id))


@pytest.mark.asyncio
async def test__account_delete__with_txs__zero_balance(clean_db, container, user_accounts_transactions):
    """

    :param clean_db:
    :param container:
    :param user_accounts_transactions:
    :return:
    """
    user, accounts, txs = user_accounts_transactions
    account_to_be_deleted = accounts[0]
    another_account = accounts[1]

    account_to_be_deleted = await get_account_by_id(GetAccountByIdDTO(user.id, account_to_be_deleted.id))
    account_to_be_deleted__balance = account_to_be_deleted.balance

    # transfer account balance to another user account
    await add_transaction_for_user(AddTransactionDTO(
        user_id=user.id,
        credit_account_id=account_to_be_deleted.id,
        debit_account_id=another_account.id,
        amount=account_to_be_deleted__balance
    ))

    await delete_account(DeleteAccountDTO(user.id, account_to_be_deleted.id))
