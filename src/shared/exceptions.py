import uuid

class EntityNotFoundException(Exception):
    def __init__(self, entity_id: uuid.UUID):
        message = f'Entity {entity_id} not found.'
        super().__init__(message)


class EntityAlreadyCreatedException(Exception):
    def __init__(self, entity_id: str | None = None):
        message = f'Entity {entity_id} already created.'
        super().__init__(message)