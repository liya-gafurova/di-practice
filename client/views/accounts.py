from decimal import Decimal

from client.models import AccountReadModel
from domain.account.commands import create_account, CreateAccountDTO, update_account, UpdateAccountDTO, delete_account, \
    DeleteAccountDTO
from domain.account.entities import Account
from domain.account.queries import get_all_user_accounts, GetAllUserAccountsDTO


async def get_accounts_data(user):
    data: list[Account] = await get_all_user_accounts(GetAllUserAccountsDTO(user.id))

    display_data = [AccountReadModel(
        number=account.number,
        name=account.name,
        balance=account.balance
    ).model_dump(by_alias=True) for account in data]

    return display_data


async def add_account__form(st, user):
    with st.form('Add account'):
        st.write('Add')
        account_name = st.text_input('Account Name')
        account_balance = st.number_input('Account Balance')

        submitted = st.form_submit_button("Add")
        if submitted:
            await create_account(
                CreateAccountDTO(
                    user_id=user.id,
                    name=account_name,
                    balance=Decimal(account_balance).quantize(Decimal('0.01'))
                )
            )


async def update_account__form(st, user):
    with st.form('Update Account'):
        st.write('Update')
        account_number = st.text_input('Account Number')
        name = st.text_input('Account Name', value=None)
        balance = st.number_input('Account Balance', value=None)

        submitted = st.form_submit_button("Update")
        if submitted:
            await update_account(
                UpdateAccountDTO(
                    user_id=user.id,
                    account_number=account_number,
                    name=name,
                    balance=Decimal(balance).quantize(Decimal('0.01')) if balance else None
                )
            )


async def delete_account__form(st, user):
    with st.form('Delete Account'):
        st.write('Delete')
        account_number = st.text_input('Account Number')

        submitted = st.form_submit_button("Delete")
        if submitted:
            await delete_account(DeleteAccountDTO(user.id, account_number))
