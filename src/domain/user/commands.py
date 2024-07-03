import uuid
from dataclasses import dataclass
from typing import Callable

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
        session_maker: Callable = Provide[Container.db_session],
        user_repo: UserRepository = Provide[Container.user_repo]
):
    # same session in this command
    user_repo.session = session_maker()

    # crate user
    user = User(id=User.next_id(), name=command.name, email=command.email)

    await user_repo.add(user)

    return user


@dataclass
class UpdateUserDTO:
    id: uuid.UUID
    name: str | None = None
    email: str | None = None


@inject
async def update_user(
        command: UpdateUserDTO,
        repo: UserRepository = Provide[Container.user_repo],
        session_maker=Provide[Container.db_session]
):
    repo.session = session_maker()
    user = await repo.get_by_id(command.id)
    if command.name:
        user.name = command.name
    if command.email:
        user.email = command.email

    await repo.update(command.id, user)

    return user
