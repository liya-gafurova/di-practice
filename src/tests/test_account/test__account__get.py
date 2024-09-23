import uuid

import pytest

from domain.account.queries import GetAccountByIdDTO, GetAllUserAccountsDTO, GetAccountByNumberDTO
from shared.exceptions import EntityNotFoundException


@pytest.mark.asyncio
async def test__get_account_by_id(clean_db, container, user_account):
    app = container.app()
    user, account = user_account

    db_account = await app.execute(GetAccountByIdDTO(user.id, account.id), container.db_session())

    assert account.id == db_account.id
    assert account.number == db_account.number
    assert account.name == db_account.name
    assert account.owner_id == db_account.owner_id
    assert account.balance == db_account.balance


@pytest.mark.asyncio
async def test__get_account_by_id__another_user_account(clean_db, container, another_user_account, user):
    app = container.app()
    another_user, another_account = another_user_account

    with pytest.raises(EntityNotFoundException):
        await app.execute(GetAccountByIdDTO(user.id, another_account.id), container.db_session())


@pytest.mark.asyncio
async def test__get_account_by_id__no_account_found(clean_db, container, user):
    app = container.app()
    with pytest.raises(EntityNotFoundException):
        await app.execute(GetAccountByIdDTO(user.id, uuid.uuid4()), container.db_session())


@pytest.mark.asyncio
async def test__get_account_by_number__no_account_found(clean_db, container, user):
    app = container.app()
    with pytest.raises(EntityNotFoundException):
        await app.execute(
            GetAccountByNumberDTO(
                user_id=user.id,
                account_number='some_number'
            ),
            container.db_session()
        )


@pytest.mark.asyncio
async def test__get_account_by_number__another_user_account(clean_db, container, user, another_user_account):
    app = container.app()
    _, another_account = another_user_account
    with pytest.raises(EntityNotFoundException):
        await app.execute(GetAccountByNumberDTO(
            user_id=user.id,
            account_number=another_account.number
        ), container.db_session())


@pytest.mark.asyncio
async def test__get_account_by_number(clean_db, container, user_account):
    app = container.app()
    user, account = user_account

    db_account = await app.execute(GetAccountByNumberDTO(
            user_id=user.id,
            account_number=account.number
        ), container.db_session())

    assert db_account == account


@pytest.mark.asyncio
async def test__get_all_user_accounts(clean_db, container, user_accounts):
    app = container.app()
    current_user, accounts = user_accounts
    accounts_sorted = sorted(accounts, key=lambda acc: acc.number)

    db_accounts = await app.execute(GetAllUserAccountsDTO(current_user.id), container.db_session())
    db_accounts_sorted = sorted(db_accounts, key=lambda acc: acc.number)

    assert len(db_accounts_sorted) == len(accounts_sorted)
    assert db_accounts_sorted[0].number == accounts_sorted[0].number
    assert db_accounts_sorted[-1].number == accounts_sorted[-1].number


@pytest.mark.asyncio
async def test__get_all_user_accounts__no_accounts(clean_db, container, user):
    app = container.app()
    db_accounts = await app.execute(GetAllUserAccountsDTO(user.id), container.db_session())
    db_accounts_sorted = sorted(db_accounts, key=lambda acc: acc.number)

    assert len(db_accounts_sorted) == 0
