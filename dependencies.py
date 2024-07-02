from dependency_injector import providers, containers

from infrastructure import UserStorage


class Container(containers.DeclarativeContainer):
    storage = providers.Singleton(UserStorage)
