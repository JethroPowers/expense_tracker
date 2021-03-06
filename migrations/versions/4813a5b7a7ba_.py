"""empty message

Revision ID: 4813a5b7a7ba
Revises: 161f26b6e775
Create Date: 2021-01-19 13:46:06.447962

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4813a5b7a7ba'
down_revision = '161f26b6e775'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Expense_Tracker', sa.Column('belongs_to', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'Expense_Tracker', 'users', ['belongs_to'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'Expense_Tracker', type_='foreignkey')
    op.drop_column('Expense_Tracker', 'belongs_to')
    # ### end Alembic commands ###
