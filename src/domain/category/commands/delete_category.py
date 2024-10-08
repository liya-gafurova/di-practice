import uuid
from dataclasses import dataclass

from dependency_injector.wiring import inject, Provide
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import Container
from domain.category.entities import Category
from domain.category.repositories import CategoryRepository
from shared.exceptions import EntityNotFoundException, ThisActionIsForbidden
from shared.interfaces import Command


@dataclass
class DeleteCategoryByIdDTO(Command):
    id: uuid.UUID
    user_id: uuid.UUID


@inject
async def delete_category(
        command: DeleteCategoryByIdDTO,
        session: AsyncSession,
        category_repo: CategoryRepository = Provide[Container.category_repo],
):
    category_repo.session = session

    to_be_deleted: Category = await category_repo.get_by_id(command.id)

    # todo: temporary
    if to_be_deleted.user_id is None:
        raise ThisActionIsForbidden('General Category cannot be deleted.')

    elif not to_be_deleted.is_available_for_user(command.user_id):
        raise EntityNotFoundException(command.id)

    await category_repo.remove(to_be_deleted)

    return to_be_deleted