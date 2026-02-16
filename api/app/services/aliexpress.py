"""AliExpress Open Platform API client.

Docs: https://open.aliexpress.com
Uses the Affiliate API for product search and details.

Required: Register at open.aliexpress.com → get app_key + app_secret + tracking_id
"""

import hashlib
import hmac
import time
from typing import Optional
from urllib.parse import urlencode

import httpx

from app.core.config import get_settings

settings = get_settings()

API_BASE = "https://api-sg.aliexpress.com/sync"


class AliExpressClient:
    """Client for AliExpress Affiliate API."""

    def __init__(self):
        self.app_key = settings.aliexpress_app_key
        self.app_secret = settings.aliexpress_app_secret
        self.tracking_id = settings.aliexpress_tracking_id
        self.http = httpx.AsyncClient(timeout=30)

    def _sign(self, params: dict) -> str:
        """Generate HMAC-SHA256 signature for API request."""
        sorted_params = sorted(params.items())
        sign_str = "".join(f"{k}{v}" for k, v in sorted_params)
        sign_str = self.app_secret + sign_str + self.app_secret
        return hmac.new(
            self.app_secret.encode(), sign_str.encode(), hashlib.sha256
        ).hexdigest().upper()

    def _base_params(self, method: str) -> dict:
        return {
            "app_key": self.app_key,
            "method": method,
            "sign_method": "hmac-sha256",
            "timestamp": str(int(time.time() * 1000)),
            "v": "2.0",
        }

    async def search_products(
        self,
        keywords: Optional[str] = None,
        category_ids: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        page_no: int = 1,
        page_size: int = 50,
        sort: str = "SALE_PRICE_ASC",
    ) -> dict:
        """Search products via aliexpress.affiliate.product.query.

        Args:
            keywords: Search terms
            category_ids: Comma-separated category IDs
            min_price: Minimum price in USD
            max_price: Maximum price in USD
            page_no: Page number (1-indexed)
            page_size: Results per page (max 50)
            sort: SALE_PRICE_ASC, SALE_PRICE_DESC, LAST_VOLUME_ASC, LAST_VOLUME_DESC

        Returns:
            API response with product list
        """
        params = self._base_params("aliexpress.affiliate.product.query")
        params["tracking_id"] = self.tracking_id

        if keywords:
            params["keywords"] = keywords
        if category_ids:
            params["category_ids"] = category_ids
        if min_price is not None:
            params["min_sale_price"] = str(min_price)
        if max_price is not None:
            params["max_sale_price"] = str(max_price)

        params["page_no"] = str(page_no)
        params["page_size"] = str(page_size)
        params["sort"] = sort
        params["target_currency"] = "USD"
        params["target_language"] = "EN"

        params["sign"] = self._sign(params)

        response = await self.http.get(API_BASE, params=params)
        response.raise_for_status()
        return response.json()

    async def get_product_detail(self, product_ids: list[str]) -> dict:
        """Get detailed product info via aliexpress.affiliate.productdetail.get.

        Args:
            product_ids: List of product IDs (max 50)

        Returns:
            API response with product details
        """
        params = self._base_params("aliexpress.affiliate.productdetail.get")
        params["tracking_id"] = self.tracking_id
        params["product_ids"] = ",".join(product_ids[:50])
        params["target_currency"] = "USD"
        params["target_language"] = "EN"

        params["sign"] = self._sign(params)

        response = await self.http.get(API_BASE, params=params)
        response.raise_for_status()
        return response.json()

    async def get_categories(self) -> dict:
        """Get all affiliate categories."""
        params = self._base_params("aliexpress.affiliate.category.get")
        params["sign"] = self._sign(params)

        response = await self.http.get(API_BASE, params=params)
        response.raise_for_status()
        return response.json()

    async def get_hot_products(
        self,
        category_ids: Optional[str] = None,
        page_no: int = 1,
        page_size: int = 50,
    ) -> dict:
        """Get trending/hot products — good for initial catalog seeding."""
        params = self._base_params("aliexpress.affiliate.hotproduct.query")
        params["tracking_id"] = self.tracking_id

        if category_ids:
            params["category_ids"] = category_ids

        params["page_no"] = str(page_no)
        params["page_size"] = str(page_size)
        params["target_currency"] = "USD"
        params["target_language"] = "EN"

        params["sign"] = self._sign(params)

        response = await self.http.get(API_BASE, params=params)
        response.raise_for_status()
        return response.json()


# Singleton
_client: Optional[AliExpressClient] = None


def get_aliexpress_client() -> AliExpressClient:
    global _client
    if _client is None:
        _client = AliExpressClient()
    return _client
