from decimal import Decimal

import pytest

from domain.account.commands import AddTransactionDTO, UpdateAccountDTO, CreateAccountDTO, DeleteAccountDTO, ShareAccountAccessDTO
from domain.account.queries import GetAccountByIdDTO, GetAllUserAccountsDTO
from domain.transaction.queries import GetAccountTransactionsDTO, GetUserTransactionsDTO
from shared.exceptions import IncorrectData, EntityNotFoundException
from tests.test_account.test__account__remove import prepare_account_for_removing


################
# Add user transactions
# check balance after every added  tx
################

@pytest.mark.asyncio
async def test__create_account_transactions(
        clean_db,
        container,
        user_accounts,
        existing_custom_category,
        existing_general_category
):
    app = container.app()
    user, accounts = user_accounts

    # add transfer
    transfer_amount = Decimal(accounts[0].balance * Decimal(0.50)).quantize(Decimal('0.01'))
    user_tx1 = await app.execute(
        AddTransactionDTO(
            user_id=user.id,
            credit_account=accounts[0].number,
            debit_account=accounts[1].number,
            amount=transfer_amount,
            category_id=existing_general_category.id
        ),
        container.db_session()
    )

    credited_account = await app.execute(GetAccountByIdDTO(user.id, accounts[0].id), container.db_session())
    debited_account = await app.execute(GetAccountByIdDTO(user.id, accounts[1].id), container.db_session())

    assert credited_account.balance == accounts[0].balance - transfer_amount
    assert debited_account.balance == accounts[1].balance + transfer_amount

    credit_acc_amount2 = Decimal(accounts[0].balance * Decimal(0.10)).quantize(Decimal('0.01'))
    user_tx2 = await app.execute(
        AddTransactionDTO(
            user_id=user.id,
            credit_account=accounts[0].number,
            debit_account=None,
            amount=credit_acc_amount2
        ),
        container.db_session()
    )

    credited_account = await app.execute(GetAccountByIdDTO(user.id, accounts[0].id), container.db_session())

    assert credited_account.balance == accounts[0].balance - transfer_amount - credit_acc_amount2
    assert debited_account.balance == accounts[1].balance + transfer_amount

    debit_acc_amount3 = Decimal(accounts[0].balance * Decimal(0.20)).quantize(Decimal('0.01'))
    user_tx3 = await app.execute(
        AddTransactionDTO(
            user_id=user.id,
            credit_account=None,
            debit_account=accounts[0].number,
            amount=debit_acc_amount3,
            category_id=existing_custom_category.id
        ),
        container.db_session()
    )
    credited_account = await app.execute(GetAccountByIdDTO(user.id, accounts[0].id), container.db_session())

    assert credited_account.balance == accounts[0].balance - transfer_amount - credit_acc_amount2 + debit_acc_amount3
    assert debited_account.balance == accounts[1].balance + transfer_amount

    txs = await app.execute(GetUserTransactionsDTO(user.id), container.db_session())

    assert txs[0].category_id == existing_custom_category.id


################
# Edit account balance
# check new balance, correction tx
################

@pytest.mark.asyncio
async def test__add_correction_transaction__create_account__with_balance(
        clean_db,
        container,
        user_accounts
):
    app = container.app()
    # create account
    user, accounts = user_accounts
    balance = Decimal('10564.45')
    new_account = await app.execute(CreateAccountDTO(user_id=user.id, name='personal', balance=balance), container.db_session())

    created_account_txs = await app.execute(GetAccountTransactionsDTO(user_id=user.id, account_number=new_account.number), container.db_session())
    created_account = await app.execute(GetAccountByIdDTO(user_id=user.id, account_id=new_account.id), container.db_session())
    all_user_accounts = await app.execute(GetAllUserAccountsDTO(user.id), container.db_session())

    assert created_account.balance == balance
    # correction tx are filtered out
    assert len(created_account_txs) == 0
    assert len(all_user_accounts) == len(accounts) + 1


@pytest.mark.asyncio
async def test__add_correction_transaction__create_account__with_zero_balance(
        clean_db,
        container,
        user_accounts
):
    app = container.app()
    # create account
    user, accounts = user_accounts
    new_account = await app.execute(CreateAccountDTO(user_id=user.id, name='personal'), container.db_session())

    created_account_txs = await app.execute(GetAccountTransactionsDTO(user_id=user.id, account_number=new_account.number), container.db_session())
    created_account = await app.execute(GetAccountByIdDTO(user_id=user.id, account_id=new_account.id), container.db_session())
    all_user_accounts = await app.execute(GetAllUserAccountsDTO(user.id), container.db_session())

    assert created_account.balance == Decimal(0.00)
    assert len(created_account_txs) == 0
    assert len(all_user_accounts) == len(accounts) + 1


@pytest.mark.asyncio
async def test__add_correction_transaction__update_balance__below_zero(
        clean_db,
        container,
        user_accounts
):
    app = container.app()
    # update account balance
    # new balance below zero

    user, accounts = user_accounts
    with pytest.raises(IncorrectData):
        updated_account = await app.execute(
            UpdateAccountDTO(
                user.id,
                accounts[0].number,
                name='New name',
                balance=Decimal(-15).quantize(Decimal('0.01'))
            ),
            container.db_session()
        )


