# Changelog

Todas las modificaciones notables al proyecto LAZOS están documentadas en este archivo.

Formato basado en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/).

---

## [Día 5] - 2025-12-29

### Fixed
- Corregido carga de localidades desde Nominatim con parámetros correctos
- Convertido campo localidad de input a verdadero desplegable con búsqueda
- Mejorada UX y validación de ubicación manual con direcciones completas
- Agregado manejo de errores detallado para imágenes R2

### Added
- Guía configuración Cloudflare R2 para imágenes públicas (`CLOUDFLARE_R2_CONFIG.md`)
- Constantes de 24 provincias argentinas (`lib/constants.js`)
- Componente Select siguiendo patrón shadcn/ui
- Logs detallados en Nominatim y carga de localidades

### Changed
- Label "Altura" → "Altura aproximada *"
- Validación ahora requiere TODOS los campos: Calle + Altura + Localidad + Provincia
- Query Nominatim usa dirección completa para coordenadas precisas
- Localidad: desplegable que se abre al hacer click, muestra 20 primeras opciones
- Filtrado de localidades con matching parcial (ej: "Ballester" encuentra "Villa Ballester")

---

## [Día 4] - 2025-12-28

### Added
- Componentes UI shadcn: Input, Label, Textarea
- Página NewPost (`/new`) con formulario completo (472 líneas)
- Upload de imagen con preview y validación
- Geolocalización automática con Navigator API
- Reverse geocoding con Nominatim (OpenStreetMap)
- Campos: imagen, ubicación, tipo, sexo, tamaño, fecha, descripción, contacto
- Validación en cliente antes de enviar
- Integración con FAB para navegar a `/new`

### Changed
- FAB ahora navega a `/new` en lugar de mostrar alert

---

## [Día 3] - 2025-12-27

### Added
- Proyecto React 18 + Vite 5
- Tailwind CSS 3.4 + shadcn/ui
- Componentes UI: Button, Card
- Layout con Header fijo y BottomNav
- Navegación inferior con 3 botones: Home, Search, Map
- PostCard component con thumbnail, sexo, tamaño, ubicación, descripción
- FAB (Floating Action Button)
- Páginas: Home (funcional), Search (placeholder), Map (placeholder)
- Hook usePosts para fetch de API
- Grilla responsive (2/3/4 columnas)
- Estados: loading (skeleton), error, empty

### Changed
- CORS backend configurado para localhost:5173

---

## [Día 2] - 2025-12-26

### Added
- Servicio de procesamiento de imágenes (`app/services/image.py`)
  - Resize a máx 2000px (lado mayor)
  - Generación de thumbnails 400x400px
  - Compresión JPEG quality 85%
  - Validación tamaño max 10MB
- Servicio de storage Cloudflare R2 (`app/services/storage.py`)
  - Upload con boto3 (S3-compatible)
  - Delete de imágenes
  - Singleton pattern
- Endpoint GET `/api/v1/map/points`
  - Filtros por bounds, animal_type, size, sex, fechas
  - Usa PostGIS ST_Within
  - Límite configurable (default 500, max 1000)

### Changed
- Endpoint POST `/api/v1/posts` ahora recibe multipart/form-data
- Campo `image` tipo UploadFile en lugar de URL string
- URLs guardadas son reales de Cloudflare R2

### Fixed
- Configuración de Supabase PostgreSQL
- Configuración de Cloudflare R2
- Dependencies: boto3 agregado

---

## [Día 1] - 2025-12-25

### Added
- Estructura backend FastAPI completa
- Modelos SQLAlchemy 2.0: Post, User (opcional)
- Enums: SexEnum, SizeEnum, AnimalEnum
- Pydantic schemas v2: PostCreate, PostResponse, PostUpdate, PostListResponse
- Endpoints CRUD para posts:
  - GET `/api/v1/posts` - Lista paginada con filtros
  - GET `/api/v1/posts/{id}` - Detalle
  - POST `/api/v1/posts` - Crear (placeholder image_url)
  - PATCH `/api/v1/posts/{id}` - Actualizar
  - DELETE `/api/v1/posts/{id}` - Soft delete
- Health check: GET `/health`
- Documentación automática: `/docs`, `/redoc`
- Docker Compose con PostgreSQL 16 + PostGIS + pgvector
- Alembic migrations setup
- Migración inicial con tablas, índices, constraints
- pytest configurado con tests básicos
- `.env.example` con variables documentadas
- Archivos: `TESTING.md`, `verify.sh`

### Technical
- SQLAlchemy 2.0 con type hints
- Pydantic Settings para config
- CORS middleware configurado
- Dependency injection con `get_db()`
- Índices: espacial (GIST), vectorial (HNSW), B-tree
- Campo `embedding` (Vector) para CLIP futuro
- Campo `user_id` nullable (posts anónimos permitidos)

---

## [Unreleased]

### Planned
- Página Search con filtros funcional
- Página Map con Leaflet
- Búsqueda por similitud con CLIP embeddings
- PWA (manifest, service worker)
- Autenticación JWT
- Sistema de usuarios completo
- Notificaciones (email/push)
- Moderación de contenido

### Known Issues
- Imágenes no se muestran (bucket R2 no público) - Ver `CLOUDFLARE_R2_CONFIG.md`
- Sin tests en frontend
- Coverage backend ~5%
- Sin structured logging
- Sin error tracking (Sentry)
- Sin caching de API

---

## Formato de Commits

Este proyecto usa commits convencionales:

```
type: description

Types:
- feat: Nueva feature
- fix: Bug fix
- docs: Documentación
- chore: Mantenimiento
- test: Tests
- refactor: Refactoring
- perf: Performance
```

Ejemplos:
```
feat: Add map page with Leaflet markers
fix: Correct image upload validation
docs: Update README with deployment steps
chore: Update dependencies to latest
test: Add tests for posts CRUD
refactor: Simplify storage service
```
