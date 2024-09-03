import uuid
from dataclasses import dataclass

from dependency_injector.wiring import Provide, inject

from core.dependencies import Container
from domain.category.repositories import CategoryRepository
from shared.exceptions import EntityNotFoundException, ThisActionIsForbidden


@dataclass
class UpdateCategoryDTO:
    id: uuid.UUID
    user_id: uuid.UUID
    name: str | None = None


@inject
async def update_category(
        command: UpdateCategoryDTO,
        session_maker=Provide[Container.db_session],
        category_repo: CategoryRepository = Provide[Container.category_repo],
):
    session = session_maker()
    category_repo.session = session

    category = await category_repo.get_by_id(command.id)
    if not category.user_id and command.name:
        raise ThisActionIsForbidden('General Category cannot be edited.')
    elif category.user_id != command.user_id:
        raise EntityNotFoundException(command.id)

    category.name = command.name
    await category_repo.update(category)

    return category
