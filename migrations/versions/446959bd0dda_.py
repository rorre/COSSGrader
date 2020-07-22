"""empty message

Revision ID: 446959bd0dda
Revises: e664550873ad
Create Date: 2020-07-22 11:05:23.919705

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '446959bd0dda'
down_revision = 'e664550873ad'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('reports',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('datetime', sa.DateTime(), nullable=True),
    sa.Column('event', sa.String(), nullable=True),
    sa.Column('submission_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['submission_id'], ['submissions.id'], name=op.f('fk_reports_submission_id_submissions')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_reports'))
    )
    with op.batch_alter_table('submissions', schema=None) as batch_op:
        batch_op.drop_column('events')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('submissions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('events', postgresql.ARRAY(sa.VARCHAR()), autoincrement=False, nullable=True))

    op.drop_table('reports')
    # ### end Alembic commands ###