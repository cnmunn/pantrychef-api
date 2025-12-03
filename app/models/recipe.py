"""Recipe and RecipeIngredient models."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.cooking_history import CookingHistory
    from app.models.favorite import Favorite
    from app.models.ingredient import Ingredient


class Recipe(Base):
    """Recipe model representing a dish that can be prepared."""

    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    instructions: Mapped[str] = mapped_column(Text, nullable=False)
    prep_time: Mapped[int | None] = mapped_column(Integer, nullable=True)  # in minutes
    cook_time: Mapped[int | None] = mapped_column(Integer, nullable=True)  # in minutes
    difficulty_level: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )  # easy, medium, hard
    servings: Mapped[int | None] = mapped_column(Integer, nullable=True)
    calories: Mapped[int | None] = mapped_column(Integer, nullable=True)  # per serving
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    recipe_ingredients: Mapped[list["RecipeIngredient"]] = relationship(
        "RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan"
    )
    favorites: Mapped[list["Favorite"]] = relationship(
        "Favorite", back_populates="recipe", cascade="all, delete-orphan"
    )
    cooking_history: Mapped[list["CookingHistory"]] = relationship(
        "CookingHistory", back_populates="recipe", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Recipe(id={self.id}, title={self.title})>"


class RecipeIngredient(Base):
    """Association table linking recipes to their required ingredients."""

    __tablename__ = "recipe_ingredients"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    recipe_id: Mapped[int] = mapped_column(
        ForeignKey("recipes.id", ondelete="CASCADE"), index=True, nullable=False
    )
    ingredient_id: Mapped[int] = mapped_column(
        ForeignKey("ingredients.id", ondelete="CASCADE"), index=True, nullable=False
    )
    quantity: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # e.g., "2", "1/2", "3-4"
    unit: Mapped[str | None] = mapped_column(
        String(30), nullable=True
    )  # e.g., "cups", "tbsp", "pieces"
    optional: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    recipe: Mapped["Recipe"] = relationship("Recipe", back_populates="recipe_ingredients")
    ingredient: Mapped["Ingredient"] = relationship(
        "Ingredient", back_populates="recipe_ingredients"
    )

    def __repr__(self) -> str:
        return f"<RecipeIngredient(recipe_id={self.recipe_id}, ingredient_id={self.ingredient_id})>"
