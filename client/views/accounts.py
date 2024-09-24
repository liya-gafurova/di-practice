from decimal import Decimal

from dependency_injector.wiring import inject, Provide

from client.models import AccountReadModel
from core.dependencies import Container
from domain.account.commands import CreateAccountDTO, UpdateAccountDTO, DeleteAccountDTO
from domain.account.entities import Account
from domain.account.queries import GetAllUserAccountsDTO


@inject
async def get_accounts_data(user, container=Provide[Container]):
    app = container.app()
    data: list[Account] = await app.execute(GetAllUserAccountsDTO(user.id), container.db_session())

    display_data = [AccountReadModel(
        number=account.number,
        name=account.name,
        balance=account.balance
    ).model_dump(by_alias=True) for account in data]

    return display_data

@inject
async def add_account__form(st, user, container=Provide[Container]):
    app = container.app()
    with st.form('Add account'):
        st.write('Add')
        account_name = st.text_input('Account Name')
        account_balance = st.number_input('Account Balance')

        submitted = st.form_submit_button("Add")
        if submitted:
            await app.execute(
                CreateAccountDTO(
                    user_id=user.id,
                    name=account_name,
                    balance=Decimal(account_balance).quantize(Decimal('0.01'))
                ),
                container.db_session()
            )

@inject
async def update_account__form(st, user, container=Provide[Container]):
    app = container.app()
    with st.form('Update Account'):
        st.write('Update')
        account_number = st.text_input('Account Number')
        name = st.text_input('Account Name', value=None)
        balance = st.number_input('Account Balance', value=None)

        submitted = st.form_submit_button("Update")
        if submitted:
            await app.execute(
                UpdateAccountDTO(
                    user_id=user.id,
                    account_number=account_number,
                    name=name,
                    balance=Decimal(balance).quantize(Decimal('0.01')) if balance else None
                ),
                container.db_session()
            )

@inject
async def delete_account__form(st, user, container=Provide[Container]):
    app = container.app()
    with st.form('Delete Account'):
        st.write('Delete')
        account_number = st.text_input('Account Number')

        submitted = st.form_submit_button("Delete")
        if submitted:
            await app.execute(DeleteAccountDTO(user.id, account_number), container.db_session())
