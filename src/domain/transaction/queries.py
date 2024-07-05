import uuid
from dataclasses import dataclass

from dependency_injector.wiring import Provide, inject

from core.dependencies import Container
from domain.transaction.repositories import TransactionRepository


@dataclass
class GetUserTransactionsDTO:
    user_id: uuid.UUID


@inject
async def get_user_transactions(
        query: GetUserTransactionsDTO,
        session_maker=Provide[Container.db_session],
        tx_repo: TransactionRepository = Provide[Container.tx_repo]
):
    tx_repo.session = session_maker()

    user_txs = await tx_repo.get_user_transactions(query.user_id)

    return user_txs
