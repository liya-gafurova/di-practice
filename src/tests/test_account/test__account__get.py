import uuid

import pytest

from domain.account.queries import get_account_by_id, GetAccountByIdDTO, get_all_user_accounts, GetAllUserAccountsDTO
from shared.exceptions import EntityNotFoundException


@pytest.mark.asyncio
async def test__get_account_by_id(clean_db, container, user_account):
    user, account = user_account

    db_account = await get_account_by_id(GetAccountByIdDTO(user.id, account.id))

    assert account.id == db_account.id
    assert account.number == db_account.number
    assert account.name == db_account.name
    assert account.owner_id == db_account.owner_id
    assert account.balance == db_account.balance


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
