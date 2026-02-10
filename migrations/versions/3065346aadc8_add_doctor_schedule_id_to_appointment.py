"""add doctor_schedule_id to appointment

Revision ID: 3065346aadc8
Revises: 01e38b45bc5e
Create Date: 2026-02-10 19:34:30.788736

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3065346aadc8'
down_revision = '01e38b45bc5e'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("appointment") as batch_op:
        batch_op.add_column(
            sa.Column("doctor_schedule_id", sa.Integer(), nullable=True)
        )
        batch_op.create_foreign_key(
            "fk_appointment_doctor_schedule",
            "doctor_schedule",
            ["doctor_schedule_id"],
            ["doctor_schedule_id"]
        )


def downgrade():
    with op.batch_alter_table("appointment") as batch_op:
        batch_op.drop_constraint(
            "fk_appointment_doctor_schedule",
            type_="foreignkey"
        )
        batch_op.drop_column("doctor_schedule_id")
