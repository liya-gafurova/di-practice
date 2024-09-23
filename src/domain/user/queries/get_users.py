import uuid
from dataclasses import dataclass

from dependency_injector.wiring import inject, Provide
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import Container
from domain.user.repositories import UserRepository
from shared.interfaces import Query


@dataclass
class GetUserDTO(Query):
    id: uuid.UUID


@inject
async def get_user_by_id(
        query: GetUserDTO,
        session:AsyncSession,
        repo=Provide[Container.user_repo]
):
    # check user_dto
    repo.session = session

    # crate user
    user = await repo.get_by_id(query.id)

    return user



@dataclass
class GetUserByNameDTO(Query):
    name: str


@inject
async def get_user_by_name(
        query: GetUserByNameDTO,
        session:AsyncSession,
        repo=Provide[Container.user_repo]
):
    # check user_dto
    repo.session = session

    # crate user
    user = await repo.get_by_name(query.name)

    return user


@dataclass
class GetUsersDTO(Query):
    pass


@inject
async def get_all_users(
        query: GetUsersDTO,
        session: AsyncSession,
        repo: UserRepository = Provide[Container.user_repo],
):
    repo.session = session
    users = await repo.get_all()

    return users
