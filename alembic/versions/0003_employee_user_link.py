"""adiciona companies.is_active e employees.user_id (vínculo Employee <-> User)

Revision ID: 0003
Revises: 0002
Create Date: 2026-08-30
"""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade():
    # 1. companies.is_active — antes não existia; entra com default true
    #    para não quebrar empresas já cadastradas.
    op.add_column(
        "companies",
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
    )

    # 2. employees.user_id — vínculo real com users.id.
    #    Entra nullable=True primeiro porque pode já existir funcionário
    #    sem usuário correspondente; depois de rodar o backfill manual
    #    (associar cada employee a um user pelo email, se aplicável),
    #    rode uma migration separada tornando a coluna NOT NULL.
    op.add_column(
        "employees",
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=True),
    )
    op.create_unique_constraint("uq_employees_user_id", "employees", ["user_id"])


def downgrade():
    op.drop_constraint("uq_employees_user_id", "employees", type_="unique")
    op.drop_column("employees", "user_id")
    op.drop_column("companies", "is_active")
