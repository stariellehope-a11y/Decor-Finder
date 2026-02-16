"""Product API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.product import Product, ProductOut

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/{product_id}", response_model=ProductOut)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    """Get a single product by ID."""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/", response_model=list[ProductOut])
async def list_products(
    category: Optional[str] = Query(None),
    retailer: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    limit: int = Query(24, le=100),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
):
    """List products with optional filters."""
    stmt = select(Product)
    if category:
        stmt = stmt.where(Product.category == category)
    if retailer:
        stmt = stmt.where(Product.retailer == retailer)
    if min_price is not None:
        stmt = stmt.where(Product.price >= min_price)
    if max_price is not None:
        stmt = stmt.where(Product.price <= max_price)

    stmt = stmt.order_by(Product.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/stats/summary")
async def product_stats(db: AsyncSession = Depends(get_db)):
    """Get catalog summary stats."""
    total = await db.scalar(select(func.count(Product.id)))
    embedded = await db.scalar(
        select(func.count(Product.id)).where(Product.image_embedding.isnot(None))
    )
    retailers = await db.execute(
        select(Product.retailer, func.count(Product.id))
        .group_by(Product.retailer)
    )
    return {
        "total_products": total or 0,
        "embedded_products": embedded or 0,
        "retailers": {r: c for r, c in retailers.all()},
    }
