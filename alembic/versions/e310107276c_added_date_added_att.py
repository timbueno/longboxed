"""added date_added attribute to creators

Revision ID: e310107276c
Revises: 1df77f8c0e6
Create Date: 2013-10-28 00:19:22.103398

"""

# revision identifiers, used by Alembic.
revision = 'e310107276c'
down_revision = '1df77f8c0e6'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('creators', sa.Column('date_added', sa.DateTime(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('creators', 'date_added')
    ### end Alembic commands ###
