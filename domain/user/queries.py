import uuid
from dataclasses import dataclass

from dependency_injector.wiring import inject, Provide

from core.dependencies import Container
from domain.user.repositories import UserRepository


@dataclass
class GetUserDTO:
    id: uuid.UUID


@inject
async def get_user_by_id(
        query: GetUserDTO,
        storage: UserRepository = Provide[Container.user_storage]
):
    # check user_dto

    # crate user
    user = await storage.get_by_id(query.id)

    return user


@dataclass
class GetUsersDTO:
    pass


@inject
async def get_all_users(
        query: GetUsersDTO,
        storage: UserRepository = Provide[Container.user_storage]
):

    users = await storage.get_all()

    return users