"""Product database model and Pydantic schemas."""

from datetime import datetime
from typing import Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import String, Float, DateTime, Integer, Text, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import get_settings
from app.core.database import Base
from pydantic import BaseModel

settings = get_settings()


class Product(Base):
    """Product stored in the Global Decor Index."""

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # External identifiers
    external_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    retailer: Mapped[str] = mapped_column(String(100), index=True)

    # Product data
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_url: Mapped[str] = mapped_column(String(2000))
    product_url: Mapped[str] = mapped_column(String(2000))
    price: Mapped[float] = mapped_column(Float, index=True)
    original_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="USD")

    # Classification
    category: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    style_tags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array
    materials: Mapped[Optional[str]] = mapped_column(Text, nullable=True)   # JSON array
    colors: Mapped[Optional[str]] = mapped_column(Text, nullable=True)      # JSON array

    # Embeddings
    image_embedding = mapped_column(Vector(settings.embedding_dimension), nullable=True)

    # Metadata
    rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    review_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    __table_args__ = (
        Index(
            "ix_products_embedding",
            image_embedding,
            postgresql_using="ivfflat",
            postgresql_with={"lists": 100},
            postgresql_ops={"image_embedding": "vector_cosine_ops"},
        ),
    )


# --- Pydantic Schemas ---


class ProductOut(BaseModel):
    id: int
    external_id: str
    retailer: str
    title: str
    image_url: str
    product_url: str
    price: float
    original_price: Optional[float] = None
    currency: str = "USD"
    category: Optional[str] = None
    style_tags: Optional[str] = None
    materials: Optional[str] = None
    colors: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    similarity_score: Optional[float] = None

    model_config = {"from_attributes": True}


class SearchRequest(BaseModel):
    query: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    category: Optional[str] = None
    retailer: Optional[str] = None
    limit: int = 24
    offset: int = 0


class SearchResponse(BaseModel):
    results: list[ProductOut]
    total: int
    query: Optional[str] = None
