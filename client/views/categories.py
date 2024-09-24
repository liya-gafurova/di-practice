import asyncio
import uuid

import streamlit as st
from dependency_injector import providers
from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel

from core.dependencies import Container
from core.settings import settings
from domain.category.commands import CreateCustomCategoryDTO, UpdateCategoryDTO, DeleteCategoryByIdDTO
from domain.category.queries import GetCategoriesDTO, GetCategoryByNameDTO
from domain.user.queries import GetUserDTO
from tests.conftest import create_engine_for_tests

users = {
    'lia': '3ddf2e94-1eba-4079-8719-dc9fafa7edde',
    'test_user': 'cbfc9862-35a7-4375-9ca3-6b19096ed210',
    'another_user': '69e3f71f-b9a4-4514-87f9-46b61979c249'
}

container = Container()
container.engine.override(providers.Singleton(create_engine_for_tests, db_url=container.config.SQLALCHEMY_DATABASE_URI))
container.config.from_dict(settings.__dict__)
container.wire(modules=[
    __name__,
    'domain.user.commands',
    'domain.user.queries',
    'domain.account.commands',
    'domain.account.queries',
    'domain.transaction.commands',
    'domain.transaction.queries'
])


class CategoryModel(BaseModel):
    name: str

@inject
async def get_categories_data(user_id: uuid.UUID, container=Provide[Container]):
    app = container.app()
    categories_date = await app.execute(
        GetCategoriesDTO(
            user_id=user_id
        ),
        container.db_session()
    )

    return [CategoryModel(name=c.name).model_dump() for c in categories_date]

@inject
async def add_category__form(st, user, container=Provide[Container]):
    app = container.app()
    with st.form('Add User category'):
        st.write('Add')
        name = st.text_input('Categoty Name', value=None)
        submitted = st.form_submit_button('Add')
        if submitted:
            new_category = await app.execute(
                CreateCustomCategoryDTO(name=name, user_id=user.id),
                container.db_session()
            )

@inject
async def edit_category__form(st, user, container=Provide[Container]):
    app = container.app()
    with st.form('Edit User category'):
        st.write('Edit')
        old_name = st.text_input('Old Name', value=None)
        new_name = st.text_input('New Name', value=None)
        submitted = st.form_submit_button('Edit')
        if submitted:
            to_be_edited = await app.execute(
                GetCategoryByNameDTO(name=old_name, user_id=user.id),
                container.db_session()
            )

            edited = await app.execute(
                UpdateCategoryDTO(
                    id=to_be_edited.id,
                    user_id=user.id,
                    name=new_name
                ),
                container.db_session()
            )

@inject
async def delete_category__form(st, user, container=Provide[Container]):
    app = container.app()
    with st.form('Delete User category'):
        st.write('Delete')
        name = st.text_input('Name', value=None)
        submitted = st.form_submit_button('Delete')
        if submitted:
            to_be_deleted = await app.execute(
                GetCategoryByNameDTO(name=name, user_id=user.id),
                container.db_session()
            )
            result = await app.execute(
                DeleteCategoryByIdDTO(
                    id=to_be_deleted.id,
                    user_id=user.id
                ),
                container.db_session()
            )

@inject
async def categories_page(container=Provide[Container]):
    app = container.app()
    user = await app.execute(GetUserDTO(id=uuid.UUID(users['test_user'])), container.db_session())
    categories = await get_categories_data(user.id)

    st.table(data=categories)
    await add_category__form(st, user)
    await edit_category__form(st, user)
    await delete_category__form(st, user)


if __name__ == '__main__':
    asyncio.run(categories_page())
