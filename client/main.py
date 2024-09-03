import asyncio
import uuid

import streamlit as st
from dependency_injector import providers

from client.views.accounts import get_accounts_data, add_account__form, update_account__form, delete_account__form
from client.views.categories import get_categories_data, add_category__form, edit_category__form, delete_category__form
from client.views.transactions import get_transactions_data, add_transaction__form
from core.dependencies import Container
from core.settings import settings
from src.domain.user.queries import get_user_by_id, GetUserDTO
from tests.conftest import create_engine_for_tests

st.set_page_config(layout="wide")
st.title('Personal Finance')

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


async def main_page(st):
    user = await get_user_by_id(GetUserDTO(id=uuid.UUID(users['lia'])))
    accounts_data = await get_accounts_data(user)
    txs_data = await get_transactions_data(user)
    categories = await get_categories_data(user.id)

    tab1, tab2, tab3 = st.tabs(["Accounts", "Transactions", "Categories"])
    with tab1:
        st.header("Accounts")

        st.table(data=accounts_data)
        await add_account__form(st, user)
        await update_account__form(st, user)
        await delete_account__form(st, user)
    with tab2:
        st.header("Transactions")

        await add_transaction__form(st, user, accounts_data, categories)
        st.table(data=txs_data)
    with tab3:
        st.header("Categories")

        st.table(data=categories)
        await add_category__form(st, user)
        await edit_category__form(st, user)
        await delete_category__form(st, user)



if __name__ == '__main__':
    asyncio.run(main_page(st))
