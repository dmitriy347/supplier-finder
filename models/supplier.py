from typing import Optional
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

class Supplier(Base):
    __tablename__ = "supplier"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False, index=True)
    region: Mapped[str] = mapped_column(String, nullable=False, index=True)
    contacts: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    min_order_qty: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    price_range: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    has_certificates: Mapped[bool] = mapped_column(Boolean, default=False)
    delivery_conditions: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)
