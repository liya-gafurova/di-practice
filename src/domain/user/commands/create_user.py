from dataclasses import dataclass

from dependency_injector.wiring import inject, Provide
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import Container
from domain.user.entities import User
from domain.user.repositories import UserRepository
from shared.interfaces import Command


@dataclass
class CreateUserDTO(Command):
    name: str
    email: str | None = None


@inject
async def create_user(
        command: CreateUserDTO,
        session: AsyncSession,
        user_repo: UserRepository = Provide[Container.user_repo]
):
    # same session in this command
    user_repo.session = session

    # crate user
    user = User(id=User.next_id(), name=command.name, email=command.email)

    await user_repo.add(user)

    return user


