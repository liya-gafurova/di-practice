import uuid

from sqlalchemy import select, or_

from domain.category.entities import Category
from domain.category.repositories import CategoryRepository
from shared.data_mapper import DataMapper
from shared.repositories import SqlAlchemyRepository
from storage.models import CategoryModel


class CategoryDataMapper(DataMapper):
    def model_to_entity(self, instance: CategoryModel) -> Category:
        return Category(
            id=instance.id,
            name=instance.name,
            user_id=instance.user_id
        )

    def entity_to_model(self, entity: Category) -> CategoryModel:
        return CategoryModel(
            id=entity.id,
            name=entity.name,
            user_id=entity.user_id
        )


class CategorySqlAlchemyRepository(CategoryRepository, SqlAlchemyRepository):
    model_class = CategoryModel
    mapper_class = CategoryDataMapper

    async def get_categories(self, user_id: uuid.UUID, with_general: bool = True):

        where_clause = [(self.model_class.user_id == user_id)]
        if with_general:
            where_clause.append((self.model_class.user_id.is_(None)))

        stmt = select(self.model_class).where(
            or_(
                *where_clause
            )
        ).order_by(
            self.model_class.name
        )

        async with self._session:
            instances = (await self._session.scalars(stmt)).all()

        return [self._get_entity(instance) for instance in instances]


