from unicodedata import category

from pydash import find

from client.models import TransactionReadModel
from domain.account.commands import add_transaction_for_user, AddTransactionDTO
from domain.account.queries import get_all_user_accounts, GetAllUserAccountsDTO, get_account_by_number, \
    GetAccountByNumberDTO
from domain.category.queries import get_category_by_name, GetCategoryByNameDTO
from domain.transaction.queries import get_user_transactions, GetUserTransactionsDTO


async def get_transactions_data(user):
    txs = await get_user_transactions(GetUserTransactionsDTO(user.id))
    user_accounts = await get_all_user_accounts(GetAllUserAccountsDTO(user.id))

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


async def add_transaction__form(st, user, accounts, categories):
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
                category = await get_category_by_name(
                    GetCategoryByNameDTO(name=category_name, user_id=user.id)
                )
            debit_account, credit_account = None, None
            if to_number:
                account = find(accounts, lambda acc: acc['name'] == to_number)
                to_number = account['number']
                debit_account = await get_account_by_number(GetAccountByNumberDTO(
                    user_id=user.id,
                    account_number=to_number
                ))
            if from_number:
                account = find(accounts, lambda acc: acc['name'] == from_number)
                from_number = account['number']
                credit_account = await get_account_by_number(GetAccountByNumberDTO(
                    user_id=user.id,
                    account_number=from_number
                ))
            await add_transaction_for_user(
                AddTransactionDTO(
                    user_id=user.id,
                    credit_account=credit_account.number if credit_account else None,
                    debit_account=debit_account.number if debit_account else None,
                    amount=amount,
                    category_id=category.id if category else None
                )
            )
