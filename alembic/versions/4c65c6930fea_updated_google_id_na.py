"""updated google id name in user model

Revision ID: 4c65c6930fea
Revises: 382352e93a37
Create Date: 2013-08-07 22:31:02.306233

"""

# revision identifiers, used by Alembic.
revision = '4c65c6930fea'
down_revision = '382352e93a37'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('google_id', sa.String(length=255), nullable=True))
    op.drop_column('users', u'googleid')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column(u'googleid', mysql.VARCHAR(length=255), nullable=True))
    op.drop_column('users', 'google_id')
    ### end Alembic commands ###
