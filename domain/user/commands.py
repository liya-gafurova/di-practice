import uuid
from dataclasses import dataclass

from dependency_injector.wiring import inject, Provide

from core.dependencies import Container
from domain.user.entities import User
from domain.user.repositories import UserRepository


@dataclass
class CreateUserDTO:
    name: str
    email: str | None = None


@inject
async def create_user(
        command: CreateUserDTO,
        storage: UserRepository = Provide[Container.user_storage]
):
    # check user_dto

    # crate user
    user = User(id=User.next_id(), name=command.name, email=command.email)

    await storage.add(user)

    return user


@dataclass
class UpdateUserDTO:
    id: uuid.UUID
    name: str | None = None
    email: str | None = None


@inject
async def update_user(
        command: UpdateUserDTO,
        storage: UserRepository = Provide[Container.user_storage]
):
    user = await storage.get_by_id(command.id)
    if command.name:
        user.name = command.name
    if command.email:
        user.email = command.email

    await storage.update(command.id, user)

    return user
