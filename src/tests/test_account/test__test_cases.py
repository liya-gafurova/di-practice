from decimal import Decimal

import pytest

from domain.account.commands import add_transaction_for_user, AddTransactionDTO
from domain.account.queries import GetAccountByIdDTO, get_account_by_id


################
# Add user transactions
# check balance after every added  tx
################

@pytest.mark.asyncio
async def test__create_account_transaction(clean_db, container, user_accounts):
    user, accounts = user_accounts

    # add transfer
    transfer_amount = Decimal(accounts[0].balance * Decimal(0.50)).quantize(Decimal('0.01'))
    user_tx1 = await add_transaction_for_user(
        command=AddTransactionDTO(
            user_id=user.id,
            credit_account_id=accounts[0].id,
            debit_account_id=accounts[1].id,
            amount=transfer_amount
        )
    )

    credited_account = await get_account_by_id(GetAccountByIdDTO(user.id, accounts[0].id))
    debited_account = await get_account_by_id(GetAccountByIdDTO(user.id, accounts[1].id))

    assert credited_account.balance == accounts[0].balance - transfer_amount
    assert debited_account.balance == accounts[1].balance + transfer_amount

    transfer_amount2 = Decimal(accounts[0].balance * Decimal(0.10)).quantize(Decimal('0.01'))
    user_tx2 = await add_transaction_for_user(
        command=AddTransactionDTO(
            user_id=user.id,
            credit_account_id=accounts[0].id,
            debit_account_id=None,
            amount=transfer_amount2
        )
    )

    credited_account = await get_account_by_id(GetAccountByIdDTO(user.id, accounts[0].id))

    assert credited_account.balance == accounts[0].balance - transfer_amount - transfer_amount2
    assert debited_account.balance == accounts[1].balance + transfer_amount






################
# Edit account balance
# check new balance, correction tx
################
