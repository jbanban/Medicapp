"""change email into username - account

Revision ID: 0d18af7b45dc
Revises: 
Create Date: 2026-01-21 18:19:39.906072
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0d18af7b45dc'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # 1️⃣ Add username as NULLABLE first
    with op.batch_alter_table('account', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('username', sa.String(length=100), nullable=True)
        )

    # 2️⃣ Copy existing email values into username
    op.execute("UPDATE account SET username = email")

    # 3️⃣ Enforce NOT NULL + UNIQUE, then drop email
    with op.batch_alter_table('account', schema=None) as batch_op:
        batch_op.alter_column(
            'username',
            nullable=False
        )
        batch_op.create_unique_constraint(
            'uq_account_username',
            ['username']
        )
        batch_op.drop_column('email')


def downgrade():
    # Reverse safely
    with op.batch_alter_table('account', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('email', sa.String(length=100), nullable=True)
        )

    op.execute("UPDATE account SET email = username")

    with op.batch_alter_table('account', schema=None) as batch_op:
        batch_op.alter_column(
            'email',
            nullable=False
        )
        batch_op.drop_constraint(
            'uq_account_username',
            type_='unique'
        )
        batch_op.drop_column('username')
