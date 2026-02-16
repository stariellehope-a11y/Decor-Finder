# Architecture

## Overview

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────────┐
│  Next.js UI  │────▶│  FastAPI      │────▶│  PostgreSQL         │
│  (Phase 2)   │     │  /api/v1/     │     │  + pgvector         │
└─────────────┘     └──────┬───────┘     └─────────────────────┘
                           │                        ▲
                    ┌──────▼───────┐               │
                    │  CLIP Model   │               │
                    │  (open_clip)  │               │
                    └──────────────┘               │
                                                    │
┌─────────────────────────────────────┐            │
│  Celery Workers                      │────────────┘
│  ├── AliExpress Ingestion           │
│  ├── Image Download + Embedding     │
│  └── Scheduled Re-crawl             │
└──────────────────┬──────────────────┘
                   │
            ┌──────▼───────┐
            │  AliExpress   │
            │  Affiliate API│
            └──────────────┘
```

## Data Flow

### Search (user-facing)
1. User submits text query OR image upload
2. FastAPI passes input to CLIP model
3. CLIP generates a 512-dim embedding vector
4. pgvector finds nearest neighbors (cosine similarity)
5. SQL filters applied (price, category, retailer)
6. Results ranked and returned with similarity scores

### Ingestion (background)
1. Celery worker queries AliExpress API by category
2. Products stored in PostgreSQL
3. Product images downloaded and embedded via CLIP
4. Embeddings stored in pgvector column
5. Scheduled re-crawl updates prices and availability

## Key Design Decisions

### Why pgvector over Pinecone/Weaviate?
- Single database for relational + vector data
- No additional service to manage
- SQL filters + vector search in one query
- Free, self-hosted, no vendor lock-in
- Sufficient for <1M products (our MVP scale)

### Why CLIP?
- Shared embedding space for images AND text
- User can search by photo or description — same underlying engine
- Pre-trained on massive internet data — understands aesthetic concepts
- Open source (open_clip) — no API costs for embeddings

### Why AliExpress first?
- Free affiliate API with product search
- Massive catalog (millions of home/decor items)
- Images included in API response
- Price data enables "find cheaper" use case
- No approval wait (unlike Wayfair partner API)

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/search/?q=` | Text similarity search |
| POST | `/api/v1/search/image` | Image similarity search |
| GET | `/api/v1/search/similar/{id}` | Find similar products |
| GET | `/api/v1/products/{id}` | Product detail |
| GET | `/api/v1/products/` | List/filter products |
| GET | `/api/v1/products/stats/summary` | Catalog stats |
| GET | `/health` | Health check |

## Similarity Scoring

Weights applied during ranking:
- **Silhouette similarity**: 0.30 (from CLIP geometric features)
- **Material similarity**: 0.25
- **Style/era similarity**: 0.20
- **Color harmony**: 0.15
- **Price proximity**: 0.10

MVP uses raw CLIP cosine similarity. Weighted scoring comes in v2 with attribute classifiers.
