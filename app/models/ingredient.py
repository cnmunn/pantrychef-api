"""Ingredient model for recipe components and pantry items."""

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.pantry import PantryItem
    from app.models.recipe import RecipeIngredient


class Ingredient(Base):
    """Ingredient model representing items that can be used in recipes."""

    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    category: Mapped[str] = mapped_column(
        String(50), index=True, nullable=False
    )  # e.g., produce, dairy, protein, grains, spices, etc.

    # Relationships
    recipe_ingredients: Mapped[list["RecipeIngredient"]] = relationship(
        "RecipeIngredient", back_populates="ingredient", cascade="all, delete-orphan"
    )
    pantry_items: Mapped[list["PantryItem"]] = relationship(
        "PantryItem", back_populates="ingredient", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Ingredient(id={self.id}, name={self.name}, category={self.category})>"
