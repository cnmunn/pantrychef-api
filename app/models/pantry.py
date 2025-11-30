"""PantryItem model for tracking user's ingredient inventory."""

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.ingredient import Ingredient
    from app.models.user import User


class PantryItem(Base):
    """PantryItem model representing ingredients a user has in their kitchen."""

    __tablename__ = "pantry_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    ingredient_id: Mapped[int] = mapped_column(
        ForeignKey("ingredients.id", ondelete="CASCADE"), index=True, nullable=False
    )
    quantity: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # e.g., "2", "500g", "1 bunch"
    unit: Mapped[str | None] = mapped_column(
        String(30), nullable=True
    )  # e.g., "cups", "pieces", "lbs"
    expiration_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="pantry_items")
    ingredient: Mapped["Ingredient"] = relationship("Ingredient", back_populates="pantry_items")

    def __repr__(self) -> str:
        return f"<PantryItem(id={self.id}, user={self.user_id}, ingredient={self.ingredient_id})>"
