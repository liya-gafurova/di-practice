from unicodedata import category

from dependency_injector.wiring import Provide, inject
from pydash import find

from client.models import TransactionReadModel
from core.dependencies import Container
from domain.account.commands import AddTransactionDTO
from domain.account.queries import GetAllUserAccountsDTO, GetAccountByNumberDTO
from domain.category.queries import GetCategoryByNameDTO
from domain.transaction.queries import GetUserTransactionsDTO

@inject
async def get_transactions_data(user, container=Provide[Container]):
    app = container.app()
    txs = await app.execute(GetUserTransactionsDTO(user.id), container.db_session())
    user_accounts = await app.execute(GetAllUserAccountsDTO(user.id), container.db_session())

    display_data = []
    for tx in txs:
        credit_acc = find(user_accounts, lambda acc: acc.number == tx.credit_account)
        debit_acc = find(user_accounts, lambda acc: acc.number == tx.debit_account)
        display_data.append(
            TransactionReadModel(
                debit_account=debit_acc.name if debit_acc else None,
                amount=tx.amount,
                credit_account=credit_acc.name if credit_acc else None,
                type=tx.type,
                category=tx.category.name if tx.category else None
            ).model_dump(by_alias=True)
        )
    return display_data

@inject
async def add_transaction__form(st, user, accounts, categories, container=Provide[Container]):
    app = container.app()
    with st.form('Add Transaction'):
        st.write('Add')
        from_number = st.selectbox('From Account', (a['name'] for a in accounts), index=None,
                                   placeholder='Select account...')
        to_number = st.selectbox('To Account', (a['name'] for a in accounts), index=None,
                                 placeholder='Select account...')
        category_name = st.selectbox('Categories', (c['name'] for c in categories), index=None,
                                     placeholder='Select category...')
        amount = st.number_input('Transaction Amount')

        submitted = st.form_submit_button("Add")
        if submitted:
            category = None
            if category_name:
                category = await app.execute(
                    GetCategoryByNameDTO(name=category_name, user_id=user.id),
                    container.db_session()
                )
            debit_account, credit_account = None, None
            if to_number:
                account = find(accounts, lambda acc: acc['name'] == to_number)
                to_number = account['number']
                debit_account = await app.execute(GetAccountByNumberDTO(
                    user_id=user.id,
                    account_number=to_number
                ), container.db_session())
            if from_number:
                account = find(accounts, lambda acc: acc['name'] == from_number)
                from_number = account['number']
                credit_account = await app.execute(GetAccountByNumberDTO(
                    user_id=user.id,
                    account_number=from_number
                ), container.db_session())
            await app.execute(
                AddTransactionDTO(
                    user_id=user.id,
                    credit_account=credit_account.number if credit_account else None,
                    debit_account=debit_account.number if debit_account else None,
                    amount=amount,
                    category_id=category.id if category else None
                ),
                container.db_session()
            )
