

class UserHasNoPermissionForAction(Exception):
    def __init__(self, message: str):
        message = message
        super().__init__(message)