"""004 alter accounts

Revision ID: 42ed6a5e9df4
Revises: 470faeda94aa
Create Date: 2024-07-08 16:40:15.810080

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '42ed6a5e9df4'
down_revision: Union[str, None] = '470faeda94aa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('account_balance',
    sa.Column('account_id', sa.UUID(), nullable=False),
    sa.Column('balance', sa.Numeric(precision=14, scale=2), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['account_id'], ['account.id'], name=op.f('account_balance_account_id_account_fkey')),
    sa.PrimaryKeyConstraint('id', name=op.f('account_balance_pkey')),
    sa.UniqueConstraint('account_id', name=op.f('account_balance_account_id_key'))
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('account_balance')
    # ### end Alembic commands ###
