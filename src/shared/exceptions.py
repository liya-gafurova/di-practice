import uuid

class EntityNotFoundException(Exception):
    def __init__(self, entity_id: uuid.UUID | str):
        message = f'Entity {entity_id} not found.'
        super().__init__(message)


class EntityAlreadyCreatedException(Exception):
    def __init__(self, entity_id: str | None = None):
        message = f'Entity {entity_id} already created.'
        super().__init__(message)


class IncorrectData(Exception):
    def __init__(self, message):
        super().__init__(message)


class ThisActionIsForbidden(Exception):
    def __init__(self, message: str):
        super().__init__(message)