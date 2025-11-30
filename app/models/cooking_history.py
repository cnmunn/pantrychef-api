"""CookingHistory model for tracking what users have cooked."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.recipe import Recipe
    from app.models.user import User


class CookingHistory(Base):
    """CookingHistory model for logging recipes a user has prepared."""

    __tablename__ = "cooking_history"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    recipe_id: Mapped[int] = mapped_column(
        ForeignKey("recipes.id", ondelete="CASCADE"), index=True, nullable=False
    )
    cooked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1-5 star rating
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="cooking_history")
    recipe: Mapped["Recipe"] = relationship("Recipe", back_populates="cooking_history")

    def __repr__(self) -> str:
        return f"<CookingHistory(id={self.id}, user_id={self.user_id}, recipe_id={self.recipe_id})>"
