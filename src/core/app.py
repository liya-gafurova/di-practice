import inspect
import typing
from importlib import import_module

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker

from shared.interfaces import Command, Query


class Application:
    """
    Application stores information about application Commands, Queries, Services
    handles execution of app functionality - wraps every unit (Commands, Queries) with Session:
     - session starts
     - command functionality is being handled
     - if command is handled successfully, then session commits changes
     - otherwise, session changes are being rolled back

    So, here sqlalchemy ORM Session Unit Of Work pattern is used
    """

    def __init__(self):
        self.modules = [
            import_module('domain.category.commands', package=None),
            import_module('domain.category.queries', package=None),

            import_module('domain.user.commands', package=None),
            import_module('domain.user.queries', package=None),

            import_module('domain.transaction.commands', package=None),
            import_module('domain.transaction.queries', package=None),

            import_module('domain.account.commands', package=None),
            import_module('domain.account.queries', package=None),

        ]

        self.handlers = self.get_handlers()

    def get_handlers(self):
        handlers = dict()
        def get_action_class(handler_function):
            params_with_types = typing.get_type_hints(handler_function)
            action_class = params_with_types.get('command') \
                if params_with_types.get('command') \
                else params_with_types.get('query')

            return action_class

        for module in self.modules:
            module_handlers = inspect.getmembers(module, inspect.isfunction)

            _handlers = dict()
            for _, handler in module_handlers:
                handler_action_class = get_action_class(handler)
                if handler_action_class:
                    _handlers[handler_action_class] = handler

            handlers.update(_handlers)

        return handlers

    async def execute(
            self,
            action: typing.Type[Command | Query],
            session_maker: async_sessionmaker
    ):
        async with session_maker() as session:
            try:
                handler = self.handlers[type(action)]
                result = await handler(action, session)
                await session.commit()
                return result
            except IntegrityError as db_error:
                await session.rollback()
