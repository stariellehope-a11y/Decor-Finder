"""AliExpress product ingestion worker.

Crawls AliExpress categories, downloads product data,
generates CLIP embeddings, and stores in PostgreSQL.
"""

import asyncio
import json
import time
from typing import Optional

from celery import Celery

# Worker config — runs independently from FastAPI
app = Celery("decor_finder", broker="redis://localhost:6379/0")
app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    task_routes={
        "workers.tasks.ingest_aliexpress.*": {"queue": "ingestion"},
    },
)

# AliExpress Home & Garden category IDs (to be populated after API exploration)
HOME_DECOR_CATEGORIES = {
    # These need to be discovered via aliexpress.affiliate.category.get
    # Examples (verify after API access):
    # "Home Decor": "100003070",
    # "Furniture": "100003061",
    # "Lighting": "100003066",
    # "Kitchen": "100003064",
    # "Bathroom": "100003063",
}


@app.task(name="ingest.discover_categories")
def discover_categories():
    """Fetch all AliExpress categories and identify home/decor ones."""
    from app.services.aliexpress import get_aliexpress_client

    async def _run():
        client = get_aliexpress_client()
        result = await client.get_categories()
        return result

    return asyncio.run(_run())


@app.task(name="ingest.crawl_category", bind=True, max_retries=3)
def crawl_category(self, category_id: str, max_pages: int = 20):
    """Crawl all products in a category and queue embedding generation.

    Args:
        category_id: AliExpress category ID
        max_pages: Max pages to crawl (50 products/page)
    """
    from app.services.aliexpress import get_aliexpress_client

    async def _run():
        client = get_aliexpress_client()
        all_products = []

        for page in range(1, max_pages + 1):
            try:
                result = await client.search_products(
                    category_ids=category_id,
                    page_no=page,
                    page_size=50,
                )
                # Extract products from response
                resp = result.get("aliexpress_affiliate_product_query_response", {})
                resp_result = resp.get("resp_result", {})
                products = resp_result.get("result", {}).get("products", {}).get("product", [])

                if not products:
                    break

                all_products.extend(products)
                time.sleep(1)  # Rate limiting

            except Exception as e:
                print(f"Error crawling page {page}: {e}")
                break

        # Queue each product for storage + embedding
        for product in all_products:
            store_product.delay(product)

        return {"category_id": category_id, "products_found": len(all_products)}

    return asyncio.run(_run())


@app.task(name="ingest.store_product", bind=True, max_retries=3)
def store_product(self, product_data: dict):
    """Store a single product and generate its CLIP embedding.

    Args:
        product_data: Raw product dict from AliExpress API
    """
    from app.services.embedding import get_embedding_service

    async def _run():
        # Import here to avoid circular deps
        from sqlalchemy import select
        from app.core.database import async_session
        from app.models.product import Product

        embedder = get_embedding_service()

        # Parse AliExpress product format
        external_id = str(product_data.get("product_id", ""))
        image_url = product_data.get("product_main_image_url", "")
        title = product_data.get("product_title", "")
        product_url = product_data.get("promotion_link", product_data.get("product_detail_url", ""))

        # Price handling
        price_info = product_data.get("target_sale_price", "0")
        original_price_info = product_data.get("target_original_price", "0")
        price = float(str(price_info).replace(",", ""))
        original_price = float(str(original_price_info).replace(",", ""))

        if not external_id or not image_url:
            return {"status": "skipped", "reason": "missing data"}

        async with async_session() as db:
            # Check for existing
            existing = await db.execute(
                select(Product).where(Product.external_id == external_id)
            )
            if existing.scalar_one_or_none():
                return {"status": "exists", "external_id": external_id}

            # Generate CLIP embedding from product image
            embedding = embedder.embed_image_url(image_url)

            product = Product(
                external_id=external_id,
                retailer="aliexpress",
                title=title,
                image_url=image_url,
                product_url=product_url,
                price=price,
                original_price=original_price if original_price > 0 else None,
                currency="USD",
                category=product_data.get("first_level_category_name"),
                image_embedding=embedding.tolist() if embedding is not None else None,
                rating=product_data.get("evaluate_rate"),
            )

            db.add(product)
            await db.commit()

            return {"status": "stored", "external_id": external_id, "embedded": embedding is not None}

    return asyncio.run(_run())


@app.task(name="ingest.full_crawl")
def full_crawl():
    """Trigger a full crawl of all home/decor categories."""
    for name, cat_id in HOME_DECOR_CATEGORIES.items():
        crawl_category.delay(cat_id)
    return {"categories_queued": len(HOME_DECOR_CATEGORIES)}
