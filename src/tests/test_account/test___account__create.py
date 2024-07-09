import random
import uuid
from decimal import Decimal

import pytest

from domain.account.commands import create_account, CreateAccountDTO
from domain.account.queries import get_account_by_id, GetAccountByIdDTO
from shared.exceptions import EntityNotFoundException, IncorrectData


@pytest.mark.asyncio
async def test__create_account__no_user(clean_db, container):
    user_id = uuid.uuid4()
    with pytest.raises(EntityNotFoundException):
        await create_account(CreateAccountDTO(user_id=user_id, name=None))


@pytest.mark.asyncio
async def test__create_account__without_balance(clean_db, container, user):
    user_id = user.id
    account_name = None
    account = await create_account(CreateAccountDTO(user_id=user_id, name=account_name))

    assert account.owner_id == user.id
    assert account.id is not None
    assert account.number is not None
    assert account.name == account_name
    assert account.balance == Decimal(0.00)


@pytest.mark.asyncio
async def test__create_account__with_balance(clean_db, container, user):
    user_id = user.id
    account_name = None
    balance = random.uniform(10, 1000)
    created_account = await create_account(
        CreateAccountDTO(
            user_id=user_id, name=account_name, balance=balance
        )
    )
    account = await get_account_by_id(GetAccountByIdDTO(user.id, created_account.id))

    assert account.owner_id == user.id
    assert account.id is not None
    assert account.number is not None
    assert account.name == account_name
    assert account.balance == Decimal(balance).quantize(Decimal('0.01'))


@pytest.mark.asyncio
async def test__create_account__with_balance__below_zero(clean_db, container, user):
    user_id = user.id
    account_name = None
    balance = random.uniform(10, 1000)

    with pytest.raises(IncorrectData):
        account = await create_account(
            CreateAccountDTO(
                user_id=user_id, name=account_name, balance=-balance
            )
        )
