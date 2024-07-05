from domain.transaction.entities import Transaction
from domain.transaction.repositories import TransactionRepository
from shared.data_mapper import DataMapper, MapperModel, MapperEntity
from shared.repositories import SqlAlchemyRepository
from storage.models import TransactionModel


class TransactionDataMapper(DataMapper):
    def model_to_entity(self, instance: TransactionModel) -> Transaction:
        return Transaction(
            id=instance.id,
            credit_account=instance.credit_account,
            debit_account=instance.debit_account,
            user_id=instance.user_id,
            amount=instance.amount
        )

    def entity_to_model(self, entity: Transaction) -> TransactionModel:
        return TransactionModel(
            id=entity.id,
            credit_account=entity.credit_account,
            debit_account=entity.debit_account,
            user_id=entity.user_id,
            amount=entity.amount
        )


class TransactionSqlAlchemyRepository(TransactionRepository, SqlAlchemyRepository):
    model_class = TransactionModel
    mapper_class = TransactionDataMapper
