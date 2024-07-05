"""003 alter transactions

Revision ID: 470faeda94aa
Revises: 3854cadcbd2d
Create Date: 2024-07-05 16:40:24.014258

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '470faeda94aa'
down_revision: Union[str, None] = '3854cadcbd2d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('transaction', 'credit_account',
               existing_type=sa.UUID(),
               nullable=True)
    op.alter_column('transaction', 'debit_account',
               existing_type=sa.UUID(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('transaction', 'debit_account',
               existing_type=sa.UUID(),
               nullable=False)
    op.alter_column('transaction', 'credit_account',
               existing_type=sa.UUID(),
               nullable=False)
    # ### end Alembic commands ###
