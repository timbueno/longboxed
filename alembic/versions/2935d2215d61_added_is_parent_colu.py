"""added is_parent column

Revision ID: 2935d2215d61
Revises: cd38e1164d7
Create Date: 2013-09-01 23:07:22.883659

"""

# revision identifiers, used by Alembic.
revision = '2935d2215d61'
down_revision = 'cd38e1164d7'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('issues', sa.Column('is_parent', sa.Boolean(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('issues', 'is_parent')
    ### end Alembic commands ###
