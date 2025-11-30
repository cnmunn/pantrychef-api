"""Ingredient model for recipe components and pantry items."""

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
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

    # Dietary flags - most ingredients default to True (suitable for most diets)
    is_vegetarian: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )  # False for meat, poultry, fish, seafood
    is_vegan: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )  # False for all animal products (meat, dairy, eggs, honey)
    is_gluten_free: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )  # False for wheat, barley, rye, and derivatives

    # Allergens - comma-separated list of allergen tags
    # Common allergens: dairy, eggs, nuts, peanuts, shellfish, soy, wheat, fish, sesame
    allergens: Mapped[str | None] = mapped_column(
        String(200), nullable=True
    )  # e.g., "dairy,soy" or "nuts,peanuts"

    # Relationships
    recipe_ingredients: Mapped[list["RecipeIngredient"]] = relationship(
        "RecipeIngredient", back_populates="ingredient", cascade="all, delete-orphan"
    )
    pantry_items: Mapped[list["PantryItem"]] = relationship(
        "PantryItem", back_populates="ingredient", cascade="all, delete-orphan"
    )

    def get_allergen_list(self) -> list[str]:
        """Return allergens as a list of strings."""
        if not self.allergens:
            return []
        return [a.strip().lower() for a in self.allergens.split(",") if a.strip()]

    def __repr__(self) -> str:
        return f"<Ingredient(id={self.id}, name={self.name}, category={self.category})>"
