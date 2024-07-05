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
        db_session=Provide[Container.db_session],
        repo=Provide[Container.user_repo]
):
    # check user_dto
    repo.session = db_session()

    # crate user
    user = await repo.get_by_id(query.id)

    return user


@dataclass
class GetUsersDTO:
    pass


@inject
async def get_all_users(
        query: GetUsersDTO,
        repo: UserRepository = Provide[Container.user_repo],
        session_maker=Provide[Container.db_session]
):
    repo.session = session_maker()
    users = await repo.get_all()

    return users
