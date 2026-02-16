# Decor Finder 🔍

AI-powered aesthetic search engine for furniture and decor. Translate visual taste into purchasable real-world objects across retailers.

## The Problem

People search for decor by *vibe*, not by product name. Existing tools fail:
- **Google Shopping** — literal keyword matching
- **Pinterest** — inspiration without purchasing
- **Retailers** — siloed inventories
- **Reverse image search** — object recognition, not style matching
- **AI chatbots** — hallucinated products with dead links

## How It Works

1. **Search by image or description** — upload a photo, rendering, or describe what you want
2. **AI understands aesthetics** — CLIP embeddings capture style, material, era, geometry
3. **Get real, purchasable results** — ranked by visual similarity with live retailer links

## Architecture

```
[Next.js Frontend] → [FastAPI Backend] → [PostgreSQL + pgvector]
                                      → [CLIP Embedding Service]
                                      → [AliExpress Ingestion Workers]
```

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Frontend | Next.js 14+ / Tailwind | Masonry grid, SSR, fast |
| Backend | Python / FastAPI | ML ecosystem native, async |
| Database | PostgreSQL + pgvector | Vector similarity + relational in one DB |
| AI/ML | CLIP (open_clip) | Unified image+text embeddings |
| Queue | Redis + Celery | Async product ingestion |
| Storage | S3-compatible | Product image cache |

## Project Structure

```
├── api/                  # FastAPI backend
│   ├── app/
│   │   ├── core/         # Config, database, dependencies
│   │   ├── models/       # SQLAlchemy + Pydantic models
│   │   ├── routers/      # API endpoints
│   │   └── services/     # Business logic (search, ingestion, embeddings)
│   └── tests/
├── workers/              # Celery ingestion workers
│   ├── tasks/            # AliExpress sync, embedding generation
│   └── tests/
├── web/                  # Next.js frontend (Phase 2)
├── infrastructure/       # Docker, deployment configs
└── docs/                 # Architecture decisions, API docs
```

## MVP Roadmap

### Phase 1: Data Pipeline + Search Core
- [ ] AliExpress API integration (affiliate)
- [ ] Product ingestion pipeline (Home Decor categories)
- [ ] CLIP embedding generation for product images
- [ ] Vector similarity search (pgvector)
- [ ] Text → embedding → search
- [ ] Image → embedding → search
- [ ] Price + category filters

### Phase 2: Frontend + Live Filters
- [ ] Masonry grid board UI
- [ ] Image upload search
- [ ] Live price slider
- [ ] Product detail + "find similar"
- [ ] Retailer click-through

### Phase 3: Multi-Retailer + Personalization
- [ ] Additional retailer APIs (Wayfair, Etsy, CJ feeds)
- [ ] Saved taste profiles
- [ ] "Cheaper version" / "Luxury upgrade" buttons
- [ ] Room-level search

## Getting Started

```bash
# Clone
git clone https://github.com/stariellehope-a11y/Decor-Finder.git
cd Decor-Finder

# Backend
cd api
cp .env.example .env          # Add your API keys
pip install -r requirements.txt
uvicorn app.main:app --reload

# Workers
cd workers
celery -A tasks worker --loglevel=info

# Frontend (Phase 2)
cd web
npm install && npm run dev
```

## API Keys Required

- **AliExpress Open Platform** — Register at [open.aliexpress.com](https://open.aliexpress.com)
- **OpenAI** (optional) — For enhanced attribute extraction

## License

Private — All rights reserved.
