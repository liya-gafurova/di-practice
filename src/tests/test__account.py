import uuid

import pytest
import pytest_asyncio

from domain.account.commands import create_account, CreateAccountDTO, update_account, UpdateAccountDTO
from domain.account.entities import Account
from domain.user.entities import User
from shared.exceptions import EntityNotFoundException


@pytest_asyncio.fixture
async def user_account(clean_db, container, user):
    session_maker = container.db_session()
    account_repo = container.account_repo()
    account_repo.session = session_maker()

    account = Account(
        id=Account.next_id(),
        name='fixture_account',
        number=Account.generate_number(),
        owner_id=user.id
    )

    await account_repo.add(account)

    return user, account


@pytest_asyncio.fixture
async def another_user(clean_db, container):
    session_maker = container.db_session()
    user_repo = container.user_repo()
    user_repo.session = session_maker()

    user = User(id=User.next_id(), name='Another user name', email='example@test.com')

    await user_repo.add(user)

    return user


@pytest_asyncio.fixture
async def another_user_account(clean_db, container, another_user):
    session_maker = container.db_session()
    account_repo = container.account_repo()
    account_repo.session = session_maker()

    account = Account(
        id=Account.next_id(),
        name='fixture_account__another',
        number=Account.generate_number(),
        owner_id=another_user.id
    )

    await account_repo.add(account)

    return another_user, account


@pytest.mark.asyncio
async def test__create_account__no_user(clean_db, container):
    user_id = uuid.uuid4()
    with pytest.raises(EntityNotFoundException):
        await create_account(CreateAccountDTO(user_id=user_id, name=None))


@pytest.mark.asyncio
async def test__create_account(clean_db, container, user):
    user_id = user.id
    account_name = None
    account = await create_account(CreateAccountDTO(user_id=user_id, name=account_name))

    assert account.owner_id == user.id
    assert account.id is not None
    assert account.number is not None
    assert account.name == account_name


@pytest.mark.asyncio
async def test__update_account(clean_db, container, user_account):
    user, account = user_account
    new_name = 'New Name'
    updated_account = await update_account(UpdateAccountDTO(
        user_id=user.id,
        account_id=account.id,
        name=new_name
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
            account_id=account.id,
            name=new_name
        ))


@pytest.mark.asyncio
async def test__update_account__no_account_found(clean_db, container, user):
    with pytest.raises(EntityNotFoundException):
        await update_account(UpdateAccountDTO(
            user_id=user.id,
            account_id=uuid.uuid4(),
            name='some name of not found account'
        ))


@pytest.mark.asyncio
async def test__update_account__no_update_field(clean_db, container, user_account):
    user, account = user_account
    updated_account = await update_account(UpdateAccountDTO(
        user_id=user.id,
        account_id=account.id,
        name=None
    ))

    assert updated_account.id == account.id
    assert updated_account.name == account.name
    assert updated_account.owner_id == user.id
    assert updated_account.number == account.number
