"""add user role

Revision ID: 0005_companie_limite
Revises: 0004_user_role
Create Date: 2026-08-30

"""
revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
def upgrade():
    op.add_column("companies", sa.Column("max_employees", sa.Integer, nullable=False, server_default="50"))