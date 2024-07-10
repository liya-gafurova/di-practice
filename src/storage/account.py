import uuid
from decimal import Decimal

from sqlalchemy import select, func, and_, or_
from sqlalchemy.exc import IntegrityError

from domain.account.entities import Account
from domain.account.repositories import AccountRepository
from shared.data_mapper import DataMapper, MapperModel, MapperEntity
from shared.exceptions import EntityAlreadyCreatedException, EntityNotFoundException
from shared.repositories import SqlAlchemyRepository
from storage.models import AccountModel, TransactionModel, AccountBalanceModel


class AccountDataMapper(DataMapper):
    def model_to_entity(self, instance: AccountModel) -> Account:
        return Account(
            id=instance.id,
            name=instance.name,
            owner_id=instance.owner_id,
            number=instance.number,
            balance=instance.balance
        )

    def entity_to_model(self, entity: Account) -> AccountModel:
        return AccountModel(
            id=entity.id,
            name=entity.name,
            owner_id=entity.owner_id,
            number=entity.number
        )


class AccountSqlalchemyRepository(AccountRepository, SqlAlchemyRepository):
    model_class = AccountModel
    mapper_class = AccountDataMapper

    def accounts__stmt(self):
        stmt = select(
            AccountModel,
            AccountBalanceModel.balance
        ).join(
            AccountBalanceModel,
            AccountBalanceModel.account_id == AccountModel.id
        )

        return stmt

    async def add(self, account: Account):
        instance = self.map_entity_to_model(account)
        try:
            async with self._session:
                self._session.add(instance)
                await self._session.flush([instance])

                self._session.add(AccountBalanceModel(account_id=instance.id, balance=account.balance))

                await self._session.commit()

        except IntegrityError as err:
            raise EntityAlreadyCreatedException()

    async def get_by_id(self, entity_id):
        async with self._session:
            instance = (await self._session.execute(
                self.accounts__stmt().where(AccountModel.id == entity_id).limit(1)
            )).first()

        if instance is None:
            raise EntityNotFoundException(entity_id=entity_id)
        return self.convert_to_account(instance[0], instance[1])

    async def get_by_number(self, number: str):
        async with self._session:
            instance = (await self._session.execute(
                self.accounts__stmt().where(AccountModel.number == number).limit(1)
            )).first()

        if instance is None:
            raise EntityNotFoundException(entity_id=number)
        return self.convert_to_account(instance[0], instance[1])

    async def update_balance(self, account: Account):
        async with self._session:
            account_balance = (
                await self._session.scalars(
                    select(AccountBalanceModel).where(AccountBalanceModel.account_id == account.id)
                )
            ).first()

            if not account_balance:
                raise EntityNotFoundException(account.id)

            account_balance.balance = account.balance
            await self._session.merge(account_balance)
            await self._session.commit()


    async def remove(self, entity):
        async with self._session:
            instance = await self._session.get(AccountModel, entity.id)
            balance = (await self._session.scalars(select(AccountBalanceModel).where(AccountBalanceModel.account_id == entity.id).limit(1))).first()
            if instance is None:
                raise EntityNotFoundException(entity_id=entity.id)

            await self._session.delete(balance)
            await self._session.delete(instance)
            await self._session.commit()

    async def get_all__user(self, user_id: uuid.UUID):
        stmt = select(AccountModel, AccountBalanceModel.balance).join(
            AccountBalanceModel, AccountBalanceModel.account_id == AccountModel.id
        ).where(AccountModel.owner_id == user_id)

        async with self._session:
            instances = (await self._session.execute(stmt)).all()

        return [self.convert_to_account(account, balance) for account, balance in instances]

    async def calculate_balance(self, account_id: uuid.UUID):

        income__subquery = select(
            TransactionModel.debit_account,
            func.coalesce(func.sum(TransactionModel.amount), 0).label('income')
        ).select_from(
            TransactionModel
        ).join(
            AccountModel,
            and_(
                AccountModel.id == account_id,
                or_(
                    AccountModel.number == TransactionModel.credit_account,
                    AccountModel.number == TransactionModel.debit_account
                )
            )
        ).join(
            AccountBalanceModel,
            AccountBalanceModel.account_id == AccountModel.id
        ).where(
            and_(
                TransactionModel.created_at > AccountBalanceModel.updated_at,
                TransactionModel.deleted_at.is_(None)
            )
        ).group_by(
            TransactionModel.debit_account
        ).subquery()

        outcome__subquery = select(
            TransactionModel.credit_account,
            func.coalesce(func.sum(TransactionModel.amount), 0).label('outcome')
        ).select_from(
            TransactionModel
        ).join(
            AccountModel,
            and_(
                AccountModel.id == account_id,
                or_(
                    AccountModel.number == TransactionModel.credit_account,
                    AccountModel.number == TransactionModel.debit_account
                )
            )
        ).join(
            AccountBalanceModel,
            AccountBalanceModel.account_id == AccountModel.id
        ).where(
            and_(
                TransactionModel.created_at > AccountBalanceModel.updated_at,
                TransactionModel.deleted_at.is_(None)
            )
        ).group_by(
            TransactionModel.credit_account
        ).subquery()

        stmt = select(
            (func.coalesce(income__subquery.c.income, 0) - func.coalesce(outcome__subquery.c.outcome, 0)).label('balance')
        ).select_from(
            AccountModel
        ).join(
            income__subquery, income__subquery.c.debit_account == AccountModel.number, isouter=True
        ).join(
            outcome__subquery, outcome__subquery.c.credit_account == AccountModel.number, isouter=True
        ).where(AccountModel.id == account_id)

        async with self._session:
            balance = await self._session.scalar(stmt)

        return balance

    def convert_to_account(
            self,
            account: AccountModel,
            balance: Decimal
    ):
        return Account(
            id=account.id,
            number=account.number,
            name=account.name,
            owner_id=account.owner_id,
            balance=balance
        )
