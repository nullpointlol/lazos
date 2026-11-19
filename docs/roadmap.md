# Roadmap

## ✅ Implementado

- [x] Sistema de posts con 1-3 imágenes
- [x] Filtros dinámicos con cascada (provincia → localidades)
- [x] Mapa interactivo con Leaflet
- [x] Sistema de avisos rápidos
- [x] Búsqueda unificada
- [x] Reportes y moderación con panel admin
- [x] **Validación híbrida de imágenes** (Python NSFW + Cloudflare AI Workers)
- [x] **Validación inteligente de texto** (Cloudflare AI - Llama-3-8b)
- [x] **Sistema de aprobación de posts** (pending_approval con metadata de validación)
- [x] **Sistema de reportes unificado** (incluye corrección de ubicación)
- [x] **Numeración secuencial de posts** (post_number)
- [x] Tema día/noche
- [x] PWA con prompt de instalación
- [x] Geocodificación con API Georef (3,979 localidades de Argentina)

## ✅ Phase 1: Foundation - Automated Testing

**Goal:** Establish the missing test infrastructure to ensure stability before implementing the remaining CLIP and PWA features.

**Tasks:**
- [x] **Backend:** Set up `pytest` and `httpx`.
- [x] **Backend:** Create DB fixtures and implement integration tests for critical API endpoints (`/api/v1/posts`, `/api/v1/alerts`, `/api/v1/search`).
- [x] **Frontend:** Set up `vitest` and `@testing-library/react`.
- [x] **Frontend:** Write tests for critical components, specifically `PostCard`, `FilterBar`, `ReportModal`, and `MapView`.

## 🚧 Phase 2: Finalize Core Features (CLIP Integration)

**Goal:** Complete the high-priority "killer feature" of image similarity search.

**Tasks:**
- [ ] Install necessary embedding dependencies in the backend.
  - **Validation / Acceptance Criteria:** `pgvector` and `transformers` (for CLIP) installed and importable in `lazos-api`.
- [ ] Create `app/services/embedding.py` to handle the generation of vector embeddings.
  - **Validation / Acceptance Criteria:** `app/services/embedding.py` exists with a `generate_embedding` function that takes an image path and returns a vector.
- [ ] Modify `create_post()` in `app/api/routes/posts.py` to generate and save the embedding to `post.embedding` upon creation.
  - **Validation / Acceptance Criteria:** New posts have `embedding` field populated with a valid vector after creation.
- [ ] Implement the `POST /api/v1/search/similar` endpoint utilizing PostgreSQL's pgvector (`ORDER BY embedding <=> $1 LIMIT 10`).
  - **Validation / Acceptance Criteria:** Endpoint `/api/v1/search/similar` returns a list of similar posts based on image embedding.
- [ ] Update the frontend `/buscar` page to include an image upload UI for similarity searches.
  - **Validation / Acceptance Criteria:** Frontend `/buscar` page displays an image upload component and shows search results from the similarity endpoint.

## 🛡️ Phase 3: Application Hardening (Security & PWA)

**Goal:** Make the application production-ready, secure, and installable on mobile devices.

**Tasks:**
- [ ] **Rate Limiting:** Install `slowapi` and configure it in `app/main.py`. Set GET limits to 100 req/
  - **Validation / Acceptance Criteria:** `slowapi` is integrated, and API requests beyond the limit receive a 429 Too Many Requests response.
