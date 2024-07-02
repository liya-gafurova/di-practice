from domain.user.entities import User
from shared.data_mapper import DataMapper, MapperModel, MapperEntity
from shared.repositories import InMemoryRepository, SqlAlchemyRepository
from domain.user.repositories import UserRepository
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
