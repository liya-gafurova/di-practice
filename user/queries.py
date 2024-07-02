import uuid
from dataclasses import dataclass

from dependency_injector.wiring import inject, Provide

from dependencies import Container
from infrastructure import UserStorage


@dataclass
class GetUserDTO:
    id: uuid.UUID


@inject
async def get_user_by_id(
        query: GetUserDTO,
        storage: UserStorage = Provide[Container.storage]
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
        storage: UserStorage = Provide[Container.storage]
):

    users = await storage.get_all()

    return users