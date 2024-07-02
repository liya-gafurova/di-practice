from abc import ABC
from typing import Generic

from sqlalchemy import select

from shared.data_mapper import DataMapper
from shared.database import Base
from shared.entities import Entity
from shared.exceptions import EntityNotFoundException


class Repository(ABC):

    async def add(self, entity):
        raise NotImplementedError

    async def get_by_id(self, id):
        raise NotImplementedError

    async def get_all(self):
        raise NotImplementedError

    async def update(self, id, entity):
        raise NotImplementedError

    async def remove(self, id):
        raise NotImplementedError


class InMemoryRepository(Repository):
    def __init__(self):
        self.entities = {}

    async def add(self, entity):
        self.entities[entity.id] = entity

    async def get_by_id(self, id):
        return self.entities.get(id)

    async def get_all(self):
        return list(self.entities.values())

    async def update(self, id, entity):
        if entity.id != id:
            raise Exception('Entity id cannot be updated.')
        if self.entities.get(id) is None:
            raise Exception('Entity not found.')
        self.entities[id] = entity

    async def remove(self, id):
        if self.entities.get(id) is None:
            raise Exception('Entity not found.')

        self.entities.pop(id)


class SqlAlchemyRepository(Repository):
    mapper_class: type[DataMapper[Entity, Base]]
    model_class: type[Base]

    def __init__(self, db_session):
        self._session = db_session

    async def add(self, entity):
        instance = self.map_entity_to_model(entity)
        self._session.add(instance)

    async def get_by_id(self, entity_id):
        instance = await self._session.get(self.get_model_class(), entity_id)
        if instance is None:
            raise EntityNotFoundException(entity_id=entity_id)
        return self._get_entity(instance)

    async def get_all(self):
        stmt = select(self.get_model_class()).order_by(self.get_model_class().created_at.desc())
        instances = (await self._session.scalars(stmt)).all()

        return [self._get_entity(instance) for instance in instances]

    async def update(self, id, entity):
        instance = self.map_entity_to_model(entity)
        merged = await self._session.merge(instance)
        self._session.add(merged)

    async def remove(self, id):
        instance = await self._session.get(self.get_model_class(), id)
        if instance is None:
            raise EntityNotFoundException( entity_id=id)
        await self._session.delete(instance)

    def map_entity_to_model(self, entity: Entity):
        assert self.mapper_class, (
            f"No data_mapper attribute in {self.__class__.__name__}. "
            "Make sure to include `mapper_class = MyDataMapper` in the Repository class."
        )

        return self.data_mapper.entity_to_model(entity)

    def map_model_to_entity(self, instance):
        assert self.data_mapper
        return self.data_mapper.model_to_entity(instance)

    @property
    def data_mapper(self):
        return self.mapper_class()

    def get_model_class(self):
        return self.model_class

    def _get_entity(self, instance):
        if instance is None:
            return None
        entity = self.map_model_to_entity(instance)
        return entity
