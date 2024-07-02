from dependency_injector import providers, containers

from storage.user import InMemoryUserRepository


class Container(containers.DeclarativeContainer):
    user_storage = providers.Singleton(InMemoryUserRepository)
