import uuid
from dataclasses import dataclass

from dependency_injector.wiring import inject, Provide
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import Container
from domain.category.entities import Category
from domain.category.repositories import CategoryRepository
from shared.interfaces import Command


@dataclass
class CreateGeneralCategoryDTO(Command):
    name: str


@inject
async def create_general_category(
        command: CreateGeneralCategoryDTO,
        session: AsyncSession,
        category_repo: CategoryRepository = Provide[Container.category_repo],
):
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
        session: AsyncSession,
        category_repo: CategoryRepository = Provide[Container.category_repo],
):
    category_repo.session = session

    # todo: check user exists

    new_category = Category(
        id=Category.next_id(),
        name=command.name,
        user_id=command.user_id
    )

    await category_repo.add(new_category)

    return new_category
