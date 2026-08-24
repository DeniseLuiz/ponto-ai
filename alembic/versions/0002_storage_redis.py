"""troca pdf_path/result_path por pdf_key/result_key (storage Redis)

Revision ID: 0002
Revises: 0001
Create Date: 2024-01-02
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("jobs", sa.Column("pdf_key", sa.String, nullable=True))
    op.add_column("jobs", sa.Column("result_key", sa.String, nullable=True))
    op.drop_column("jobs", "pdf_path")
    op.drop_column("jobs", "result_path")
    op.alter_column("jobs", "pdf_key", nullable=False)


def downgrade():
    op.add_column("jobs", sa.Column("pdf_path", sa.String, nullable=True))
    op.add_column("jobs", sa.Column("result_path", sa.String, nullable=True))
    op.drop_column("jobs", "pdf_key")
    op.drop_column("jobs", "result_key")
    op.alter_column("jobs", "pdf_path", nullable=False)
    # ;;;
