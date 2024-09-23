import uuid
from dataclasses import dataclass

from dependency_injector.wiring import Provide, inject
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import Container
from domain.category.repositories import CategoryRepository
from shared.exceptions import EntityNotFoundException, ThisActionIsForbidden
from shared.interfaces import Command


@dataclass
class UpdateCategoryDTO:
    id: uuid.UUID
    user_id: uuid.UUID
    name: str | None = None


@inject
async def update_category(
        command: UpdateCategoryDTO,
        session: AsyncSession,
        category_repo: CategoryRepository = Provide[Container.category_repo],
):
    category_repo.session = session

    category = await category_repo.get_by_id(command.id)
    if not category.user_id and command.name:
        raise ThisActionIsForbidden('General Category cannot be edited.')
    elif category.user_id != command.user_id:
        raise EntityNotFoundException(command.id)

    category.name = command.name
    await category_repo.update(category)

    return category



@dataclass
class TestCommandDTO(Command):
    user_id: uuid.UUID
    name: str


@inject
async def test_handler(
        command: TestCommandDTO,
        session: AsyncSession,
        category_repo: CategoryRepository=Provide[Container.category_repo]
):
    category_repo.session = session

    cts = await category_repo.get_categories(command.user_id)

    return cts