@pytest.mark.asyncio
async def test__add_correction_transaction__update_balance__equals_current_balance(
        clean_db,
        container,
        user_accounts
):
    app = container.app()
    # update account balance
    # new balance equals current balance
    user, accounts = user_accounts
    account_balance = accounts[0].balance
    account_txs__before = await app.execute(GetAccountTransactionsDTO(user.id, accounts[0].number),container.db_session())
    sorted__account_txs__before = sorted(account_txs__before, key=lambda tx: tx.id)

    await app.execute(
        UpdateAccountDTO(
            user.id,
            accounts[0].number,
            name='New name',
            balance=account_balance
        ),
        container.db_session()
    )

    updated_account = await app.execute(GetAccountByIdDTO(user.id, accounts[0].id), container.db_session())
    account_txs__after = await app.execute(GetAccountTransactionsDTO(user.id, accounts[0].number), container.db_session())
    sorted__account_txs__after = sorted(account_txs__after, key=lambda tx: tx.id)

    assert updated_account.balance == accounts[0].balance
    assert sorted__account_txs__after == sorted__account_txs__before


@pytest.mark.asyncio
async def test__add_correction_transaction__update_balance(
        clean_db,
        container,
        user_accounts
):
    app = container.app()
    # update account balance
    # correction tx added, balance updated
    user, accounts = user_accounts
    account_balance = accounts[0].balance
    account_txs__before = await app.execute(GetAccountTransactionsDTO(user.id, accounts[0].number), container.db_session())
    sorted__account_txs__before = sorted(account_txs__before, key=lambda tx: tx.id)

    balance_delta = Decimal(10.00)
    await app.execute(
        UpdateAccountDTO(
            user.id,
            accounts[0].number,
            name='New name',
            balance=account_balance + balance_delta
        ),
        container.db_session()
    )

    updated_account = await app.execute(GetAccountByIdDTO(user.id, accounts[0].id), container.db_session())
    account_txs__after = await app.execute(GetAccountTransactionsDTO(user.id, accounts[0].number), container.db_session())
    sorted__account_txs__after = sorted(account_txs__after, key=lambda tx: tx.id)

    assert updated_account.balance == accounts[0].balance + balance_delta
    # correction tx are filtered out
    assert len(sorted__account_txs__after) == len(sorted__account_txs__before)


@pytest.mark.asyncio
async def test__account_delete(
        clean_db,
        container,
        user_accounts_transactions,
        another_user_transactions
):
    app = container.app()
    user, accounts, txs = user_accounts_transactions

    account = await app.execute(GetAccountByIdDTO(user.id, accounts[0].id), container.db_session())
    if account.balance != Decimal(0.0):

        # transfer account balance to another user account
        await prepare_account_for_removing(
            container,
            user=user,
            account_to_be_deleted=account,
            another_user_account=accounts[1]
        )

    user_txs__before = await app.execute(GetUserTransactionsDTO(user.id), container.db_session())

    # perform removing
    await app.execute(DeleteAccountDTO(user.id, account.number), container.db_session())

    user_txs__after = await app.execute(GetUserTransactionsDTO(user.id), container.db_session())
    user_txs__before__filtered = list(filter(lambda tx: not(tx.debit_account is None and tx.credit_account == account.number or tx.credit_account is None and tx.debit_account == account.number), user_txs__before))
    assert user_txs__before__filtered == user_txs__after

    with pytest.raises(EntityNotFoundException):
        await app.execute(GetAccountByIdDTO(user.id, account.id), container.db_session())


################
# Share account
# check new account user sees transactions added previously
################

@pytest.mark.asyncio
async def test__account_share(
        clean_db,
        container,
        user_accounts_transactions,
        another_user_transactions
):
    app = container.app()
    user, accounts, txs = user_accounts_transactions
    _user, _accounts, _txs = another_user_transactions
    shared_account = accounts[0]

    assert shared_account not in _accounts

    shared_account = await app.execute(ShareAccountAccessDTO(
        account_number=shared_account.number,
        account_owner_id=user.id,
        share_access_with_id=_user.id
    ), container.db_session())

    db_accounts_after = await app.execute(GetAllUserAccountsDTO(_user.id), container.db_session())

    assert shared_account in db_accounts_after

    amount = Decimal(shared_account.balance * Decimal(0.20)).quantize(Decimal('0.01'))
    nex_tx = await app.execute(
        AddTransactionDTO(
            user_id=user.id,
            credit_account=None,
            debit_account=shared_account.number,
            amount=amount,
        ),
        container.db_session()
    )

    user_txs = await app.execute(GetUserTransactionsDTO(user.id), container.db_session())
    _user_txs = await app.execute(GetUserTransactionsDTO(_user.id), container.db_session())

    assert user_txs[0].id == _user_txs[0].id

