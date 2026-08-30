from alembic import op
import sqlalchemy as sa
def upgrade():
    op.add_column("users", sa.Column("role", sa.String, nullable=False, server_default="user"))

def downgrade():
    op.drop_column("users", "role")