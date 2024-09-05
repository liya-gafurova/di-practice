from sqlalchemy import select

from domain.user.entities import User

from domain.user.repositories import UserRepository
from shared.data_mapper import DataMapper
from shared.repositories import InMemoryRepository, SqlAlchemyRepository
from storage.models import UserModel


class InMemoryUserRepository(UserRepository, InMemoryRepository):
    pass


class UserMapper(DataMapper):
    def model_to_entity(self, instance: UserModel) -> User:
        return User(
            id=instance.id,
            name=instance.username,
            email=None,
        )

    def entity_to_model(self, entity: User) -> UserModel:
        return UserModel(
            id=entity.id,
            username=entity.name
        )


class UserSqlAlchemyRepository(UserRepository, SqlAlchemyRepository):
    model_class = UserModel
    mapper_class = UserMapper

    async def get_by_name(self, name: str):
        stmt = select(UserModel).filter_by(username=name).limit(1)

        async with self._session:
            instance = (await self._session.scalars(stmt)).first()

        return self._get_entity(instance)


