from abc import ABC


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
