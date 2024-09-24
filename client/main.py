import asyncio
import os
import uuid
from enum import Enum
import sys

import streamlit as st
from dependency_injector import providers
from dependency_injector.wiring import inject, Provide

from client.views.accounts import get_accounts_data, add_account__form, update_account__form, delete_account__form
from client.views.categories import get_categories_data, add_category__form, edit_category__form, delete_category__form
from client.views.transactions import get_transactions_data, add_transaction__form
from core.dependencies import Container
from core.settings import settings
from domain.user.queries import GetUserDTO
from tests.conftest import create_engine_for_tests

st.set_page_config(layout="wide")


users = {
    'main_user': '3ddf2e94-1eba-4079-8719-dc9fafa7edde',
    'test_user': 'cbfc9862-35a7-4375-9ca3-6b19096ed210',
    'another_user': '69e3f71f-b9a4-4514-87f9-46b61979c249'
}

class Pages(str, Enum):
    accounts = 'Accounts'
    categories = 'Categories'
    transactions  = 'Transactions'
    title = 'Personal Finance'


Deps = Container()
Deps.engine.override(providers.Singleton(create_engine_for_tests, db_url=Deps.config.SQLALCHEMY_DATABASE_URI))
Deps.config.from_dict(settings.__dict__)
Deps.wire(modules=[
    __name__,
    'domain.user.commands',
    'domain.user.queries',
    'domain.account.commands',
    'domain.account.queries',
    'domain.transaction.commands',
    'domain.transaction.queries',
    'domain.category.commands',
    'domain.category.queries',
    'client.views.accounts',
])

@inject
async def main_page(st, container):
    app = container.app()
    current_user_id = users['main_user']
    current_user_name = {id: name for name, id in users.items()}[current_user_id]
    st.title(f'{Pages.title} / {current_user_name}')

    user = await app.execute(GetUserDTO(id=uuid.UUID(current_user_id)), container.db_session())
    accounts_data = await get_accounts_data(user)
    txs_data = await get_transactions_data(user)
    categories = await get_categories_data(user.id)

    tab1, tab2, tab3 = st.tabs([Pages.accounts, Pages.transactions, Pages.categories])
    with tab1:
        st.header(Pages.accounts.value)

        st.table(data=accounts_data)
        await add_account__form(st, user)
        await update_account__form(st, user)
        await delete_account__form(st, user)
    with tab2:
        st.header(Pages.transactions.value)

        await add_transaction__form(st, user, accounts_data, categories)
        st.table(data=txs_data)
    with tab3:
        st.header(Pages.categories.value)
        col1, col2 = st.columns(2)
        with col1:
            st.table(data=categories)
        with col2:
            await add_category__form(st, user)
            await edit_category__form(st, user)
            await delete_category__form(st, user)



if __name__ == '__main__':
    asyncio.run(main_page(st, Deps))
