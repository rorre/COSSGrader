"""empty message

Revision ID: e664550873ad
Revises: 
Create Date: 2020-07-21 14:05:25.135112

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e664550873ad'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('color', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_roles'))
    )
    with op.batch_alter_table('roles', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_roles_color'), ['color'], unique=False)
        batch_op.create_index(batch_op.f('ix_roles_name'), ['name'], unique=True)

    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(), nullable=False),
    sa.Column('password_hash', sa.String(), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.Text(), nullable=True),
    sa.Column('is_admin', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], name=op.f('fk_users_role_id_roles')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_users'))
    )
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_users_email'), ['email'], unique=True)
        batch_op.create_index(batch_op.f('ix_users_username'), ['username'], unique=True)

    op.create_table('quizzes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('info', sa.Text(), nullable=False),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.Column('open_time', sa.DateTime(), nullable=True),
    sa.Column('close_time', sa.DateTime(), nullable=True),
    sa.Column('show_results', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], name=op.f('fk_quizzes_owner_id_users')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_quizzes'))
    )
    op.create_table('questions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('question', sa.Text(), nullable=False),
    sa.Column('answer', sa.Text(), nullable=False),
    sa.Column('is_essay', sa.Boolean(), nullable=False),
    sa.Column('options', sa.ARRAY(sa.String()), nullable=True),
    sa.Column('quiz_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['quiz_id'], ['quizzes.id'], name=op.f('fk_questions_quiz_id_quizzes')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_questions'))
    )
    op.create_table('submissions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('options', sa.ARRAY(sa.String()), nullable=True),
    sa.Column('scores', sa.ARRAY(sa.Integer()), nullable=True),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.Column('quiz_id', sa.Integer(), nullable=True),
    sa.Column('events', sa.ARRAY(sa.String()), nullable=True),
    sa.Column('start_time', sa.DateTime(), nullable=True),
    sa.Column('is_done', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], name=op.f('fk_submissions_owner_id_users')),
    sa.ForeignKeyConstraint(['quiz_id'], ['quizzes.id'], name=op.f('fk_submissions_quiz_id_quizzes')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_submissions'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('submissions')
    op.drop_table('questions')
    op.drop_table('quizzes')
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_username'))
        batch_op.drop_index(batch_op.f('ix_users_email'))

    op.drop_table('users')
    with op.batch_alter_table('roles', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_roles_name'))
        batch_op.drop_index(batch_op.f('ix_roles_color'))

    op.drop_table('roles')
    # ### end Alembic commands ###
