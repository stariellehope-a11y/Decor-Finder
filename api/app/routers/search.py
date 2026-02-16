"""Search API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.product import SearchResponse
from app.services.search import SearchService

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/", response_model=SearchResponse)
async def search_text(
    q: str = Query(..., description="Text search query (e.g. 'mid-century walnut desk')"),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    category: Optional[str] = Query(None),
    retailer: Optional[str] = Query(None),
    limit: int = Query(24, le=100),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
):
    """Search by text description — uses CLIP to match aesthetic intent."""
    service = SearchService(db)
    return await service.search_by_text(
        query=q,
        min_price=min_price,
        max_price=max_price,
        category=category,
        retailer=retailer,
        limit=limit,
        offset=offset,
    )


@router.post("/image", response_model=SearchResponse)
async def search_image(
    image: UploadFile = File(..., description="Upload an image to find similar products"),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    category: Optional[str] = Query(None),
    retailer: Optional[str] = Query(None),
    limit: int = Query(24, le=100),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
):
    """Search by image — upload a photo, rendering, or screenshot."""
    image_bytes = await image.read()
    service = SearchService(db)
    return await service.search_by_image(
        image_bytes=image_bytes,
        min_price=min_price,
        max_price=max_price,
        category=category,
        retailer=retailer,
        limit=limit,
        offset=offset,
    )


@router.get("/similar/{product_id}", response_model=SearchResponse)
async def find_similar(
    product_id: int,
    limit: int = Query(12, le=50),
    db: AsyncSession = Depends(get_db),
):
    """Find products visually similar to a specific product."""
    service = SearchService(db)
    return await service.find_similar(product_id=product_id, limit=limit)
