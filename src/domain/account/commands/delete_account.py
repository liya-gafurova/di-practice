import uuid
from dataclasses import dataclass
from decimal import Decimal

from dependency_injector.wiring import inject, Provide
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import Container
from domain.account.entities import AccountNumber
from domain.account.repositories import AccountRepository
from shared.exceptions import EntityNotFoundException, ThisActionIsForbidden
from shared.interfaces import Command


@dataclass
class DeleteAccountDTO(Command):
    user_id: uuid.UUID
    account_number: AccountNumber


@inject
async def delete_account(
        command: DeleteAccountDTO,
        session: AsyncSession,
        account_repo:AccountRepository=Provide[Container.account_repo],
):
    account_repo.session = session

    account = await account_repo.get_by_number(command.account_number, command.user_id)

    if account.balance != Decimal(0.00):
        raise ThisActionIsForbidden(f'Balance is {account.balance}. Transfer all account balance to other accounts.')

    await account_repo.remove(account)

    return account


"""
check account balance
if balance = 0.0, can delete account
delete account
all tx are referenced to account.number so txs are staing in system
"""