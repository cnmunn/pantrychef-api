"""Add dietary and allergen fields to ingredients.

Revision ID: 002
Revises: 001
Create Date: 2025-11-30

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: str | None = "001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add dietary and allergen columns to ingredients table."""
    # Add is_vegetarian column (default True - most ingredients are vegetarian)
    op.add_column(
        "ingredients",
        sa.Column(
            "is_vegetarian",
            sa.Boolean(),
            nullable=False,
            server_default="true",
        ),
    )

    # Add is_vegan column (default True - most plant ingredients are vegan)
    op.add_column(
        "ingredients",
        sa.Column(
            "is_vegan",
            sa.Boolean(),
            nullable=False,
            server_default="true",
        ),
    )

    # Add is_gluten_free column (default True - most whole foods are gluten-free)
    op.add_column(
        "ingredients",
        sa.Column(
            "is_gluten_free",
            sa.Boolean(),
            nullable=False,
            server_default="true",
        ),
    )

    # Add allergens column (comma-separated list of allergen tags)
    op.add_column(
        "ingredients",
        sa.Column(
            "allergens",
            sa.String(length=200),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Remove dietary and allergen columns from ingredients table."""
    op.drop_column("ingredients", "allergens")
    op.drop_column("ingredients", "is_gluten_free")
    op.drop_column("ingredients", "is_vegan")
    op.drop_column("ingredients", "is_vegetarian")
