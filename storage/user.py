from shared.repositories import InMemoryRepository
from domain.user.repositories import UserRepository


class InMemoryUserRepository(UserRepository, InMemoryRepository):
    pass