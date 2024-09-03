import uuid
from dataclasses import dataclass

from dependency_injector.wiring import inject, Provide

from core.dependencies import Container
from domain.category.entities import Category
from domain.category.repositories import CategoryRepository


@dataclass
class CreateGeneralCategoryDTO:
    name: str


@inject
async def create_general_category(
        command: CreateGeneralCategoryDTO,
        session_maker=Provide[Container.db_session],
        category_repo: CategoryRepository = Provide[Container.category_repo],
):
    session = session_maker()
    category_repo.session = session

    # todo: check, that user CAN create general categories,
    # add category with user_id=None

    new_category = Category(
        id=Category.next_id(),
        name=command.name,
        user_id=None
    )

    await category_repo.add(new_category)

    return new_category


@dataclass
class CreateCustomCategoryDTO(CreateGeneralCategoryDTO):
    user_id: uuid.UUID


@inject
async def create_custom_category(
        command: CreateCustomCategoryDTO,
        session_maker=Provide[Container.db_session],
        category_repo: CategoryRepository = Provide[Container.category_repo],
):
    session = session_maker()
    category_repo.session = session

    # todo: check user exists

    new_category = Category(
        id=Category.next_id(),
        name=command.name,
        user_id=command.user_id
    )

    await category_repo.add(new_category)

    return new_category
