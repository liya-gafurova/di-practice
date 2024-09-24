import uuid
from dataclasses import dataclass

from dependency_injector.wiring import inject, Provide
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import Container
from domain.user.repositories import UserRepository
from shared.interfaces import Command


@dataclass
class UpdateUserDTO(Command):
    id: uuid.UUID
    name: str | None = None
    email: str | None = None


@inject
async def update_user(
        command: UpdateUserDTO,
        session: AsyncSession,
        repo: UserRepository = Provide[Container.user_repo],
):
    repo.session = session
    user = await repo.get_by_id(command.id)
    if command.name:
        user.name = command.name
    if command.email:
        user.email = command.email

    await repo.update(user)

    return user
