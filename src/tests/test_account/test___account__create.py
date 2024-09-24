import random
import uuid
from decimal import Decimal

import pytest

from domain.account.commands import CreateAccountDTO
from domain.account.queries import GetAccountByIdDTO
from shared.exceptions import EntityNotFoundException, IncorrectData


@pytest.mark.asyncio
async def test__create_account__no_user(clean_db, container):
    app = container.app()
    user_id = uuid.uuid4()
    with pytest.raises(EntityNotFoundException):
        await app.execute(CreateAccountDTO(user_id=user_id, name=None), container.db_session())


@pytest.mark.asyncio
async def test__create_account__without_balance(clean_db, container, user):
    app = container.app()
    user_id = user.id
    account_name = None
    account = await app.execute(CreateAccountDTO(user_id=user_id, name=account_name), container.db_session())

    assert account.owner_id == user.id
    assert account.id is not None
    assert account.number is not None
    assert account.name == account_name
    assert account.balance == Decimal(0.00)


@pytest.mark.asyncio
async def test__create_account__with_balance(clean_db, container, user):
    app = container.app()
    user_id = user.id
    account_name = None
    balance = random.uniform(10, 1000)
    created_account = await app.execute(CreateAccountDTO(
            user_id=user_id, name=account_name, balance=balance
        ), container.db_session())
    account = await app.execute(GetAccountByIdDTO(user.id, created_account.id), container.db_session())

    assert account.owner_id == user.id
    assert account.id is not None
    assert account.number is not None
    assert account.name == account_name
    assert account.balance == Decimal(balance).quantize(Decimal('0.01'))


@pytest.mark.asyncio
async def test__create_account__with_balance__below_zero(clean_db, container, user):
    app = container.app()
    user_id = user.id
    account_name = None
    balance = random.uniform(10, 1000)

    with pytest.raises(IncorrectData):
        account = await app.execute(
            CreateAccountDTO(
                user_id=user_id, name=account_name, balance=-balance
            ),
            container.db_session()
        )
