import uuid

import pytest

from domain.account.commands import create_account, CreateAccountDTO, update_account, UpdateAccountDTO, \
    DeleteAccountDTO, delete_account
from domain.account.queries import get_account_by_id, GetAccountByIdDTO, get_all_user_accounts, GetAllUserAccountsDTO
from shared.exceptions import EntityNotFoundException
from tests.conftest import user_accounts, user_account, another_user_account


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
async def test__get_account_by_id(clean_db, container, user_account):
    user, account = user_account

    db_account = await get_account_by_id(GetAccountByIdDTO(user.id, account.id))

    assert account.id == db_account.id
    assert account.number == db_account.number
    assert account.name == db_account.name
    assert account.owner_id == db_account.owner_id


@pytest.mark.asyncio
async def test__get_account_by_id__another_user_account(clean_db, container, another_user_account, user):
    another_user, another_account = another_user_account

    with pytest.raises(EntityNotFoundException):
        await get_account_by_id(GetAccountByIdDTO(user.id, another_account.id))


@pytest.mark.asyncio
async def test__get_account_by_id__no_account_found(clean_db, container, user):
    with pytest.raises(EntityNotFoundException):
        await get_account_by_id(GetAccountByIdDTO(user.id, uuid.uuid4()))


@pytest.mark.asyncio
async def test__get_all_user_accounts(clean_db, container, user_accounts):

    current_user, accounts = user_accounts
    accounts_sorted = sorted(accounts, key=lambda acc: acc.number)

    db_accounts = await get_all_user_accounts(GetAllUserAccountsDTO(current_user.id))
    db_accounts_sorted = sorted(db_accounts, key=lambda acc: acc.number)

    assert len(db_accounts_sorted) == len(accounts_sorted)
    assert db_accounts_sorted[0].number == accounts_sorted[0].number
    assert db_accounts_sorted[-1].number == accounts_sorted[-1].number


@pytest.mark.asyncio
async def test__get_all_user_accounts__no_accounts(clean_db, container, user):

    db_accounts = await get_all_user_accounts(GetAllUserAccountsDTO(user.id))
    db_accounts_sorted = sorted(db_accounts, key=lambda acc: acc.number)

    assert len(db_accounts_sorted) == 0


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
