import uuid

import pytest

from domain.account.commands import delete_account, DeleteAccountDTO
from domain.account.queries import get_account_by_id, GetAccountByIdDTO
from shared.exceptions import EntityNotFoundException


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
