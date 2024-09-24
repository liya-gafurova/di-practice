import uuid
from dataclasses import dataclass

from dependency_injector.wiring import inject, Provide
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import Container
from domain.category.repositories import CategoryRepository
from shared.exceptions import EntityNotFoundException
from shared.interfaces import Query


@dataclass
class GetCategoryByIdDTO(Query):
    id: uuid.UUID
    user_id: uuid.UUID


@inject
async def get_category_by_id(
        query: GetCategoryByIdDTO,
        session: AsyncSession,
        category_repo: CategoryRepository = Provide[Container.category_repo],
):
    category_repo.session = session

    category = await category_repo.get_by_id(query.id)

    if category.user_id is not None and category.user_id != query.user_id:
        raise EntityNotFoundException(query.id)

    return category


@dataclass
class GetCategoryByNameDTO(Query):
    name: str
    user_id: uuid.UUID


@inject
async def get_category_by_name(
        query: GetCategoryByNameDTO,
        session: AsyncSession,
        category_repo: CategoryRepository = Provide[Container.category_repo],
):
    category_repo.session = session

    category = await category_repo.get_by_name(query.name, query.user_id)

    if category.user_id is not None and category.user_id != query.user_id:
        raise EntityNotFoundException(query.name)

    return category


@dataclass
class GetCategoriesDTO(Query):
    user_id: uuid.UUID

    with_general: bool = True


@inject
async def get_categories(
        query: GetCategoriesDTO,
        session: AsyncSession,
        category_repo: CategoryRepository = Provide[Container.category_repo],
):
    category_repo.session = session

    categories = await category_repo.get_categories(
        user_id=query.user_id,
        with_general=query.with_general
    )

    return categories
