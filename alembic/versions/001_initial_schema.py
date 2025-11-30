"""Initial schema for PantryChef.

Revision ID: 001
Revises:
Create Date: 2025-11-29

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create initial database schema."""
    # Create users table
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)

    # Create ingredients table
    op.create_table(
        "ingredients",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ingredients_category"), "ingredients", ["category"], unique=False)
    op.create_index(op.f("ix_ingredients_id"), "ingredients", ["id"], unique=False)
    op.create_index(op.f("ix_ingredients_name"), "ingredients", ["name"], unique=True)

    # Create recipes table
    op.create_table(
        "recipes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("instructions", sa.Text(), nullable=False),
        sa.Column("prep_time", sa.Integer(), nullable=True),
        sa.Column("cook_time", sa.Integer(), nullable=True),
        sa.Column("difficulty_level", sa.String(length=20), nullable=True),
        sa.Column("servings", sa.Integer(), nullable=True),
        sa.Column("image_url", sa.String(length=500), nullable=True),
        sa.Column("source_url", sa.String(length=500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_recipes_id"), "recipes", ["id"], unique=False)
    op.create_index(op.f("ix_recipes_title"), "recipes", ["title"], unique=False)

    # Create recipe_ingredients association table
    op.create_table(
        "recipe_ingredients",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("recipe_id", sa.Integer(), nullable=False),
        sa.Column("ingredient_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.String(length=50), nullable=True),
        sa.Column("unit", sa.String(length=30), nullable=True),
        sa.Column("optional", sa.Boolean(), nullable=False, server_default="false"),
        sa.ForeignKeyConstraint(
            ["ingredient_id"],
            ["ingredients.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["recipe_id"],
            ["recipes.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_recipe_ingredients_id"), "recipe_ingredients", ["id"], unique=False)
    op.create_index(
        op.f("ix_recipe_ingredients_ingredient_id"),
        "recipe_ingredients",
        ["ingredient_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_recipe_ingredients_recipe_id"),
        "recipe_ingredients",
        ["recipe_id"],
        unique=False,
    )

    # Create pantry_items table
    op.create_table(
        "pantry_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("ingredient_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.String(length=50), nullable=True),
        sa.Column("unit", sa.String(length=30), nullable=True),
        sa.Column("expiration_date", sa.Date(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["ingredient_id"],
            ["ingredients.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_pantry_items_id"), "pantry_items", ["id"], unique=False)
    op.create_index(
        op.f("ix_pantry_items_ingredient_id"),
        "pantry_items",
        ["ingredient_id"],
        unique=False,
    )
    op.create_index(op.f("ix_pantry_items_user_id"), "pantry_items", ["user_id"], unique=False)

    # Create favorites table
    op.create_table(
        "favorites",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("recipe_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["recipe_id"],
            ["recipes.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "recipe_id", name="uq_user_recipe_favorite"),
    )
    op.create_index(op.f("ix_favorites_id"), "favorites", ["id"], unique=False)
    op.create_index(op.f("ix_favorites_recipe_id"), "favorites", ["recipe_id"], unique=False)
    op.create_index(op.f("ix_favorites_user_id"), "favorites", ["user_id"], unique=False)

    # Create cooking_history table
    op.create_table(
        "cooking_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("recipe_id", sa.Integer(), nullable=False),
        sa.Column(
            "cooked_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("rating", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["recipe_id"],
            ["recipes.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_cooking_history_id"), "cooking_history", ["id"], unique=False)
    op.create_index(
        op.f("ix_cooking_history_recipe_id"),
        "cooking_history",
        ["recipe_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_cooking_history_user_id"),
        "cooking_history",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    """Drop all tables."""
    op.drop_index(op.f("ix_cooking_history_user_id"), table_name="cooking_history")
    op.drop_index(op.f("ix_cooking_history_recipe_id"), table_name="cooking_history")
    op.drop_index(op.f("ix_cooking_history_id"), table_name="cooking_history")
    op.drop_table("cooking_history")

    op.drop_index(op.f("ix_favorites_user_id"), table_name="favorites")
    op.drop_index(op.f("ix_favorites_recipe_id"), table_name="favorites")
    op.drop_index(op.f("ix_favorites_id"), table_name="favorites")
    op.drop_table("favorites")

    op.drop_index(op.f("ix_pantry_items_user_id"), table_name="pantry_items")
    op.drop_index(op.f("ix_pantry_items_ingredient_id"), table_name="pantry_items")
    op.drop_index(op.f("ix_pantry_items_id"), table_name="pantry_items")
    op.drop_table("pantry_items")

    op.drop_index(op.f("ix_recipe_ingredients_recipe_id"), table_name="recipe_ingredients")
    op.drop_index(op.f("ix_recipe_ingredients_ingredient_id"), table_name="recipe_ingredients")
    op.drop_index(op.f("ix_recipe_ingredients_id"), table_name="recipe_ingredients")
    op.drop_table("recipe_ingredients")

    op.drop_index(op.f("ix_recipes_title"), table_name="recipes")
    op.drop_index(op.f("ix_recipes_id"), table_name="recipes")
    op.drop_table("recipes")

    op.drop_index(op.f("ix_ingredients_name"), table_name="ingredients")
    op.drop_index(op.f("ix_ingredients_id"), table_name="ingredients")
    op.drop_index(op.f("ix_ingredients_category"), table_name="ingredients")
    op.drop_table("ingredients")

    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
