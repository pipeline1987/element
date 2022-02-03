"""create users table

Revision ID: 56fd16df3dc4
Revises: 
Create Date: 2022-02-01 17:58:33.251335

"""
import uuid
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = '56fd16df3dc4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute('create extension "uuid-ossp"')

    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('email', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True)
    )


def downgrade():
    op.execute('drop extension "uuid-ossp"')

    op.drop_table('users')
