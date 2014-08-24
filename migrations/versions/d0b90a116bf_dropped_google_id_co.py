"""dropped google_id column

Revision ID: d0b90a116bf
Revises: e310107276c
Create Date: 2014-03-21 01:17:27.604889

"""

# revision identifiers, used by Alembic.
revision = 'd0b90a116bf'
down_revision = 'e310107276c'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', u'google_id')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column(u'google_id', sa.VARCHAR(length=255), nullable=True))
    ### end Alembic commands ###