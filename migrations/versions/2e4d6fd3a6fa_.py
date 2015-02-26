"""empty message

Revision ID: 2e4d6fd3a6fa
Revises: 5a22b3401cfd
Create Date: 2014-12-10 19:58:32.094908

"""

# revision identifiers, used by Alembic.
revision = '2e4d6fd3a6fa'
down_revision = '5a22b3401cfd'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('diamond_lists', sa.Column('revision', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('diamond_lists', 'revision')
    ### end Alembic commands ###