import uuid

import pytest

from domain.account.commands import update_account, UpdateAccountDTO
from shared.exceptions import EntityNotFoundException


@pytest.mark.asyncio
async def test__update_account__name(clean_db, container, user_account):
    user, account = user_account
    new_name = 'New Name'
    updated_account = await update_account(UpdateAccountDTO(
        user_id=user.id,
        account_number=account.number,
        name=new_name,
        balance=None
    ))

    assert updated_account.id == account.id
    assert updated_account.name == new_name
    assert updated_account.owner_id == user.id
    assert updated_account.number == account.number


@pytest.mark.asyncio
async def test__update_account__not_user_account(clean_db, container, another_user_account, user):
    another_user, account = another_user_account
    new_name = 'New Name'

    with pytest.raises(EntityNotFoundException):
        await update_account(UpdateAccountDTO(
            user_id=user.id,
            account_number=account.number,
            name=new_name,
            balance=None
        ))


@pytest.mark.asyncio
async def test__update_account__no_account_found(clean_db, container, user):
    with pytest.raises(EntityNotFoundException):
        await update_account(UpdateAccountDTO(
            user_id=user.id,
            account_number='some number',
            name='some name of not found account',
            balance=None
        ))


@pytest.mark.asyncio
async def test__update_account__no_update_field(clean_db, container, user_account):
    user, account = user_account
    updated_account = await update_account(UpdateAccountDTO(
        user_id=user.id,
        account_number=account.number,
        name=None,
        balance=None
    ))

    assert updated_account.id == account.id
    assert updated_account.name == account.name
    assert updated_account.owner_id == user.id
    assert updated_account.number == account.number
