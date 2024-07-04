import uuid

from sqlalchemy import select

from domain.account.entities import Account
from domain.account.repositories import AccountRepository
from shared.data_mapper import DataMapper, MapperModel, MapperEntity
from shared.repositories import SqlAlchemyRepository
from storage.models import AccountModel


class AccountDataMapper(DataMapper):
    def model_to_entity(self, instance: AccountModel) -> Account:
        return Account(
            id=instance.id,
            name=instance.name,
            owner_id=instance.owner_id,
            number=instance.number
        )

    def entity_to_model(self, entity: Account) -> AccountModel:
        return AccountModel(
            id=entity.id,
            name=entity.name,
            owner_id=entity.owner_id,
            number=entity.number
        )


class AccountSqlalchemyRepository(AccountRepository, SqlAlchemyRepository):
    model_class = AccountModel
    mapper_class = AccountDataMapper

    async def get_all__user(self, user_id: uuid.UUID):
        stmt = select(AccountModel).where(AccountModel.owner_id == user_id)

        instances = (await self._session.scalars(stmt)).all()

        return [self._get_entity(instance) for instance in instances]