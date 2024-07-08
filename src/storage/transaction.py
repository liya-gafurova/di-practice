import uuid

from sqlalchemy import select, and_, or_

from domain.transaction.entities import Transaction
from domain.transaction.repositories import TransactionRepository
from shared.data_mapper import DataMapper
from shared.repositories import SqlAlchemyRepository
from storage.models import TransactionModel, AccountModel


class TransactionDataMapper(DataMapper):
    def model_to_entity(self, instance: TransactionModel) -> Transaction:
        return Transaction(
            id=instance.id,
            credit_account=instance.credit_account,
            debit_account=instance.debit_account,
            user_id=instance.user_id,
            amount=instance.amount,
            type=instance.type
        )

    def entity_to_model(self, entity: Transaction) -> TransactionModel:
        return TransactionModel(
            id=entity.id,
            credit_account=entity.credit_account,
            debit_account=entity.debit_account,
            user_id=entity.user_id,
            amount=entity.amount,
            type=entity.type
        )


class TransactionSqlAlchemyRepository(TransactionRepository, SqlAlchemyRepository):
    model_class = TransactionModel
    mapper_class = TransactionDataMapper

    async def get_user_transactions(self, user_id: uuid.UUID) -> list[Transaction]:
        user_accounts__subquery = select(
            AccountModel.id
        ).where(
            and_(
                AccountModel.owner_id == user_id,
                AccountModel.deleted_at.is_(None)
            )
        )

        stmt = select(TransactionModel).where(
            or_(
                TransactionModel.debit_account.in_(user_accounts__subquery),
                TransactionModel.credit_account.in_(user_accounts__subquery),
            )
        )

        async with self._session:
            instances = (await self._session.scalars(stmt)).all()

        return [self._get_entity(instance) for instance in instances]

