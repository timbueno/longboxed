"""empty message

Revision ID: 5a22b3401cfd
Revises: 3b7095f105a6
Create Date: 2014-12-09 21:49:31.372254

"""

# revision identifiers, used by Alembic.
revision = '5a22b3401cfd'
down_revision = '3b7095f105a6'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('diamond_lists',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date_created', sa.DateTime(), nullable=True),
    sa.Column('date', sa.Date(), nullable=True),
    sa.Column('hash_string', sa.String(length=100), nullable=True),
    sa.Column('issue_link_time', sa.DateTime(), nullable=True),
    sa.Column('source', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('hash_string')
    )
    op.create_table('diamonds_issues',
    sa.Column('issue_id', sa.Integer(), nullable=True),
    sa.Column('diamonds_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['diamonds_id'], ['diamond_lists.id'], ),
    sa.ForeignKeyConstraint(['issue_id'], ['issues.id'], ),
    sa.PrimaryKeyConstraint()
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('diamonds_issues')
    op.drop_table('diamond_lists')
    ### end Alembic commands ###
