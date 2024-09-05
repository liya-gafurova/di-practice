import uuid

import pytest

from domain.account.commands import share_account_access, ShareAccountAccessDTO
from domain.account.queries import get_all_user_accounts, GetAllUserAccountsDTO
from shared.exceptions import EntityNotFoundException, IncorrectData


@pytest.mark.asyncio
async def test__account_share(clean_db, container, user_account, another_user):
    user, account = user_account

    db_accounts = await get_all_user_accounts(GetAllUserAccountsDTO(another_user.id))

    shared_account = await share_account_access(ShareAccountAccessDTO(
        account_number=account.number,
        account_owner_id=user.id,
        share_access_with_id=another_user.id
    ))

    db_accounts_after = await get_all_user_accounts(GetAllUserAccountsDTO(another_user.id))

    assert db_accounts + [shared_account] == db_accounts_after


@pytest.mark.asyncio
async def test__account_share__user_not_account_owner(
        clean_db,
        container,
        user_account,
        another_user
):
    user, account = user_account
    with pytest.raises(EntityNotFoundException):
        shared_account = await share_account_access(ShareAccountAccessDTO(
            account_number=account.number,
            account_owner_id=another_user.id,
            share_access_with_id=uuid.uuid4()
        ))


@pytest.mark.asyncio
async def test__account_share__user_already_has_access(
        clean_db,
        container,
        user_account,
        another_user
):
    user, account = user_account

    shared_account = await share_account_access(ShareAccountAccessDTO(
        account_number=account.number,
        account_owner_id=user.id,
        share_access_with_id=another_user.id
    ))

    with pytest.raises(IncorrectData):
        shared_account2 = await share_account_access(ShareAccountAccessDTO(
            account_number=account.number,
            account_owner_id=user.id,
            share_access_with_id=another_user.id
        ))


@pytest.mark.asyncio
async def test__account_share__account_not_found(
        clean_db,
        container,
        user_account,
        another_user
):
    user, account = user_account

    with pytest.raises(EntityNotFoundException):
        shared_account = await share_account_access(ShareAccountAccessDTO(
            account_number='some_number',
            account_owner_id=user.id,
            share_access_with_id=another_user.id
        ))


@pytest.mark.asyncio
async def test__account_share__target_user_not_found(
        clean_db,
        container,
        user_account
):
    user, account = user_account

    with pytest.raises(EntityNotFoundException):
        shared_account = await share_account_access(ShareAccountAccessDTO(
            account_number=account.number,
            account_owner_id=user.id,
            share_access_with_id=uuid.uuid4()
        ))
