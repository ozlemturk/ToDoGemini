"""phone number added

Revision ID: 4f61a69d050a
Revises: 
Create Date: 2026-05-10 16:45:25.915050

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4f61a69d050a'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

#Applies the migration
def upgrade() -> None:
    #Adds a nullable phone_number column to the users table.
    op.add_column("users",sa.Column("phone_number",sa.String(),nullable = True))

#Reverts the migration
def downgrade() -> None:
    #Removes the phone_number from the users table.
    #op.drop_column("users", "phone_number")
    pass
