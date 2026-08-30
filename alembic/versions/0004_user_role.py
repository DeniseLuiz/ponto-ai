"""add user role

Revision ID: 0004_user_role
Revises: 0003_nome_da_migracao_anterior
Create Date: 2026-08-30

"""
revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
def upgrade():
    op.add_column("users", sa.Column("role", sa.String, nullable=False, server_default="user"))

def downgrade():
    op.drop_column("users", "role")