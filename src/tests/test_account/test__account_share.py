import uuid

import pytest
from click import command

from domain.account.commands import ShareAccountAccessDTO
from domain.account.queries import  GetAllUserAccountsDTO
from shared.exceptions import EntityNotFoundException, IncorrectData


@pytest.mark.asyncio
async def test__account_share(clean_db, container, user_account, another_user):
    app = container.app()
    user, account = user_account

    db_accounts = await app.execute(GetAllUserAccountsDTO(another_user.id), container.db_session())

    shared_account = await app.execute(ShareAccountAccessDTO(
        account_number=account.number,
        account_owner_id=user.id,
        share_access_with_id=another_user.id
    ), container.db_session())

    db_accounts_after = await app.execute(GetAllUserAccountsDTO(another_user.id), container.db_session())

    assert db_accounts + [shared_account] == db_accounts_after


@pytest.mark.asyncio
async def test__account_share__user_not_account_owner(
        clean_db,
        container,
        user_account,
        another_user
):
    app = container.app()
    user, account = user_account
    with pytest.raises(EntityNotFoundException):
        shared_account = await app.execute(ShareAccountAccessDTO(
            account_number=account.number,
            account_owner_id=another_user.id,
            share_access_with_id=uuid.uuid4()
        ), container.db_session())


@pytest.mark.asyncio
async def test__account_share__user_already_has_access(
        clean_db,
        container,
        user_account,
        another_user
):
    app = container.app()
    user, account = user_account

    shared_account = await app.execute(ShareAccountAccessDTO(
        account_number=account.number,
        account_owner_id=user.id,
        share_access_with_id=another_user.id
    ), container.db_session())

    with pytest.raises(IncorrectData):
        shared_account2 = await app.execute(ShareAccountAccessDTO(
            account_number=account.number,
            account_owner_id=user.id,
            share_access_with_id=another_user.id
        ), container.db_session())


@pytest.mark.asyncio
async def test__account_share__account_not_found(
        clean_db,
        container,
        user_account,
        another_user
):
    app = container.app()
    user, account = user_account

    with pytest.raises(EntityNotFoundException):
        shared_account = await app.execute(ShareAccountAccessDTO(
            account_number='some_number',
            account_owner_id=user.id,
            share_access_with_id=another_user.id
        ), container.db_session())


@pytest.mark.asyncio
async def test__account_share__target_user_not_found(
        clean_db,
        container,
        user_account
):
    app = container.app()
    user, account = user_account

    with pytest.raises(EntityNotFoundException):
        shared_account = await app.execute(ShareAccountAccessDTO(
            account_number=account.number,
            account_owner_id=user.id,
            share_access_with_id=uuid.uuid4()
        ), container.db_session())
