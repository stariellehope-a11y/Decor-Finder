"""Search service — vector similarity + filters."""

from typing import Optional

import numpy as np
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product, ProductOut, SearchResponse
from app.services.embedding import get_embedding_service


class SearchService:
    """Hybrid search: CLIP vector similarity + SQL filters."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.embedder = get_embedding_service()

    async def search_by_text(
        self,
        query: str,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        category: Optional[str] = None,
        retailer: Optional[str] = None,
        limit: int = 24,
        offset: int = 0,
    ) -> SearchResponse:
        """Text query → CLIP embedding → vector similarity search."""
        embedding = self.embedder.embed_text(query)
        return await self._vector_search(
            embedding, min_price, max_price, category, retailer, limit, offset, query
        )

    async def search_by_image(
        self,
        image_bytes: bytes,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        category: Optional[str] = None,
        retailer: Optional[str] = None,
        limit: int = 24,
        offset: int = 0,
    ) -> SearchResponse:
        """Image upload → CLIP embedding → vector similarity search."""
        embedding = self.embedder.embed_image(image_bytes)
        return await self._vector_search(
            embedding, min_price, max_price, category, retailer, limit, offset
        )

    async def find_similar(
        self,
        product_id: int,
        limit: int = 12,
    ) -> SearchResponse:
        """Find products visually similar to a given product."""
        stmt = select(Product.image_embedding).where(Product.id == product_id)
        result = await self.db.execute(stmt)
        embedding = result.scalar_one_or_none()

        if embedding is None:
            return SearchResponse(results=[], total=0)

        return await self._vector_search(
            np.array(embedding), limit=limit, offset=0, exclude_id=product_id
        )

    async def _vector_search(
        self,
        embedding: np.ndarray,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        category: Optional[str] = None,
        retailer: Optional[str] = None,
        limit: int = 24,
        offset: int = 0,
        query: Optional[str] = None,
        exclude_id: Optional[int] = None,
    ) -> SearchResponse:
        """Core vector similarity search with SQL filters."""
        embedding_list = embedding.tolist()

        # Cosine distance (pgvector <=> operator)
        distance = Product.image_embedding.cosine_distance(embedding_list)

        # Build filter conditions
        conditions = [Product.image_embedding.isnot(None)]
        if min_price is not None:
            conditions.append(Product.price >= min_price)
        if max_price is not None:
            conditions.append(Product.price <= max_price)
        if category:
            conditions.append(Product.category == category)
        if retailer:
            conditions.append(Product.retailer == retailer)
        if exclude_id:
            conditions.append(Product.id != exclude_id)

        # Query with similarity score
        stmt = (
            select(Product, (1 - distance).label("similarity"))
            .where(and_(*conditions))
            .order_by(distance)
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        rows = result.all()

        # Count total matches
        count_stmt = select(func.count(Product.id)).where(and_(*conditions))
        total = await self.db.scalar(count_stmt)

        products = []
        for product, similarity in rows:
            out = ProductOut.model_validate(product)
            out.similarity_score = round(float(similarity), 4)
            products.append(out)

        return SearchResponse(results=products, total=total or 0, query=query)
