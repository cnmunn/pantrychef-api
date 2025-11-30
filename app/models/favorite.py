"""Favorite model for tracking user's favorite recipes."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.recipe import Recipe
    from app.models.user import User


class Favorite(Base):
    """Favorite model representing a user's saved/favorite recipes."""

    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    recipe_id: Mapped[int] = mapped_column(
        ForeignKey("recipes.id", ondelete="CASCADE"), index=True, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="favorites")
    recipe: Mapped["Recipe"] = relationship("Recipe", back_populates="favorites")

    # Constraints
    __table_args__ = (UniqueConstraint("user_id", "recipe_id", name="uq_user_recipe_favorite"),)

    def __repr__(self) -> str:
        return f"<Favorite(id={self.id}, user_id={self.user_id}, recipe_id={self.recipe_id})>"
