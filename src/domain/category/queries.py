import uuid
from dataclasses import dataclass

from dependency_injector.wiring import inject, Provide

from core.dependencies import Container
from domain.category.repositories import CategoryRepository
from shared.exceptions import EntityNotFoundException


@dataclass
class GetCategoryByIdDTO:
    id: uuid.UUID
    user_id: uuid.UUID


@inject
async def get_category_by_id(
        query: GetCategoryByIdDTO,
        session_maker=Provide[Container.db_session],
        category_repo: CategoryRepository = Provide[Container.category_repo],
):
    category_repo.session = session_maker()

    category = await category_repo.get_by_id(query.id)

    if category.user_id is not None and category.user_id != query.user_id:
        raise EntityNotFoundException(query.id)

    return category


@dataclass
class GetCategoriesDTO:
    user_id: uuid.UUID

    with_general: bool = True


@inject
async def get_categories(
        query: GetCategoriesDTO,
        session_maker=Provide[Container.db_session],
        category_repo: CategoryRepository = Provide[Container.category_repo],
):
    category_repo.session = session_maker()

    categories = await category_repo.get_categories(
        user_id=query.user_id,
        with_general=query.with_general
    )

    return categories


