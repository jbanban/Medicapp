"""fix reminder column standard

Revision ID: 1ec52538d8db
Revises: 9076f912965a
Create Date: 2026-02-19 08:57:30.147397
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '1ec52538d8db'
down_revision = '9076f912965a'
branch_labels = None
depends_on = None


def upgrade():
    # 1) Fix existing NULL values first (SQLite-safe)
    op.execute(
        "UPDATE appointment SET reminder_1hr_sent = 0 WHERE reminder_1hr_sent IS NULL"
    )
    op.execute(
        "UPDATE appointment SET reminder_ontime_sent = 0 WHERE reminder_ontime_sent IS NULL"
    )

    # 2) Now enforce NOT NULL + default
    with op.batch_alter_table('appointment', schema=None) as batch_op:
        batch_op.alter_column(
            'reminder_1hr_sent',
            existing_type=sa.BOOLEAN(),
            nullable=False,
            server_default=sa.text("0")
        )
        batch_op.alter_column(
            'reminder_ontime_sent',
            existing_type=sa.BOOLEAN(),
            nullable=False,
            server_default=sa.text("0")
        )


def downgrade():
    # Revert to nullable and remove defaults
    with op.batch_alter_table('appointment', schema=None) as batch_op:
        batch_op.alter_column(
            'reminder_ontime_sent',
            existing_type=sa.BOOLEAN(),
            nullable=True,
            server_default=None
        )
        batch_op.alter_column(
            'reminder_1hr_sent',
            existing_type=sa.BOOLEAN(),
            nullable=True,
            server_default=None
        )
