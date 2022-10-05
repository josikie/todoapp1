"""empty message

Revision ID: 7422608cfe68
Revises: b0a44ef38db5
Create Date: 2022-10-04 14:43:19.043420

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7422608cfe68'
down_revision = 'b0a44ef38db5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('todos', 'list_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('todos', 'list_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###