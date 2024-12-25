"""Edit value Float to Decimal

Revision ID: 2bc97e70a324
Revises: f7cd78a6cf71
Create Date: 2024-12-24 18:09:45.848493

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = '2bc97e70a324'
down_revision: Union[str, None] = 'f7cd78a6cf71'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    
    if 'users' not in inspector.get_table_names():
        op.create_table('users',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('username', sa.String(), nullable=True),
            sa.Column('hashed_password', sa.String(), nullable=True),
            sa.Column('email', sa.String(), nullable=True),
            sa.Column('balance', sa.DECIMAL(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )

    indexes = inspector.get_indexes('users')
    if not any(index['name'] == 'ix_users_email' for index in indexes):
        op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    if not any(index['name'] == 'ix_users_id' for index in indexes):
        op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    if not any(index['name'] == 'ix_users_username' for index in indexes):
        op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    if 'transactions' not in inspector.get_table_names():
        op.create_table('transactions',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('sender_id', sa.Integer(), nullable=False),
            sa.Column('receiver_id', sa.Integer(), nullable=False),
            sa.Column('amount', sa.DECIMAL(), nullable=False),
            sa.Column('status', sa.String(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['receiver_id'], ['users.id']),
            sa.ForeignKeyConstraint(['sender_id'], ['users.id']),
            sa.PrimaryKeyConstraint('id')
        )
    
    indexes = inspector.get_indexes('transactions')
    if not any(index['name'] == 'ix_transactions_id' for index in indexes):
        op.create_index(op.f('ix_transactions_id'), 'transactions', ['id'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_transactions_id'), table_name='transactions')
    op.drop_table('transactions')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
