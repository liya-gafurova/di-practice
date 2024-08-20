from decimal import Decimal

import pytest

from domain.account.commands import add_transaction_for_user, AddTransactionDTO, update_account, UpdateAccountDTO, \
    create_account, CreateAccountDTO, delete_account, DeleteAccountDTO
from domain.account.queries import GetAccountByIdDTO, get_account_by_id, GetAllUserAccountsDTO, get_all_user_accounts
from domain.transaction.entities import TransactionType
from domain.transaction.queries import get_account_transactions, GetAccountTransactionsDTO, GetUserTransactionsDTO, \
    get_user_transactions
from shared.exceptions import IncorrectData, EntityNotFoundException
from tests.test_account.test__account__remove import prepare_account_for_removing


################
# Add user transactions
# check balance after every added  tx
################

@pytest.mark.asyncio
async def test__create_account_transactions(clean_db, container, user_accounts):
    user, accounts = user_accounts

    # add transfer
    transfer_amount = Decimal(accounts[0].balance * Decimal(0.50)).quantize(Decimal('0.01'))
    user_tx1 = await add_transaction_for_user(
        command=AddTransactionDTO(
            user_id=user.id,
            credit_account=accounts[0].number,
            debit_account=accounts[1].number,
            amount=transfer_amount
        )
    )

    credited_account = await get_account_by_id(GetAccountByIdDTO(user.id, accounts[0].id))
    debited_account = await get_account_by_id(GetAccountByIdDTO(user.id, accounts[1].id))

    assert credited_account.balance == accounts[0].balance - transfer_amount
    assert debited_account.balance == accounts[1].balance + transfer_amount

    credit_acc_amount2 = Decimal(accounts[0].balance * Decimal(0.10)).quantize(Decimal('0.01'))
    user_tx2 = await add_transaction_for_user(
        command=AddTransactionDTO(
            user_id=user.id,
            credit_account=accounts[0].number,
            debit_account=None,
            amount=credit_acc_amount2
        )
    )

    credited_account = await get_account_by_id(GetAccountByIdDTO(user.id, accounts[0].id))

    assert credited_account.balance == accounts[0].balance - transfer_amount - credit_acc_amount2
    assert debited_account.balance == accounts[1].balance + transfer_amount

    debit_acc_amount3 = Decimal(accounts[0].balance * Decimal(0.20)).quantize(Decimal('0.01'))
    user_tx3 = await add_transaction_for_user(
        command=AddTransactionDTO(
            user_id=user.id,
            credit_account=None,
            debit_account=accounts[0].number,
            amount=debit_acc_amount3
        )
    )
    credited_account = await get_account_by_id(GetAccountByIdDTO(user.id, accounts[0].id))

    assert credited_account.balance == accounts[0].balance - transfer_amount - credit_acc_amount2 + debit_acc_amount3
    assert debited_account.balance == accounts[1].balance + transfer_amount


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
    # create account
    user, accounts = user_accounts
    balance = Decimal('10564.45')
    new_account = await create_account(CreateAccountDTO(user_id=user.id, name='personal', balance=balance))

    created_account_txs = await get_account_transactions(GetAccountTransactionsDTO(user_id=user.id, account_number=new_account.number))
    created_account = await get_account_by_id(GetAccountByIdDTO(user_id=user.id, account_id=new_account.id))
    all_user_accounts = await get_all_user_accounts(GetAllUserAccountsDTO(user.id))

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
    # create account
    user, accounts = user_accounts
    new_account = await create_account(CreateAccountDTO(user_id=user.id, name='personal'))

    created_account_txs = await get_account_transactions(GetAccountTransactionsDTO(user_id=user.id, account_number=new_account.number))
    created_account = await get_account_by_id(GetAccountByIdDTO(user_id=user.id, account_id=new_account.id))
    all_user_accounts = await get_all_user_accounts(GetAllUserAccountsDTO(user.id))

    assert created_account.balance == Decimal(0.00)
    assert len(created_account_txs) == 0
    assert len(all_user_accounts) == len(accounts) + 1


@pytest.mark.asyncio
async def test__add_correction_transaction__update_balance__below_zero(
        clean_db,
        container,
        user_accounts
):
    # update account balance
    # new balance below zero

    user, accounts = user_accounts
    with pytest.raises(IncorrectData):
        updated_account = await update_account(
            UpdateAccountDTO(
                user.id,
                accounts[0].number,
                name='New name',
                balance=Decimal(-15).quantize(Decimal('0.01'))
            )
        )


@pytest.mark.asyncio
async def test__add_correction_transaction__update_balance__equals_current_balance(
        clean_db,
        container,
        user_accounts
):
    # update account balance
    # new balance equals current balance
    user, accounts = user_accounts
    account_balance = accounts[0].balance
    account_txs__before = await get_account_transactions(GetAccountTransactionsDTO(user.id, accounts[0].number))
    sorted__account_txs__before = sorted(account_txs__before, key=lambda tx: tx.id)

    await update_account(
        UpdateAccountDTO(
            user.id,
            accounts[0].number,
            name='New name',
            balance=account_balance
        )
    )

    updated_account = await get_account_by_id(GetAccountByIdDTO(user.id, accounts[0].id))
    account_txs__after = await get_account_transactions(GetAccountTransactionsDTO(user.id, accounts[0].number))
    sorted__account_txs__after = sorted(account_txs__after, key=lambda tx: tx.id)

    assert updated_account.balance == accounts[0].balance
    assert sorted__account_txs__after == sorted__account_txs__before


@pytest.mark.asyncio
async def test__add_correction_transaction__update_balance(
        clean_db,
        container,
        user_accounts
):
    # update account balance
    # correction tx added, balance updated
    user, accounts = user_accounts
    account_balance = accounts[0].balance
    account_txs__before = await get_account_transactions(GetAccountTransactionsDTO(user.id, accounts[0].number))
    sorted__account_txs__before = sorted(account_txs__before, key=lambda tx: tx.id)

    balance_delta = Decimal(10.00)
    await update_account(
        UpdateAccountDTO(
            user.id,
            accounts[0].number,
            name='New name',
            balance=account_balance + balance_delta
        )
    )

    updated_account = await get_account_by_id(GetAccountByIdDTO(user.id, accounts[0].id))
    account_txs__after = await get_account_transactions(GetAccountTransactionsDTO(user.id, accounts[0].number))
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
    user, accounts, txs = user_accounts_transactions

    account = await get_account_by_id(GetAccountByIdDTO(user.id, accounts[0].id))
    if account.balance != Decimal(0.0):

        # transfer account balance to another user account
        await prepare_account_for_removing(
            user=user,
            account_to_be_deleted=account,
            another_user_account=accounts[1]
        )

    user_txs__before = await get_user_transactions(GetUserTransactionsDTO(user.id))

    # perform removing
    await delete_account(DeleteAccountDTO(user.id, account.number))

    user_txs__after = await get_user_transactions(GetUserTransactionsDTO(user.id))
    user_txs__before__filtered = list(filter(lambda tx: not(tx.debit_account is None and tx.credit_account == account.number or tx.credit_account is None and tx.debit_account == account.number), user_txs__before))
    assert user_txs__before__filtered == user_txs__after

    with pytest.raises(EntityNotFoundException):
        await get_account_by_id(GetAccountByIdDTO(user.id, account.id))