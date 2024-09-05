import uuid
from unicodedata import category

from sqlalchemy import select, and_, or_

from domain.account.entities import AccountNumber
from domain.category.entities import Category
from domain.transaction.entities import Transaction, TransactionType
from domain.transaction.repositories import TransactionRepository
from shared.data_mapper import DataMapper
from shared.repositories import SqlAlchemyRepository
from storage.models import TransactionModel, AccountModel, AccountAccessModel


class TransactionDataMapper(DataMapper):
    def model_to_entity(self, instance: TransactionModel) -> Transaction:
        return Transaction(
            id=instance.id,
            credit_account=instance.credit_account,
            debit_account=instance.debit_account,
            user_id=instance.user_id,
            amount=instance.amount,
            type=instance.type,
            category_id=instance.category_id,
            category=Category(
                id=instance.category_id,
                name=instance.category.name,
                user_id=instance.category.user_id)
            if instance.category else None
        )

    def entity_to_model(self, entity: Transaction) -> TransactionModel:
        return TransactionModel(
            id=entity.id,
            credit_account=entity.credit_account,
            debit_account=entity.debit_account,
            user_id=entity.user_id,
            amount=entity.amount,
            type=entity.type,
            category_id=entity.category_id
        )


class TransactionSqlAlchemyRepository(TransactionRepository, SqlAlchemyRepository):
    model_class = TransactionModel
    mapper_class = TransactionDataMapper


    async def get_user_transactions(self, user_id: uuid.UUID) -> list[Transaction]:
        user_accounts__subquery = select(
            AccountModel.number
        ).join(
            AccountAccessModel,
            and_(
                AccountModel.id == AccountAccessModel.account_id,
                AccountAccessModel.user_id == user_id
            )
        ).where(
            and_(
                AccountModel.deleted_at.is_(None)
            )
        )

        stmt = select(TransactionModel).where(
            or_(
                TransactionModel.debit_account.in_(user_accounts__subquery),
                TransactionModel.credit_account.in_(user_accounts__subquery),
            )
        ).where(
            TransactionModel.type != TransactionType.CORRECTION.value
        ).order_by(
            TransactionModel.created_at.desc()
        )

        async with self._session:
            instances = (await self._session.scalars(stmt)).all()

        return [self._get_entity(instance) for instance in instances]

    async def get_account_transactions(self, account_number: AccountNumber) -> list[Transaction]:
        stmt = select(TransactionModel).where(
            and_(
                or_(
                    TransactionModel.debit_account == account_number,
                    TransactionModel.credit_account == account_number
                ),
                TransactionModel.type != TransactionType.CORRECTION.value
            )
        ).order_by(
            TransactionModel.created_at.desc()
        )

        async with self._session:
            instances = (await self._session.scalars(stmt)).all()

        return [self._get_entity(instance) for instance in instances]

