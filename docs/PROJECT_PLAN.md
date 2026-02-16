# Decor Finder — Project Plan

## Vision
AI-powered aesthetic search engine that translates visual taste into purchasable real-world objects across retailers. Users search by vibe, not by product name.

## Problem
- Google Shopping → literal keyword matching
- Pinterest → inspiration without purchasing
- Retailers → siloed inventories
- Reverse image search → object recognition, not style matching
- AI chatbots → hallucinated products with dead links

## Target Users

**Primary:** Interior designers, homeowners, property developers staging homes, Airbnb owners, architectural visualization artists

**Secondary:** Retail buyers, hospitality sourcing managers, set designers, content creators

---

## Input Types
- Text description ("warm minimalist oak console table")
- Photo upload
- Rendering / 3D visualization
- Moodboard
- Hybrid text + image

## Output
Pinterest-style masonry board with: image, title, price, similarity score, retailer, product link

---

## Retailer Strategy

### Phase 1 — AliExpress Only (MVP)
- Free affiliate API
- Massive catalog for home/decor
- Images included in API response
- Enables "find the cheaper version" use case
- **Status: API keys pending approval**

### Phase 2 — Premium Retailers
| Retailer | Access Method | Priority |
|----------|--------------|----------|
| Wayfair | Partner API (requires approval) | High |
| Etsy | Open API v3 (free tier) | High |
| West Elm | CJ Affiliate product feed | Medium |
| CB2 | CJ Affiliate product feed | Medium |
| Anthropologie | CJ/ShareASale feed | Medium |
| IKEA | Scraper | Medium |
| Article | Scraper | Medium |

### Phase 3 — Luxury + Wholesale
| Retailer | Access Method | Priority |
|----------|--------------|----------|
| 1stDibs | Scraper | High |
| RH | Scraper | Medium |
| Soho Home | Scraper | Medium |
| Design Within Reach | Scraper | Medium |
| Perigold | Wayfair Partner API | Medium |
| Alibaba/1688 | Future API integration | Low |

### Affiliate Networks (bulk product feeds)
- **CJ Affiliate** — West Elm, CB2, Anthropologie, Crate & Barrel
- **ShareASale** — many home/decor brands
- **Rakuten** — similar coverage

---

## Tech Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Frontend | Next.js 14+ / Tailwind | Masonry grid, SSR, React ecosystem |
| Backend | Python / FastAPI | ML ecosystem native, async |
| Database | PostgreSQL + pgvector | Vector + relational in one DB, free |
| AI/ML | CLIP (open_clip ViT-B-32) | Unified image+text embeddings, open source |
| Queue | Redis + Celery | Async product ingestion |
| Storage | S3-compatible | Product image cache |
| Deploy | Docker Compose → Railway/Fly.io | Simple MVP hosting |

### APIs Required
1. **AliExpress Open Platform** (affiliate) — product data
2. **open_clip** (self-hosted) — CLIP embeddings (no API cost)
3. **OpenAI Vision** (optional, future) — richer attribute extraction

---

## AI/ML Pipeline

### Embedding Generation
- CLIP ViT-B-32 generates 512-dim vectors
- Same model embeds both images and text into shared vector space
- Users can search by photo OR description — same underlying engine

### Extracted Attributes (v2+)
- Style (mid-century, minimalist, bohemian, industrial, etc.)
- Category (desk, lamp, sofa, shelf, etc.)
- Material (wood, metal, fabric, glass, etc.)
- Color palette
- Era/period
- Geometry/silhouette
- Quality tier
- Budget bracket

### Similarity Scoring

**MVP:** Raw CLIP cosine similarity via pgvector

**v2 Weighted Scoring:**
| Factor | Weight |
|--------|--------|
| Silhouette similarity | 0.30 |
| Material similarity | 0.25 |
| Style/era similarity | 0.20 |
| Color harmony | 0.15 |
| Price proximity | 0.10 |

### Ranking Engine
- Criteria: similarity, price adherence, retailer diversity, availability, visual variety
- Anti-duplicate: diversity penalty (prevents same item from one retailer dominating)
- Image hash clustering for deduplication across retailers

---

## MVP Roadmap

### Phase 1: Data Pipeline + Search Core (Weeks 1-4)
- [x] Project scaffold (FastAPI, models, services, workers)
- [x] AliExpress API client
- [x] CLIP embedding service
- [x] Vector similarity search engine
- [x] Docker Compose dev environment
- [ ] **AliExpress API keys** (pending approval)
- [ ] Discover home/decor category IDs
- [ ] Run first product ingestion (target: 50k products)
- [ ] Validate search quality with test queries
- [ ] Alembic migrations for schema versioning

### Phase 2: Frontend + Live Filters (Weeks 5-8)
- [ ] Next.js project setup
- [ ] Masonry grid board UI
- [ ] Text search bar
- [ ] Image upload search
- [ ] Live price slider filtering
- [ ] Product card (image, title, price, score, retailer link)
- [ ] "Find similar" button per product
- [ ] Responsive design (mobile-first)
- [ ] Hover details interaction

### Phase 3: Multi-Retailer + Polish (Weeks 9-12)
- [ ] CJ Affiliate feed integration (West Elm, CB2)
- [ ] Etsy API integration
- [ ] Cross-retailer deduplication
- [ ] Scheduled re-crawl for price/availability updates
- [ ] Category and material filters
- [ ] Search result caching

### Phase 4: Personalization + Pro (Future)
- [ ] Saved taste profiles
- [ ] "Cheaper version" / "Luxury upgrade" buttons
- [ ] Room-level search (detect multiple items in one photo)
- [ ] Material filters
- [ ] Availability detection
- [ ] Pro designer subscription tier
- [ ] Auto sourcing list export
- [ ] Real estate developer API

---

## Monetization (Future)
- **Primary:** Affiliate revenue (commission on click-throughs)
- **Secondary:** Pro designer subscription
- **Future:** Real estate developer API access

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Scraping blocks | Rotating proxies, aggressive caching, prefer APIs |
| Bad similarity results | Custom fine-tuned model on interior/decor dataset |
| Duplicate items across retailers | Image hash clustering + embedding distance dedup |
| Price drift / stale links | Scheduled re-crawl workers |
| CLIP model too generic | Fine-tune on curated decor dataset (v2) |
| pgvector scale limits | Migrate to dedicated vector DB if >1M products |

---

## Current Status
- **Repo:** https://github.com/stariellehope-a11y/Decor-Finder
- **Scaffold:** Complete (FastAPI + CLIP + pgvector + AliExpress client + Celery workers)
- **Blocker:** Waiting on AliExpress API key approval
- **Next action:** Once keys arrive → discover categories → run first ingestion → validate search quality
