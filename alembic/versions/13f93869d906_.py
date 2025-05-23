"""empty message

Revision ID: 13f93869d906
Revises: 657b6d394559
Create Date: 2025-03-04 18:50:48.030681

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '13f93869d906'
down_revision: Union[str, None] = '657b6d394559'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('dni', sa.String(length=50), nullable=False))
    op.create_unique_constraint(None, 'users', ['dni'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='unique')
    op.drop_column('users', 'dni')
    # ### end Alembic commands ###
