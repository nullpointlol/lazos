# LAZOS - Guía Completa para Agentes IA

**Versión**: 2.0
**Fecha actualización**: 2025-12-29
**Propósito**: Documentación completa y centralizada para agentes IA que desarrollan o mantienen el proyecto LAZOS

---

## ÍNDICE

1. [Origen y Visión del Proyecto](#1-origen-y-visión-del-proyecto)
2. [Arquitectura Técnica](#2-arquitectura-técnica)
3. [Estado Actual del Proyecto](#3-estado-actual-del-proyecto)
4. [Modelos de Datos](#4-modelos-de-datos)
5. [API Backend](#5-api-backend)
6. [Frontend](#6-frontend)
7. [Flujos Principales](#7-flujos-principales)
8. [Configuración y Deployment](#8-configuración-y-deployment)
9. [Decisiones de Arquitectura](#9-decisiones-de-arquitectura)
10. [Próximos Pasos](#10-próximos-pasos)

---

## 1. ORIGEN Y VISIÓN DEL PROYECTO

### 1.1 Descripción

**LAZOS** es una plataforma colaborativa para reportar avistamientos de mascotas en la vía pública. El objetivo es ayudar a dueños a encontrar sus mascotas perdidas mediante reportes ciudadanos con foto y ubicación.

### 1.2 Propuesta de Valor

| Característica | LAZOS | Competencia |
|----------------|-------|-------------|
| Registro obligatorio | NO (posts anónimos permitidos) | SÍ |
| Consulta sin cuenta | SÍ (API pública) | NO |
| Venta de datos | NUNCA | Sí (ubicación) |
| Enfoque principal | Avistamientos ciudadanos | Dueños buscando |
| Matching con IA | SÍ (CLIP embeddings) | No o básico |
| Avisos rápidos | SÍ (sin fotos, ubicación temporal) | NO |

### 1.3 Usuarios Objetivo

1. **Reportador**: Persona que ve un animal en la calle y quiere ayudar
2. **Buscador**: Dueño que perdió su mascota y busca avistamientos
3. **Moderador**: Admin que revisa reportes de contenido inapropiado

---

## 2. ARQUITECTURA TÉCNICA

### 2.1 Stack Tecnológico

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND                                  │
├─────────────────────────────────────────────────────────────────┤
│  Web App (PWA)                                                   │
│  - Framework: React 18 + Vite 5                                 │
│  - Styling: Tailwind CSS 3.4 + shadcn/ui                        │
│  - Router: React Router DOM 6                                   │
│  - Mapas: Leaflet 1.9.4 + React Leaflet 4.2.1                  │
│  - Icons: Lucide React                                          │
│  - Theme: Día/Noche con CSS variables                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        BACKEND                                   │
├─────────────────────────────────────────────────────────────────┤
│  API REST                                                        │
│  - Framework: Python 3.11 + FastAPI 0.109                       │
│  - ORM: SQLAlchemy 2.0 + GeoAlchemy2                            │
│  - Validación: Pydantic v2                                      │
│  - Migraciones: Alembic 1.13                                    │
│  - Storage: boto3 para Cloudflare R2 (S3-compatible)            │
│  - Image Processing: Pillow 10.2                                │
│  - Email: SMTP para notificaciones                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      PERSISTENCIA                                │
├─────────────────────────────────────────────────────────────────┤
│  Base de datos: PostgreSQL 15+ con extensiones:                 │
│  - PostGIS: queries geoespaciales (Geography POINT)             │
│  - pgvector: embeddings para similitud de imágenes CLIP         │
│  - uuid-ossp: generación de UUIDs                               │
│                                                                  │
│  Storage de imágenes: Cloudflare R2 (S3-compatible)             │
│  - Bucket público con R2.dev subdomain                          │
│  - Organización: /posts/{uuid}.jpg, /posts/{uuid}_thumb.jpg     │
│                                                                  │
│  Servicios externos:                                             │
│  - API Georef (INDEC Argentina): geocodificación precisa        │
│  - Nominatim (OpenStreetMap): reverse geocoding y fallback      │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Estructura de Directorios

```
lazos/
├── lazos-api/              # Backend FastAPI
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py         # Entry point, CORS, routers
│   │   ├── config.py       # Pydantic Settings
│   │   ├── database.py     # SQLAlchemy engine
│   │   ├── api/
│   │   │   ├── deps.py     # Dependency injection (get_db)
│   │   │   └── routes/
│   │   │       ├── posts.py    # CRUD posts + filtros dinámicos
│   │   │       ├── alerts.py   # CRUD alerts (avisos rápidos)
│   │   │       ├── search.py   # Búsqueda unificada
│   │   │       ├── map.py      # Endpoints para mapa
│   │   │       ├── reports.py  # Sistema de reportes
│   │   │       └── admin.py    # Panel de moderación
│   │   ├── models/
│   │   │   ├── post.py         # Post + enums (Sex, Size, Animal)
│   │   │   ├── post_image.py   # PostImage (1:N con Post)
│   │   │   ├── alert.py        # Alert (avisos sin imágenes)
│   │   │   ├── report.py       # Report + ReportReasonEnum
│   │   │   └── user.py         # User (opcional, no usado)
│   │   ├── schemas/
│   │   │   ├── post.py         # PostCreate, PostResponse, etc.
│   │   │   ├── alert.py        # AlertCreate, AlertResponse, etc.
│   │   │   ├── report.py       # ReportCreate, ReportResponse
│   │   │   ├── search.py       # SearchResponse con results
│   │   │   └── common.py       # PaginationMeta, schemas compartidos
│   │   ├── services/
│   │   │   ├── storage.py      # StorageService (Cloudflare R2)
│   │   │   ├── image.py        # ImageService (resize, thumbnail, EXIF)
│   │   │   └── email.py        # EmailService (SMTP notifications)
│   │   └── utils/
│   ├── migrations/             # Alembic migrations
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── lazos-web/              # Frontend React
│   ├── public/
│   │   └── data/
│   │       ├── provincias.json     # 24 provincias Argentina
│   │       └── localidades.json    # 3,979 localidades
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx                 # Router principal
│   │   ├── index.css               # Tailwind + CSS variables
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   ├── Layout.jsx      # Wrapper con BottomNav
│   │   │   │   └── BottomNav.jsx   # Navegación inferior fija
│   │   │   ├── posts/
│   │   │   │   └── PostCard.jsx    # Tarjeta de post
│   │   │   ├── common/
│   │   │   │   └── FAB.jsx         # Floating Action Button
│   │   │   ├── ui/                 # shadcn/ui components
│   │   │   │   ├── button.jsx
│   │   │   │   ├── input.jsx
│   │   │   │   ├── textarea.jsx
│   │   │   │   ├── label.jsx
│   │   │   │   ├── select.jsx
│   │   │   │   └── card.jsx
│   │   │   ├── FilterBar.jsx       # Barra de filtros colapsable
│   │   │   └── ReportModal.jsx     # Modal para reportar contenido
│   │   ├── pages/
│   │   │   ├── Home.jsx            # Feed principal con grilla
│   │   │   ├── Search.jsx          # Búsqueda unificada
│   │   │   ├── Map.jsx             # Mapa con Leaflet
│   │   │   ├── NewPost.jsx         # Formulario crear post (1-3 fotos)
│   │   │   ├── PostDetail.jsx      # Detalle con carousel
│   │   │   ├── Alerts.jsx          # Lista de avisos rápidos
│   │   │   ├── NewAlert.jsx        # Formulario crear aviso
│   │   │   ├── AlertDetail.jsx     # Detalle de aviso
│   │   │   └── Admin.jsx           # Panel de moderación
│   │   ├── hooks/
│   │   │   ├── usePosts.js         # Fetch posts con filtros
│   │   │   ├── useAlerts.js        # Fetch alerts
│   │   │   ├── usePullToRefresh.js # Pull-to-refresh gesture
│   │   │   └── useAutoRefresh.js   # Auto-refresh periódico
│   │   ├── lib/
│   │   │   └── utils.js            # cn() helper para Tailwind
│   │   └── services/
│   │       └── api.js              # Cliente HTTP
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── package.json
│
└── docs/                   # Documentación
    ├── ai/
    │   └── COMPREHENSIVE_GUIDE.md  # Este archivo
    └── README.md           # Índice de documentación
```

---

## 3. ESTADO ACTUAL DEL PROYECTO

### 3.1 Features Implementadas

#### Backend ✅

**Sistema de Posts con Múltiples Imágenes:**
- Upload de 1-3 imágenes por publicación (multipart/form-data)
- Corrección automática de orientación EXIF (`ImageOps.exif_transpose`)
- Resize automático (max 2000px lado mayor)
- Generación de thumbnails (400px cuadrados)
- Compresión JPEG quality 85%
- Storage en Cloudflare R2 con URLs públicas
- Modelo `PostImage` con relación 1:N a `Post`
- Campos: `is_primary` (imagen principal), `display_order` (orden de visualización)

**Sistema de Filtros Dinámicos:**
- Filtros disponibles: provincia, localidad, animal_type, size, sex, date_from, date_to
- Filtros en cascada: provincia → localidades disponibles
- `available_filters` calculados dinámicamente con conteos
- Parsing de `location_name` (formato: "calle número, ciudad, provincia")
- Ordenamiento por `created_at DESC` por defecto
- Soporte para `sort` (created_at o sighting_date) y `order` (asc/desc)

**Geocodificación Argentina:**
- Integración con API Georef (datos oficiales INDEC)
- 3,979 localidades de todas las provincias
- 24 provincias argentinas
- Validación de dirección completa (calle + altura + localidad + provincia)
- Geocodificación precisa (no solo centro de ciudad)
- Nominatim (OpenStreetMap) como fallback
- Reverse geocoding para GPS

**Sistema de Avisos Rápidos (Alerts):**
- Posts sin imágenes para avistamientos temporales
- Campo `direction` (hacia dónde iba el animal)
- Mismo sistema de ubicación que Posts
- Endpoints: GET, POST, DELETE (soft delete)

**Sistema de Reportes y Moderación:**
- Endpoint POST `/api/v1/reports` para reportar posts o alerts
- Razones: `not_animal`, `inappropriate`, `spam`, `other`
- Campo `description` opcional para detalles
- Guarda `reporter_ip` automáticamente
- Notificación automática por email al moderador (SMTP)
- Panel admin: GET `/admin/reports`, POST `/admin/reports/{id}/resolve`, DELETE `/admin/posts/{id}`
- Estadísticas: GET `/admin/stats`

**Búsqueda Unificada:**
- Endpoint GET `/api/v1/search` para buscar en posts y alerts
- Búsqueda en: `description`, `location_name`, `animal_type`
- Filtro por tipo: `posts`, `alerts`, `all`
- Búsqueda por proximidad (lat, lon, radius_km)
- Ordenamiento por distancia cuando hay coordenadas

**Endpoints para Mapa:**
- GET `/api/v1/map/points` (legacy)
- GET `/api/v1/map/points/unified` (posts + alerts unificados)
- Filtrado por bounds (sw_lat, sw_lng, ne_lat, ne_lng)
- Filtros: animal_type, date_from, date_to
- Límite configurable (max 2000 puntos)

**Infraestructura CLIP (Preparada):**
- Campo `embedding VECTOR(512)` en DB
- Índice HNSW para búsqueda rápida
- Endpoint `/search/similar` definido
- **PENDIENTE:** Integrar modelo CLIP, generar embeddings al crear posts

#### Frontend ✅

**Páginas Implementadas:**

1. **Home** (`/`)
   - Feed principal con grilla responsive (2 cols mobile, 3-4 desktop)
   - FilterBar colapsable con filtros dinámicos
   - Pull-to-refresh
   - Auto-refresh cada 5 minutos
   - Indicador "Última actualización: hace X"
   - Loading states con skeletons
   - Empty states diferenciados (sin posts vs sin resultados con filtros)

2. **Search** (`/buscar`)
   - Input de búsqueda con debounce (300ms)
   - Tabs: Todos / Posts / Avisos
   - Resultados con highlight del término buscado
   - Contador de resultados
   - Empty state cuando no hay resultados

3. **Map** (`/mapa`)
   - Mapa interactivo con React Leaflet + Leaflet Cluster
   - Tiles de OpenStreetMap
   - Markers personalizados (naranjas para posts, amarillos para alerts)
   - Popups con thumbnail e info básica
   - Botón "Mi ubicación"
   - Panel de filtros (animal_type)
   - Leyenda con contadores

4. **NewPost** (`/new`)
   - Upload múltiple de imágenes (1-3, max 10MB c/u)
   - Preview con posibilidad de remover
   - Indicador de imagen principal
   - Ubicación GPS o manual con geocodificación (API Georef)
   - Autocompletado de provincias (24) y localidades (3,979)
   - Validación client-side
   - Contador de caracteres (descripción max 1000)

5. **PostDetail** (`/post/:id`)
   - Carousel de imágenes con navegación (prev/next)
   - Swipe gestures en móvil
   - Indicadores de posición (ej: 2/3)
   - Botón reportar
   - Info completa: tipo, sexo, tamaño, ubicación, fecha, descripción
   - Contacto (si disponible)

6. **Alerts** (`/avisos`)
   - Lista de avisos rápidos
   - Cards con emoji y tiempo relativo (hace X minutos/horas)
   - FAB para crear nuevo aviso

7. **NewAlert** (`/avisos/nuevo`)
   - Similar a NewPost pero sin imágenes
   - Campo adicional "dirección" (hacia dónde iba el animal)

8. **AlertDetail** (`/avisos/:id`)
   - Emoji del animal (🐕🐈🐾)
   - Tiempo relativo destacado
   - Dirección del movimiento
   - Botón reportar

9. **Admin** (`/admin`)
   - Login con password (X-Admin-Password header)
   - Dashboard con stats (posts totales, activos, reportes pendientes)
   - Lista de reportes con preview de posts
   - Botones: Ignorar reporte / Eliminar post
   - Link directo para ver post
   - Contador de reportes por post

**Componentes:**

- **PostCard**: Tarjeta de post con thumbnail, indicador de múltiples imágenes, iconos de sexo (♂♀?), truncado de descripción, fecha relativa
- **FilterBar**: Barra de filtros colapsable con badge de filtros activos, contador de publicaciones, chips de filtros activos con botón X, dropdowns de provincia y localidad con conteos, presets de fecha
- **ReportModal**: Modal para reportar contenido con radio buttons, textarea opcional, loading y success states
- **Layout + BottomNav**: Navegación inferior fija con 4 botones (Home, Avisos, Buscar, Mapa)
- **FAB**: Floating Action Button para crear nueva publicación

**Hooks:**

- `usePosts(filters)`: Fetch posts con filtros, retorna `{ posts, loading, error, meta, availableFilters, refetch }`
- `useAlerts(filters)`: Fetch alerts
- `usePullToRefresh()`: Pull-to-refresh gesture
- `useAutoRefresh(callback, interval)`: Auto-refresh periódico con timestamp

**Tema Día/Noche:**
- Sistema completo con CSS variables
- Tonos cálidos para día, oscuros para noche
- Mejor contraste en ambos temas
- Variaciones de hover sutiles
- Toggle en header

### 3.2 Features No Implementadas

**Búsqueda por Similitud CLIP (UI):**
- Backend: Endpoint `/search/similar` definido
- Frontend: Falta UI de upload de imagen
- **PENDIENTE:** Integrar modelo CLIP, generar embeddings al crear posts, mostrar resultados con % de similitud

**PWA Completo:**
- Falta: manifest.json con iconos, service worker para offline, cache de imágenes, install prompt

**Autenticación JWT:**
- Config lista (JWT_SECRET, JWT_ALGORITHM en .env)
- No implementado en MVP
- **DECISIÓN PENDIENTE:** ¿Implementar o permitir posts anónimos?

### 3.3 Bugs Conocidos

**NINGUNO** - Todos los bugs críticos han sido resueltos:
- ✅ Imágenes invertidas de móviles (corregido con ImageOps.exif_transpose)
- ✅ Imágenes no se mostraban (R2_PUBLIC_URL configurado)
- ✅ React error "Objects are not valid" (renderizar departamento.nombre)
- ✅ Localidades incompletas (3,979 localidades cargadas)
- ✅ Ordenamiento alfabético (implementado con localeCompare)
- ✅ react-leaflet incompatible con React 18 (downgradeado a 4.2.1)

---

## 4. MODELOS DE DATOS

### 4.1 Diagrama Entidad-Relación

```
┌──────────────────────────────────────────────────────────────┐
│                          POSTS                                │
├──────────────────────────────────────────────────────────────┤
│ id              UUID PRIMARY KEY                             │
│ image_url       VARCHAR(500) (backward compat)               │
│ thumbnail_url   VARCHAR(500) (backward compat)               │
│ sex             ENUM('male','female','unknown')              │
│ size            ENUM('small','medium','large') NOT NULL      │
│ animal_type     ENUM('dog','cat','other') DEFAULT 'dog'      │
│ description     TEXT (max 1000 chars)                        │
│ location        GEOGRAPHY(POINT, 4326) NOT NULL              │
│ location_name   VARCHAR(200)                                 │
│ sighting_date   DATE NOT NULL                                │
│ created_at      TIMESTAMP DEFAULT NOW()                      │
│ updated_at      TIMESTAMP                                    │
│ is_active       BOOLEAN DEFAULT TRUE                         │
│ contact_method  VARCHAR(200)                                 │
│ embedding       VECTOR(512)  -- CLIP embedding               │
│ user_id         UUID REFERENCES users(id) NULL               │
└──────────────────────────────────────────────────────────────┘
                    │
                    │ 1:N
                    ▼
┌──────────────────────────────────────────────────────────────┐
│                      POST_IMAGES                              │
├──────────────────────────────────────────────────────────────┤
│ id              UUID PRIMARY KEY                             │
│ post_id         UUID REFERENCES posts(id) NOT NULL           │
│ image_url       VARCHAR(500) NOT NULL                        │
│ thumbnail_url   VARCHAR(500) NOT NULL                        │
│ display_order   INTEGER NOT NULL                             │
│ is_primary      BOOLEAN DEFAULT FALSE                        │
│ created_at      TIMESTAMP DEFAULT NOW()                      │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                          ALERTS                               │
├──────────────────────────────────────────────────────────────┤
│ id              UUID PRIMARY KEY                             │
│ description     TEXT NOT NULL                                │
│ animal_type     ENUM('dog','cat','other') DEFAULT 'dog'      │
│ direction       VARCHAR(200)  -- hacia dónde iba             │
│ location        GEOGRAPHY(POINT, 4326) NOT NULL              │
│ location_name   VARCHAR(200)                                 │
│ created_at      TIMESTAMP DEFAULT NOW()                      │
│ is_active       BOOLEAN DEFAULT TRUE                         │
│ user_id         UUID REFERENCES users(id) NULL               │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                         REPORTS                               │
├──────────────────────────────────────────────────────────────┤
│ id              UUID PRIMARY KEY                             │
│ post_id         UUID REFERENCES posts(id) NULL               │
│ alert_id        UUID REFERENCES alerts(id) NULL              │
│ reason          ENUM('not_animal','inappropriate',           │
│                      'spam','other') NOT NULL                │
│ description     TEXT                                         │
│ reporter_ip     VARCHAR(45)                                  │
│ created_at      TIMESTAMP DEFAULT NOW()                      │
│ resolved        BOOLEAN DEFAULT FALSE                        │
│ CONSTRAINT: CHECK ((post_id IS NULL) != (alert_id IS NULL)) │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                          USERS (opcional, no usado)           │
├──────────────────────────────────────────────────────────────┤
│ id              UUID PRIMARY KEY                             │
│ email           VARCHAR(255) UNIQUE                          │
│ password_hash   VARCHAR(255)                                 │
│ created_at      TIMESTAMP DEFAULT NOW()                      │
│ is_active       BOOLEAN DEFAULT TRUE                         │
└──────────────────────────────────────────────────────────────┘
```

### 4.2 Índices PostgreSQL

```sql
-- Posts
CREATE INDEX idx_posts_location ON posts USING GIST (location);
CREATE INDEX idx_posts_created_at ON posts (created_at DESC);
CREATE INDEX idx_posts_sighting_date ON posts (sighting_date DESC);
CREATE INDEX idx_posts_animal_type ON posts (animal_type);
CREATE INDEX idx_posts_size ON posts (size);
CREATE INDEX idx_posts_sex ON posts (sex);
CREATE INDEX idx_posts_active ON posts (is_active) WHERE is_active = TRUE;

-- Embeddings (HNSW para búsqueda rápida)
CREATE INDEX idx_posts_embedding ON posts
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Post Images
CREATE INDEX idx_post_images_post_id ON post_images (post_id);

-- Alerts
CREATE INDEX idx_alerts_location ON alerts USING GIST (location);
CREATE INDEX idx_alerts_created_at ON alerts (created_at DESC);

-- Reports
CREATE INDEX idx_reports_post_id ON reports (post_id);
CREATE INDEX idx_reports_alert_id ON reports (alert_id);
CREATE INDEX idx_reports_resolved ON reports (resolved) WHERE resolved = FALSE;
```

---

## 5. API BACKEND

### 5.1 Endpoints

#### Posts

```yaml
GET /api/v1/posts
  Descripción: Listar posts con filtros dinámicos y paginación
  Query params:
    - page: int (default 1, ge 1)
    - limit: int (default 20, ge 1, le 100)
    - provincia: str (ej: "Buenos Aires")
    - localidad: str (ej: "La Plata")
    - animal_type: str (dog|cat|other)
    - size: str (small|medium|large)
    - sex: str (male|female|unknown)
    - date_from: date (YYYY-MM-DD)
    - date_to: date (YYYY-MM-DD)
    - sort: str (created_at|sighting_date, default created_at)
    - order: str (asc|desc, default desc)
  Response: 200
    {
      "data": [PostResponse],
      "meta": {
        "page": 1,
        "limit": 20,
        "total": 150,
        "total_pages": 8
      },
      "available_filters": {
        "provincias": [
          { "value": "Buenos Aires", "count": 45 },
          { "value": "CABA", "count": 30 }
        ],
        "localidades": [
          { "value": "La Plata", "count": 15, "provincia": "Buenos Aires" }
        ],
        "animal_types": [
          { "value": "dog", "label": "Perros", "count": 80 },
          { "value": "cat", "label": "Gatos", "count": 50 }
        ],
        "sizes": [...],
        "sexes": [...]
      }
    }

GET /api/v1/posts/{id}
  Descripción: Obtener detalle de un post con todas sus imágenes
  Response: 200 PostResponse | 404
    {
      "id": "uuid",
      "sex": "male",
      "size": "medium",
      "animal_type": "dog",
      "description": "...",
      "location_name": "Av. 7 1234, La Plata, Buenos Aires",
      "latitude": -34.921,
      "longitude": -57.954,
      "sighting_date": "2025-12-29",
      "created_at": "2025-12-29T10:30:00",
      "is_active": true,
      "contact_method": "email@example.com",
      "images": [
        {
          "id": "uuid",
          "image_url": "https://pub-xxx.r2.dev/posts/uuid1.jpg",
          "thumbnail_url": "https://pub-xxx.r2.dev/posts/uuid1_thumb.jpg",
          "display_order": 0,
          "is_primary": true
        },
        {
          "id": "uuid",
          "image_url": "https://pub-xxx.r2.dev/posts/uuid2.jpg",
          "thumbnail_url": "https://pub-xxx.r2.dev/posts/uuid2_thumb.jpg",
          "display_order": 1,
          "is_primary": false
        }
      ]
    }

POST /api/v1/posts
  Descripción: Crear post con 1-3 imágenes
  Body (multipart/form-data):
    - images: File[] (1-3 archivos, max 10MB c/u, JPG/PNG/WEBP)
    - latitude: float (required, -90 to 90)
    - longitude: float (required, -180 to 180)
    - size: str (required, small|medium|large)
    - animal_type: str (optional, default dog)
    - sex: str (optional, default unknown)
    - sighting_date: date (required, YYYY-MM-DD)
    - description: str (optional, max 1000 chars)
    - location_name: str (optional, max 200)
    - contact_method: str (optional, max 200)
  Response: 201 PostResponse

PATCH /api/v1/posts/{id}
  Descripción: Actualizar post (sin auth por ahora)
  Body (JSON):
    - sex: str
    - size: str
    - description: str
    - is_active: bool
  Response: 200 PostResponse | 404

DELETE /api/v1/posts/{id}
  Descripción: Soft delete (is_active=False)
  Response: 204 | 404
```

#### Alerts

```yaml
GET /api/v1/alerts
  Descripción: Listar avisos rápidos activos
  Query params: (similares a /posts)
    - page, limit, animal_type, date_from, date_to, sort, order
  Response: 200
    {
      "data": [AlertResponse],
      "meta": { ... }
    }

GET /api/v1/alerts/{id}
  Response: 200 AlertResponse | 404

POST /api/v1/alerts
  Body (JSON):
    - description: str (required, max 1000)
    - animal_type: str (optional, default dog)
    - direction: str (optional, max 200)
    - latitude: float (required)
    - longitude: float (required)
    - location_name: str (optional)
  Response: 201 AlertResponse

DELETE /api/v1/alerts/{id}
  Response: 204 | 404
```

#### Búsqueda

```yaml
GET /api/v1/search
  Descripción: Búsqueda unificada en posts y alerts
  Query params:
    - q: str (búsqueda en description, location_name, animal_type)
    - type: str (posts|alerts|all, default all)
    - lat: float (para búsqueda por proximidad)
    - lon: float (para búsqueda por proximidad)
    - radius_km: float (default 10)
    - limit: int (default 20, max 100)
  Response: 200
    {
      "results": [
        {
          "type": "post",
          "id": "uuid",
          "title": "Perro mediano marrón",
          "snippet": "...texto con <mark>término</mark> destacado...",
          "location_name": "...",
          "thumbnail_url": "...",
          "created_at": "...",
          "distance_km": 2.5  // si lat/lon provisto
        },
        {
          "type": "alert",
          "id": "uuid",
          ...
        }
      ],
      "total": 15
    }

POST /api/v1/search/similar
  Descripción: Búsqueda por similitud de imagen con CLIP
  Body (multipart/form-data):
    - image: File (required)
    - limit: int (default 10, max 50)
    - min_similarity: float (0-1, default 0.7)
  Response: 200
    {
      "data": [
        {
          "post": PostResponse,
          "similarity": 0.89
        }
      ]
    }
  NOTA: Requiere embeddings generados (pendiente)
```

#### Mapa

```yaml
GET /api/v1/map/points/unified
  Descripción: Obtener puntos de posts y alerts para mapa
  Query params:
    - sw_lat, sw_lng, ne_lat, ne_lng: float (bounds del mapa)
    - animal_type: str (filtro opcional)
    - date_from, date_to: date (filtros opcionales)
    - limit: int (default 500, max 2000)
  Response: 200
    {
      "data": [
        {
          "type": "post",
          "id": "uuid",
          "latitude": -34.603,
          "longitude": -58.381,
          "thumbnail_url": "...",
          "animal_type": "dog",
          "size": "medium",
          "location_name": "..."
        },
        {
          "type": "alert",
          "id": "uuid",
          ...
        }
      ],
      "count": 150
    }
```

#### Reportes

```yaml
POST /api/v1/reports
  Descripción: Reportar un post o alert
  Body (JSON):
    - post_id: str (uuid, optional)
    - alert_id: str (uuid, optional)
    - reason: str (required, not_animal|inappropriate|spam|other)
    - description: str (optional, max 1000)
  Response: 201 ReportResponse
  Nota: Guarda reporter_ip automáticamente

GET /api/v1/admin/reports
  Descripción: Listar reportes pendientes (requiere autenticación)
  Headers:
    - X-Admin-Password: str (required)
  Response: 200
    {
      "data": [
        {
          "id": "uuid",
          "post_id": "uuid",
          "alert_id": null,
          "reason": "spam",
          "description": "...",
          "reporter_ip": "1.2.3.4",
          "created_at": "...",
          "resolved": false,
          "post_data": {  // si post_id
            "id": "uuid",
            "thumbnail_url": "...",
            "description": "...",
            ...
          },
          "total_reports": 3  // total de reportes para este post/alert
        }
      ]
    }

POST /api/v1/admin/reports/{id}/resolve
  Headers: X-Admin-Password
  Response: 200 ReportResponse

DELETE /api/v1/admin/posts/{id}
  Descripción: Eliminar post (soft delete is_active=False)
  Headers: X-Admin-Password
  Response: 204

GET /api/v1/admin/stats
  Headers: X-Admin-Password
  Response: 200
    {
      "total_posts": 150,
      "active_posts": 145,
      "total_alerts": 50,
      "active_alerts": 48,
      "pending_reports": 5
    }
```

### 5.2 Schemas Pydantic

**Post:**
```python
class PostResponse(BaseModel):
    id: UUID
    sex: SexEnum  # male/female/unknown
    size: SizeEnum  # small/medium/large
    animal_type: AnimalEnum  # dog/cat/other
    description: str | None
    location_name: str | None
    latitude: float
    longitude: float
    sighting_date: date
    created_at: datetime
    is_active: bool
    contact_method: str | None
    images: list[PostImageResponse]  # array de imágenes

class PostImageResponse(BaseModel):
    id: UUID
    image_url: str
    thumbnail_url: str
    display_order: int
    is_primary: bool
```

**Alert:**
```python
class AlertResponse(BaseModel):
    id: UUID
    description: str
    animal_type: AnimalEnum
    direction: str | None
    location_name: str | None
    latitude: float
    longitude: float
    created_at: datetime
    is_active: bool
```

**Report:**
```python
class ReportCreate(BaseModel):
    post_id: UUID | None = None
    alert_id: UUID | None = None
    reason: ReportReasonEnum  # not_animal/inappropriate/spam/other
    description: str | None = Field(None, max_length=1000)

class ReportResponse(BaseModel):
    id: UUID
    post_id: UUID | None
    alert_id: UUID | None
    reason: ReportReasonEnum
    description: str | None
    reporter_ip: str
    created_at: datetime
    resolved: bool
```

---

## 6. FRONTEND

### 6.1 Estructura de Páginas

**Home (`/`):**
```jsx
// Componentes principales:
// - FilterBar (colapsable con filtros dinámicos)
// - Grilla de PostCards (responsive 2/3/4 cols)
// - Pull-to-refresh indicator
// - Auto-refresh con timestamp

const Home = () => {
  const [filters, setFilters] = useState({})
  const { posts, loading, meta, availableFilters } = usePosts(filters)
  const { isPulling } = usePullToRefresh(() => refetch())
  const { timeAgo } = useAutoRefresh(() => refetch(), 5 * 60 * 1000)

  return (
    <Layout>
      <FilterBar
        filters={filters}
        onFiltersChange={setFilters}
        availableFilters={availableFilters}
        totalResults={meta?.total}
      />
      {loading ? <SkeletonGrid /> : (
        posts.length > 0 ? (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {posts.map(post => <PostCard key={post.id} post={post} />)}
          </div>
        ) : (
          <EmptyState hasFilters={Object.keys(filters).length > 0} />
        )
      )}
      <FAB onClick={() => navigate('/new')} />
    </Layout>
  )
}
```

**PostDetail (`/post/:id`):**
```jsx
// Componentes principales:
// - Carousel de imágenes con navegación
// - Info completa del post
// - Botón reportar
// - ReportModal

const PostDetail = () => {
  const { id } = useParams()
  const [post, setPost] = useState(null)
  const [currentImageIndex, setCurrentImageIndex] = useState(0)
  const [showReportModal, setShowReportModal] = useState(false)

  // Carousel con navegación prev/next
  // Swipe gestures en móvil
  // Indicadores de posición (ej: 2/3)

  return (
    <Layout>
      <div className="max-w-2xl mx-auto p-4">
        <ImageCarousel
          images={post.images}
          currentIndex={currentImageIndex}
          onIndexChange={setCurrentImageIndex}
        />
        <PostInfo post={post} />
        <button onClick={() => setShowReportModal(true)}>
          Reportar
        </button>
        <ReportModal
          postId={post.id}
          isOpen={showReportModal}
          onClose={() => setShowReportModal(false)}
        />
      </div>
    </Layout>
  )
}
```

**Map (`/mapa`):**
```jsx
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import MarkerClusterGroup from 'react-leaflet-cluster'

const Map = () => {
  const [points, setPoints] = useState([])
  const [filters, setFilters] = useState({})
  const mapRef = useRef()

  useEffect(() => {
    const bounds = mapRef.current?.getBounds()
    if (bounds) {
      fetchPoints({
        sw_lat: bounds.getSouthWest().lat,
        sw_lng: bounds.getSouthWest().lng,
        ne_lat: bounds.getNorthEast().lat,
        ne_lng: bounds.getNorthEast().lng,
        ...filters
      })
    }
  }, [filters])

  return (
    <MapContainer center={[-34.603, -58.381]} zoom={12} ref={mapRef}>
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      <MarkerClusterGroup>
        {points.map(point => (
          <Marker
            key={point.id}
            position={[point.latitude, point.longitude]}
            icon={customIcon(point.type)}  // naranja=post, amarillo=alert
          >
            <Popup>
              <img src={point.thumbnail_url} />
              <p>{point.location_name}</p>
              <Link to={`/${point.type}/${point.id}`}>Ver detalle</Link>
            </Popup>
          </Marker>
        ))}
      </MarkerClusterGroup>
    </MapContainer>
  )
}
```

**Admin (`/admin`):**
```jsx
const Admin = () => {
  const [password, setPassword] = useState(localStorage.getItem('adminPassword') || '')
  const [reports, setReports] = useState([])
  const [stats, setStats] = useState({})

  const fetchReports = async () => {
    const res = await fetch('/api/v1/admin/reports', {
      headers: { 'X-Admin-Password': password }
    })
    if (res.ok) {
      setReports(await res.json())
      localStorage.setItem('adminPassword', password)
    }
  }

  return (
    <div className="max-w-6xl mx-auto p-4">
      <h1>Panel de Moderación</h1>
      <Stats stats={stats} />
      <ReportsList
        reports={reports}
        onResolve={handleResolve}
        onDelete={handleDelete}
      />
    </div>
  )
}
```

### 6.2 Hooks Personalizados

**usePosts.js:**
```javascript
export const usePosts = (filters = {}) => {
  const [posts, setPosts] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [meta, setMeta] = useState({})
  const [availableFilters, setAvailableFilters] = useState({})

  const fetchPosts = useCallback(async () => {
    setLoading(true)
    try {
      const queryParams = new URLSearchParams(filters).toString()
      const res = await fetch(`${API_URL}/api/v1/posts?${queryParams}`)
      const data = await res.json()
      setPosts(data.data)
      setMeta(data.meta)
      setAvailableFilters(data.available_filters)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [filters])

  useEffect(() => {
    fetchPosts()
  }, [fetchPosts])

  return { posts, loading, error, meta, availableFilters, refetch: fetchPosts }
}
```

**usePullToRefresh.js:**
```javascript
export const usePullToRefresh = (onRefresh) => {
  const [isPulling, setIsPulling] = useState(false)
  const [pullProgress, setPullProgress] = useState(0)

  useEffect(() => {
    let startY = 0
    const threshold = 100

    const handleTouchStart = (e) => {
      if (window.scrollY === 0) {
        startY = e.touches[0].clientY
      }
    }

    const handleTouchMove = (e) => {
      if (window.scrollY === 0 && startY > 0) {
        const currentY = e.touches[0].clientY
        const diff = currentY - startY
        if (diff > 0) {
          setPullProgress(Math.min(diff / threshold, 1))
          setIsPulling(diff > threshold)
        }
      }
    }

    const handleTouchEnd = () => {
      if (isPulling) {
        onRefresh()
      }
      startY = 0
      setPullProgress(0)
      setIsPulling(false)
    }

    window.addEventListener('touchstart', handleTouchStart)
    window.addEventListener('touchmove', handleTouchMove)
    window.addEventListener('touchend', handleTouchEnd)

    return () => {
      window.removeEventListener('touchstart', handleTouchStart)
      window.removeEventListener('touchmove', handleTouchMove)
      window.removeEventListener('touchend', handleTouchEnd)
    }
  }, [isPulling, onRefresh])

  return { isPulling, pullProgress }
}
```

### 6.3 Componentes Clave

**FilterBar.jsx:**
```jsx
const FilterBar = ({ filters, onFiltersChange, availableFilters, totalResults }) => {
  const [isExpanded, setIsExpanded] = useState(false)
  const activeFiltersCount = Object.keys(filters).filter(k => filters[k]).length

  return (
    <div className="sticky top-0 bg-background border-b shadow-sm z-10">
      <button onClick={() => setIsExpanded(!isExpanded)}>
        <Filter className="h-4 w-4" />
        <span>Filtros</span>
        {activeFiltersCount > 0 && (
          <Badge>{activeFiltersCount}</Badge>
        )}
      </button>

      {isExpanded && (
        <div className="p-4 space-y-4">
          {/* Chips de filtros activos */}
          {activeFiltersCount > 0 && (
            <div className="flex flex-wrap gap-2">
              {Object.entries(filters).map(([key, value]) => (
                value && (
                  <Chip
                    key={key}
                    label={formatFilter(key, value)}
                    onRemove={() => onFiltersChange({ ...filters, [key]: null })}
                  />
                )
              ))}
            </div>
          )}

          {/* Contador de resultados */}
          <p className="text-sm text-muted-foreground">
            {totalResults} publicaciones encontradas
          </p>

          {/* Dropdowns de filtros */}
          <Select
            label="Provincia"
            value={filters.provincia}
            onChange={(val) => onFiltersChange({ ...filters, provincia: val, localidad: null })}
            options={availableFilters.provincias?.map(p => ({
              value: p.value,
              label: `${p.value} (${p.count})`
            }))}
          />

          {filters.provincia && (
            <Select
              label="Localidad"
              value={filters.localidad}
              onChange={(val) => onFiltersChange({ ...filters, localidad: val })}
              options={availableFilters.localidades
                ?.filter(l => l.provincia === filters.provincia)
                .map(l => ({
                  value: l.value,
                  label: `${l.value} (${l.count})`
                }))
              }
            />
          )}

          {/* Botones de filtro */}
          <div>
            <label>Tipo de animal</label>
            <div className="flex gap-2">
              {availableFilters.animal_types?.map(type => (
                <Button
                  key={type.value}
                  variant={filters.animal_type === type.value ? 'default' : 'outline'}
                  onClick={() => onFiltersChange({
                    ...filters,
                    animal_type: filters.animal_type === type.value ? null : type.value
                  })}
                >
                  {type.label} ({type.count})
                </Button>
              ))}
            </div>
          </div>

          {/* Presets de fecha */}
          <div>
            <label>Fecha</label>
            <div className="flex gap-2">
              <Button onClick={() => setDatePreset('today')}>Hoy</Button>
              <Button onClick={() => setDatePreset('week')}>Semana</Button>
              <Button onClick={() => setDatePreset('month')}>Mes</Button>
              <Button onClick={() => setDatePreset('all')}>Todos</Button>
            </div>
          </div>

          <Button variant="ghost" onClick={() => onFiltersChange({})}>
            Limpiar filtros
          </Button>
        </div>
      )}
    </div>
  )
}
```

**ReportModal.jsx:**
```jsx
const ReportModal = ({ postId, alertId, isOpen, onClose }) => {
  const [reason, setReason] = useState('')
  const [description, setDescription] = useState('')
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)

  const handleSubmit = async () => {
    setLoading(true)
    try {
      await fetch('/api/v1/reports', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          post_id: postId,
          alert_id: alertId,
          reason,
          description
        })
      })
      setSuccess(true)
      setTimeout(() => {
        onClose()
        setSuccess(false)
      }, 2000)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Reportar contenido</DialogTitle>
        </DialogHeader>

        {success ? (
          <div>
            <CheckCircle className="text-green-500" />
            <p>Reporte enviado correctamente</p>
          </div>
        ) : (
          <>
            <RadioGroup value={reason} onValueChange={setReason}>
              <RadioGroupItem value="not_animal" label="No es un animal" />
              <RadioGroupItem value="inappropriate" label="Contenido inapropiado" />
              <RadioGroupItem value="spam" label="Spam" />
              <RadioGroupItem value="other" label="Otro" />
            </RadioGroup>

            <Textarea
              placeholder="Descripción adicional (opcional)"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              maxLength={1000}
            />
            <p className="text-xs">{description.length}/1000</p>

            <Button onClick={handleSubmit} disabled={!reason || loading}>
              {loading ? 'Enviando...' : 'Enviar reporte'}
            </Button>
          </>
        )}
      </DialogContent>
    </Dialog>
  )
}
```

---

## 7. FLUJOS PRINCIPALES

### 7.1 Crear Post con Múltiples Imágenes

```
1. Usuario accede a /new
2. Selecciona 1-3 imágenes desde galería o cámara
3. Frontend muestra preview de imágenes con opción de remover
4. Usuario marca una imagen como principal (radio buttons)
5. Completa ubicación:
   - Opción A: GPS automático → reverse geocoding con Nominatim
   - Opción B: Manual → autocomplete provincias/localidades → geocoding con API Georef
6. Completa formulario: tipo, sexo, tamaño, fecha, descripción, contacto (opcional)
7. Validación client-side (1-3 imágenes, todos los campos requeridos)
8. Submit: FormData con arrays
   - images[0], images[1], images[2]
   - primary_image_index
   - ...otros campos
9. Backend: POST /api/v1/posts
   - Valida cada imagen (tipo, tamaño max 10MB)
   - Procesa cada imagen:
     * ImageService.exif_transpose() → corrige orientación
     * Resize max 2000px
     * Genera thumbnail 400px
     * Compresión JPEG 85%
   - StorageService.upload_images() → sube a R2
   - Crea Post + múltiples PostImage records en DB
   - Primer imagen (o la marcada como primary) → is_primary=True
   - display_order según orden de upload
10. Retorna 201 con PostResponse completo (incluye array images)
11. Frontend navega a Home, muestra mensaje de éxito
```

### 7.2 Filtrar Posts Dinámicamente

```
1. Usuario abre FilterBar en Home (click en botón "Filtros")
2. Selecciona provincia en dropdown (ej: "Buenos Aires")
   - Frontend: onFiltersChange({ ...filters, provincia: "Buenos Aires" })
   - usePosts hook detecta cambio → refetch
3. Backend: GET /api/v1/posts?provincia=Buenos Aires
   - Query: WHERE location_name LIKE '%Buenos Aires%'
   - Calcula available_filters:
     * Provincias con conteos (incluyendo Buenos Aires con su count)
     * Localidades de Buenos Aires con conteos
     * Animal types, sizes, sexes con conteos
4. Backend retorna:
   {
     "data": [posts filtrados],
     "meta": { total: 45, ... },
     "available_filters": {
       "provincias": [
         { "value": "Buenos Aires", "count": 45 },
         { "value": "CABA", "count": 30 },
         ...
       ],
       "localidades": [
         { "value": "La Plata", "count": 15, "provincia": "Buenos Aires" },
         { "value": "Mar del Plata", "count": 10, "provincia": "Buenos Aires" },
         ...
       ],
       "animal_types": [
         { "value": "dog", "label": "Perros", "count": 30 },
         { "value": "cat", "label": "Gatos", "count": 15 }
       ],
       ...
     }
   }
5. Frontend:
   - Actualiza grilla de posts
   - FilterBar muestra opciones disponibles con conteos
   - Dropdown de localidad se habilita con opciones de Buenos Aires
   - Contador: "45 publicaciones encontradas"
6. Usuario selecciona localidad "La Plata"
   - Mismo flujo, ahora filtra por provincia AND localidad
7. Usuario selecciona tipo "Perros"
   - Cascada de filtros se aplica
8. Chips de filtros activos aparecen arriba:
   - [Buenos Aires ✕] [La Plata ✕] [Perros ✕]
   - Click en ✕ → remueve ese filtro → refetch
9. Botón "Limpiar filtros" → resetea todo → refetch sin filtros
```

### 7.3 Reportar Contenido

```
1. Usuario ve un post inapropiado en PostDetail
2. Click en botón "Reportar"
3. ReportModal abre con razones predefinidas:
   - ◯ No es un animal
   - ◯ Contenido inapropiado
   - ◯ Spam
   - ◯ Otro
4. Usuario selecciona razón (ej: "Spam")
5. Opcionalmente escribe descripción adicional (max 1000 chars)
6. Click en "Enviar reporte"
7. Frontend: POST /api/v1/reports
   {
     "post_id": "uuid",
     "reason": "spam",
     "description": "Publicación repetida 5 veces"
   }
8. Backend:
   - Extrae reporter_ip del request
   - Crea Report en DB:
     * post_id
     * reason
     * description
     * reporter_ip
     * resolved=False
   - Si SMTP configurado:
     * EmailService.send_report_notification()
     * Email al MODERATOR_EMAIL con:
       - Razón del reporte
       - Descripción
       - Link directo al post
       - IP del reportero
9. Backend retorna 201 con ReportResponse
10. Frontend:
    - Modal muestra "✓ Reporte enviado correctamente"
    - Auto-cierra después de 2 segundos
11. Moderador recibe email:
    Subject: "Nuevo reporte en LAZOS"
    Body:
      Se ha reportado un post:
      - Razón: Spam
      - Descripción: Publicación repetida 5 veces
      - Post ID: uuid
      - Link: https://lazos.app/post/uuid
      - IP reportero: 1.2.3.4
      - Fecha: 2025-12-29 10:30:00

      Accede al panel de administración para revisar:
      https://lazos.app/admin
```

### 7.4 Moderar Contenido (Panel Admin)

```
1. Admin accede a /admin
2. Si no tiene password guardado en localStorage:
   - Muestra input de password
   - Ingresa password
   - Click en "Ingresar"
3. Frontend: GET /api/v1/admin/reports
   - Headers: { "X-Admin-Password": password }
4. Backend:
   - Valida password contra settings.ADMIN_PASSWORD
   - Si incorrecto → 401 Unauthorized
   - Si correcto → retorna reportes pendientes con post_data
5. Frontend:
   - Guarda password en localStorage
   - Muestra dashboard con stats
   - Lista de reportes:
     ┌────────────────────────────────────────────────┐
     │ REPORTE #1 - Spam (3 reportes totales)        │
     │ ┌──────┐                                       │
     │ │THUMB │ Perro marrón con...                   │
     │ └──────┘ Reportado por: 1.2.3.4                │
     │          Descripción: Publicación repetida...  │
     │                                                 │
     │ [Ver post] [Ignorar reporte] [Eliminar post]  │
     └────────────────────────────────────────────────┘
6. Admin tiene 3 opciones:

   OPCIÓN A - Ver post:
   - Click en "Ver post"
   - Abre /post/:id en nueva pestaña
   - Admin revisa contenido

   OPCIÓN B - Ignorar reporte:
   - Click en "Ignorar reporte"
   - POST /api/v1/admin/reports/:id/resolve
   - Backend: marca report.resolved=True
   - Frontend: remueve de lista, actualiza stats

   OPCIÓN C - Eliminar post:
   - Click en "Eliminar post"
   - Confirmación: "¿Seguro? Esto marcará el post como inactivo"
   - DELETE /api/v1/admin/posts/:id
   - Backend:
     * Post.is_active = False
     * Marca todos los reportes de ese post como resolved=True
   - Frontend: remueve de lista, actualiza stats
7. Dashboard stats actualiza en tiempo real:
   - Total posts: 150
   - Posts activos: 145 (-1 si eliminó)
   - Reportes pendientes: 5 (-1 si resolvió)
```

### 7.5 Búsqueda Unificada

```
1. Usuario accede a /buscar
2. Escribe en input: "perro marrón palermo"
3. Debounce de 300ms
4. Frontend: GET /api/v1/search?q=perro marrón palermo&type=all
5. Backend:
   - Busca en posts.description, posts.location_name, posts.animal_type
   - Busca en alerts.description, alerts.location_name, alerts.animal_type
   - Aplica ILIKE con % (case-insensitive)
   - Ordena por created_at DESC
   - Retorna resultados con:
     * type (post|alert)
     * snippet con término destacado (usa <mark>)
     * thumbnail_url (si post)
     * location_name
     * created_at
6. Frontend muestra resultados:
   ┌────────────────────────────────────────────┐
   │ 🐕 POST                                    │
   │ ┌──────┐                                   │
   │ │THUMB │ Perro marrón con collar...        │
   │ └──────┘ ...visto en <mark>Palermo</mark> │
   │          Hace 2 horas                      │
   └────────────────────────────────────────────┘
   ┌────────────────────────────────────────────┐
   │ 📢 AVISO                                   │
   │ <mark>Perro marrón</mark> corriendo hacia  │
   │ Av. Santa Fe, <mark>Palermo</mark>         │
   │ Hace 30 minutos                            │
   └────────────────────────────────────────────┘
7. Usuario puede filtrar por tabs:
   - [Todos (15)] [Posts (10)] [Avisos (5)]
8. Click en resultado → navega a /post/:id o /avisos/:id
```

---

## 8. CONFIGURACIÓN Y DEPLOYMENT

### 8.1 Variables de Entorno

#### Backend (.env)

```bash
# ========================================
# DATABASE
# ========================================
DATABASE_URL=postgresql://user:password@host:5432/dbname
# Ejemplo con Supabase:
# DATABASE_URL=postgresql://postgres.xxxxx:password@aws-0-us-east-1.pooler.supabase.com:5432/postgres

# ========================================
# CLOUDFLARE R2 STORAGE
# ========================================
# CRÍTICO: R2_PUBLIC_URL debe configurarse o las imágenes no se mostrarán
R2_PUBLIC_URL=https://pub-xxxxx.r2.dev
R2_ENDPOINT=https://xxxxx.r2.cloudflarestorage.com
R2_ACCESS_KEY=your_access_key
R2_SECRET_KEY=your_secret_key
R2_BUCKET=lazos-images

# ========================================
# JWT AUTHENTICATION (opcional, no usado en MVP)
# ========================================
JWT_SECRET=CHANGE-THIS-IN-PRODUCTION-xxxxx
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# ========================================
# ADMIN & MODERATION
# ========================================
ADMIN_PASSWORD=your_admin_password
MODERATOR_EMAIL=admin@example.com

# ========================================
# EMAIL (SMTP) - Para notificaciones de reportes
# ========================================
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your_google_app_password

# ========================================
# APPLICATION
# ========================================
PROJECT_NAME=LAZOS API
VERSION=1.0.0
API_V1_PREFIX=/api/v1

# ========================================
# CORS (comma-separated origins)
# ========================================
CORS_ORIGINS=http://localhost:5173,https://lazos.app
```

#### Frontend (.env)

```bash
VITE_API_URL=http://localhost:8000
# Producción:
# VITE_API_URL=https://api.lazos.app
```

### 8.2 Configuración Cloudflare R2

**⚠️ CRÍTICO:** Sin R2_PUBLIC_URL las imágenes retornarán 403 Forbidden.

**Opción 1: R2.dev Subdomain (Recomendado para desarrollo)**

1. Cloudflare Dashboard → R2 → tu bucket
2. Settings → Public Access
3. Enable "Allow Access" bajo "R2.dev subdomain"
4. Se genera URL como: `https://pub-xxxxx.r2.dev`
5. Agregar a `.env`: `R2_PUBLIC_URL=https://pub-xxxxx.r2.dev`

**Opción 2: Custom Domain (Recomendado para producción)**

1. Conectar un custom domain (ej: `images.lazos.app`)
2. Cloudflare configura SSL automáticamente
3. Agregar a `.env`: `R2_PUBLIC_URL=https://images.lazos.app`

### 8.3 Docker Compose (Desarrollo)

```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_DB: lazos
      POSTGRES_USER: lazos
      POSTGRES_PASSWORD: your_password_here
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./lazos-api/init.sql:/docker-entrypoint-initdb.d/init.sql

  api:
    build: ./lazos-api
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://lazos:your_password_here@db:5432/lazos
      R2_PUBLIC_URL: ${R2_PUBLIC_URL}
      R2_ENDPOINT: ${R2_ENDPOINT}
      R2_ACCESS_KEY: ${R2_ACCESS_KEY}
      R2_SECRET_KEY: ${R2_SECRET_KEY}
      R2_BUCKET: ${R2_BUCKET}
      CORS_ORIGINS: http://localhost:5173
    depends_on:
      - db
    volumes:
      - ./lazos-api:/app

volumes:
  postgres_data:
```

**Comandos:**
```bash
# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f api

# Detener
docker-compose down

# Reiniciar con rebuild
docker-compose up -d --build
```

### 8.4 Comandos Útiles

**Backend:**
```bash
cd lazos-api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt

# Migraciones
alembic upgrade head
alembic revision --autogenerate -m "descripción"

# Dev server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Tests
pytest
pytest -v
pytest tests/api/test_posts.py -v
```

**Frontend:**
```bash
cd lazos-web
npm install

# Dev server
npm run dev

# Build para producción
npm run build

# Preview build
npm run preview
```

### 8.5 Deployment Sugerido

**Opción A: Railway + Vercel**

Backend (Railway):
1. Conectar repo GitHub
2. Agregar PostgreSQL addon con PostGIS
3. Configurar variables de entorno
4. Deploy automático en push a main

Frontend (Vercel):
1. Conectar repo GitHub
2. Framework: Vite
3. Root directory: `lazos-web`
4. Configurar `VITE_API_URL` en env vars
5. Deploy automático en push a main

**Opción B: Docker + VPS**

1. VPS con Docker instalado (DigitalOcean, Linode, etc.)
2. `docker-compose.yml` configurado para producción
3. Nginx reverse proxy con SSL (Let's Encrypt)
4. GitHub Actions para CI/CD

---

## 9. DECISIONES DE ARQUITECTURA

### 9.1 Múltiples Imágenes vs Imagen Única

**Decisión:** Múltiples imágenes (hasta 3)

**Razón:**
- Mejor contexto visual del animal (frente, perfil, marcas distintivas)
- Mayor probabilidad de matching para dueños buscando
- No sobrecarga el storage (límite de 3)

**Implementación:**
- Tabla `post_images` separada (relación 1:N)
- Campos `is_primary` (imagen principal para thumbnails), `display_order` (orden de visualización)
- Backward compatibility: `posts.image_url` y `posts.thumbnail_url` apuntan a imagen primaria

**Alternativa descartada:**
- JSON array en `posts.images` → dificulta queries, no aprovecha relaciones SQL

### 9.2 Geocodificación: API Georef vs Nominatim

**Decisión:** Híbrido (API Georef prioritario, Nominatim fallback)

**Razón:**
- API Georef: Datos oficiales INDEC Argentina, más preciso para direcciones argentinas
- Nominatim: Coverage global, útil para reverse geocoding GPS
- Datos offline (provincias.json, localidades.json): Rápido, sin rate limits, UX mejorada

**Implementación:**
- Frontend autocomplete usa JSONs estáticos (3,979 localidades)
- Geocodificación de dirección completa: API Georef primero, Nominatim si falla
- Reverse geocoding GPS: Nominatim (más rápido)

**Formato de ubicación:**
```
"calle número, ciudad, provincia"
Ejemplo: "Av. 7 1234, La Plata, Buenos Aires"
```

### 9.3 Filtros Dinámicos vs Estáticos

**Decisión:** Dinámicos con conteos en backend

**Razón:**
- UX superior: Usuario ve solo opciones disponibles con resultados
- Evita "0 resultados" por combinaciones imposibles
- Más complejidad en backend, pero frontend más simple

**Implementación:**
- Backend calcula `available_filters` con conteos después de aplicar filtros actuales
- Filtros en cascada: provincia → localidades disponibles
- Parsing de `location_name` para extraer provincia y localidad

**Ejemplo:**
```json
{
  "available_filters": {
    "provincias": [
      { "value": "Buenos Aires", "count": 45 },
      { "value": "CABA", "count": 30 }
    ],
    "localidades": [
      { "value": "La Plata", "count": 15, "provincia": "Buenos Aires" }
    ]
  }
}
```

### 9.4 Autenticación: JWT vs Anónimo

**Decisión:** Anónimo en MVP (JWT config lista pero no implementado)

**Razón:**
- **PRO anónimo:** Menos fricción para reportar, API pública sin auth, foco en adopción
- **CONTRA anónimo:** Riesgo de spam, no se puede editar posts propios, sin tracking de usuario

**Mitigación de riesgos:**
- Sistema de reportes + moderación manual
- Rate limiting por IP (pendiente)
- Captcha en formularios (pendiente)

**Futuro:**
- Implementar JWT como opcional
- Usuarios autenticados pueden editar/eliminar sus posts
- Posts anónimos siguen permitidos

### 9.5 Storage: Cloudflare R2 vs S3

**Decisión:** Cloudflare R2

**Razón:**
- **Costo:** Sin egress fees (S3 cobra por transferencia)
- **Compatibilidad:** S3-compatible (usa boto3)
- **Performance:** CDN de Cloudflare integrado

**Costos estimados:**
- 1000 fotos/mes × 500KB = 500MB
- Storage: $0.015/GB/mes = ~$0.01/mes
- Operaciones: insignificantes
- Egress: **$0** (principal ventaja)

**Total: < $1/mes**

### 9.6 Tema Visual: Fijo vs Día/Noche

**Decisión:** Día/Noche con CSS variables

**Razón:**
- Mejor UX, menos fatiga visual en horarios nocturnos
- Preferencia de usuario respetada
- Implementación simple con Tailwind dark mode

**Implementación:**
- CSS variables en `index.css` con tonos cálidos (día) y oscuros (noche)
- Toggle en header con persistencia en localStorage
- Tailwind classes: `dark:bg-background`, `dark:text-foreground`, etc.

---

## 10. PRÓXIMOS PASOS

### 10.1 Alta Prioridad

**1. Integración CLIP para Búsqueda por Similitud**

**Objetivo:** Permitir a usuarios subir foto de su mascota perdida y encontrar posts similares.

**Pasos:**
1. Instalar dependencias:
   ```bash
   pip install transformers torch pillow
   ```
2. Crear `app/services/embedding.py`:
   ```python
   from transformers import CLIPProcessor, CLIPModel
   import torch

   class EmbeddingService:
       def __init__(self):
           self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
           self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
           self.device = "cuda" if torch.cuda.is_available() else "cpu"
           self.model.to(self.device)

       def get_embedding(self, image: Image) -> np.ndarray:
           inputs = self.processor(images=image, return_tensors="pt")
           inputs = {k: v.to(self.device) for k, v in inputs.items()}
           with torch.no_grad():
               features = self.model.get_image_features(**inputs)
           embedding = features.cpu().numpy().flatten()
           return embedding / np.linalg.norm(embedding)  # normalizar
   ```
3. Modificar `app/api/routes/posts.py` → `create_post()`:
   - Después de procesar imagen, generar embedding
   - Guardar en `post.embedding`
4. Implementar `POST /api/v1/search/similar`:
   - Recibir imagen, generar embedding
   - Query: `SELECT * FROM posts ORDER BY embedding <=> $1 LIMIT 10`
   - Retornar posts con % de similitud
5. Frontend (`/buscar`):
   - Agregar sección "Buscar por imagen"
   - Input file → upload → mostrar resultados con % similitud

**Impacto:** Feature killer de la app, diferenciación clave vs competencia.

**2. PWA Completo**

**Objetivo:** App instalable en móviles con funcionalidad offline.

**Pasos:**
1. Crear `public/manifest.json`:
   ```json
   {
     "name": "LAZOS - Encuentra Mascotas",
     "short_name": "LAZOS",
     "icons": [
       { "src": "/icon-192.png", "sizes": "192x192", "type": "image/png" },
       { "src": "/icon-512.png", "sizes": "512x512", "type": "image/png" }
     ],
     "start_url": "/",
     "display": "standalone",
     "background_color": "#ffffff",
     "theme_color": "#f97316"
   }
   ```
2. Instalar `vite-plugin-pwa`:
   ```bash
   npm install -D vite-plugin-pwa
   ```
3. Configurar `vite.config.js`:
   ```javascript
   import { VitePWA } from 'vite-plugin-pwa'

   plugins: [
     react(),
     VitePWA({
       registerType: 'autoUpdate',
       manifest: './public/manifest.json',
       workbox: {
         runtimeCaching: [
           {
             urlPattern: /^https:\/\/pub-.*\.r2\.dev\/.*/,
             handler: 'CacheFirst',
             options: {
               cacheName: 'images-cache',
               expiration: { maxEntries: 100, maxAgeSeconds: 30 * 24 * 60 * 60 }
             }
           }
         ]
       }
     })
   ]
   ```
4. Crear iconos 192x192 y 512x512
5. Testear en Chrome DevTools → Application → Manifest

**Impacto:** Mejor UX móvil, app "nativa", funciona offline.

### 10.2 Media Prioridad

**3. Rate Limiting por IP**

**Objetivo:** Prevenir spam y abuse de API pública.

**Pasos:**
1. Instalar `slowapi`:
   ```bash
   pip install slowapi
   ```
2. Configurar en `app/main.py`:
   ```python
   from slowapi import Limiter
   from slowapi.util import get_remote_address

   limiter = Limiter(key_func=get_remote_address)
   app.state.limiter = limiter

   @app.post("/api/v1/posts")
   @limiter.limit("10/hour")
   async def create_post(...):
       ...
   ```
3. Límites sugeridos:
   - GET endpoints: 100 req/min
   - POST posts: 10 req/hora
   - POST reports: 5 req/hora

**4. Analytics Privacy-First (Plausible)**

**Objetivo:** Entender uso sin invadir privacidad.

**Pasos:**
1. Crear cuenta en Plausible.io
2. Agregar script en `index.html`:
   ```html
   <script defer data-domain="lazos.app" src="https://plausible.io/js/script.js"></script>
   ```
3. No requiere cookies ni GDPR banners
4. Métricas: páginas vistas, fuentes de tráfico, dispositivos

### 10.3 Baja Prioridad

**5. Autenticación JWT (Opcional)**

Si se decide implementar:
1. Endpoints `POST /auth/register`, `POST /auth/login`
2. Middleware de autenticación para rutas protegidas
3. Frontend: Login/registro UI, token storage en localStorage
4. Asociar posts a usuarios
5. Permitir editar/eliminar solo posts propios

**6. Testing**

Backend:
- pytest con fixtures para DB
- Coverage objetivo: >80%
- Tests de integración para endpoints críticos

Frontend:
- Vitest + React Testing Library
- Tests de componentes clave (FilterBar, PostCard)
- E2E con Playwright (flujo completo de crear post)

**7. Optimizaciones de Performance**

- CDN para imágenes (Cloudflare CDN ya incluido con R2)
- Redis para cache de GET /posts (resultados frecuentes)
- Connection pooling tuning en PostgreSQL
- Lazy loading de componentes React (React.lazy)
- Image lazy loading en grilla (loading="lazy")

---

## APÉNDICE A: TROUBLESHOOTING

### Problema: Imágenes no se muestran (403 Forbidden)

**Causa:** R2_PUBLIC_URL no configurado o bucket no público.

**Solución:**
1. Verificar `.env`: `R2_PUBLIC_URL=https://pub-xxxxx.r2.dev`
2. Cloudflare Dashboard → R2 → bucket → Settings → Public Access → Enable
3. Reiniciar backend: `docker-compose restart api`
4. Test: Abrir URL de imagen en navegador incógnito

### Problema: react-leaflet error "Cannot read properties of null"

**Causa:** Versión incompatible con React 18.

**Solución:**
```bash
npm install react-leaflet@4.2.1
```

### Problema: CORS error en frontend

**Causa:** CORS_ORIGINS no incluye URL de frontend.

**Solución:**
1. Verificar `.env` backend:
   ```
   CORS_ORIGINS=http://localhost:5173,https://lazos.app
   ```
2. Reiniciar backend
3. Verificar en Network tab (F12) que header `Access-Control-Allow-Origin` está presente

### Problema: Localidades no cargan en desplegable

**Causa:** JSON no encontrado o error de parsing.

**Solución:**
1. Verificar archivos existen:
   ```bash
   ls -lh lazos-web/public/data/
   # Debe mostrar provincias.json y localidades.json
   ```
2. Verificar JSON válido:
   ```bash
   jq . lazos-web/public/data/localidades.json | head
   ```
3. Check console browser (F12) por errores de fetch

### Problema: Emails de reportes no se envían

**Causa:** SMTP no configurado o credenciales incorrectas.

**Solución:**
1. Verificar `.env`:
   ```
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=tu_email@gmail.com
   SMTP_PASSWORD=tu_app_password  # NO tu password normal
   ```
2. Gmail: Generar App Password en https://myaccount.google.com/apppasswords
3. Test endpoint:
   ```bash
   curl -X POST http://localhost:8000/api/v1/reports \
     -H "Content-Type: application/json" \
     -d '{"post_id":"uuid","reason":"spam"}'
   ```
4. Check logs backend por errores SMTP

---

## APÉNDICE B: GLOSARIO TÉCNICO

**Alert:** Aviso rápido sin imágenes, para reportes temporales de animales en movimiento.

**API Georef:** Servicio de georeferenciación del INDEC (Argentina) con datos oficiales de provincias, localidades, calles.

**Available Filters:** Filtros dinámicos calculados por el backend que muestran solo opciones con resultados disponibles, incluyendo conteos.

**CLIP:** Contrastive Language-Image Pre-training. Modelo de IA de OpenAI que genera embeddings de imágenes para búsqueda por similitud semántica.

**Embedding:** Vector numérico de 512 dimensiones que representa una imagen en espacio semántico. Permite comparar similitud entre imágenes con distancia coseno.

**EXIF Transpose:** Corrección de orientación de imágenes basada en metadatos EXIF. Esencial para fotos de móviles que pueden estar rotadas.

**Geocoding:** Conversión de dirección (ej: "Av. 7 1234, La Plata") a coordenadas (lat, lon).

**Geography POINT:** Tipo de dato PostGIS que almacena coordenadas geográficas (lat, lon) en formato WGS84 (SRID 4326).

**HNSW:** Hierarchical Navigable Small World. Algoritmo de indexación para búsqueda rápida de vecinos más cercanos en espacios vectoriales (usado en pgvector).

**PostGIS:** Extensión de PostgreSQL para queries geoespaciales (distancias, áreas, intersecciones).

**pgvector:** Extensión de PostgreSQL para almacenar y buscar vectores (embeddings). Soporta índices HNSW para búsqueda rápida.

**R2.dev Subdomain:** URL pública generada por Cloudflare R2 para acceder a archivos en buckets (ej: https://pub-xxxxx.r2.dev).

**Reverse Geocoding:** Conversión de coordenadas (lat, lon) a dirección legible (ej: "Av. 7 1234, La Plata").

**Soft Delete:** Marcar registro como inactivo (is_active=False) en lugar de eliminarlo físicamente. Permite recuperación y auditoría.

**shadcn/ui:** Colección de componentes React reutilizables construidos con Tailwind CSS y Radix UI. No es una biblioteca instalable, se copian componentes al proyecto.

---

## APÉNDICE C: CHECKLIST DE DESARROLLO

### Al agregar una nueva feature:

- [ ] Actualizar este documento (COMPREHENSIVE_GUIDE.md) con detalles técnicos
- [ ] Agregar entry en CHANGELOG.md
- [ ] Si cambia DB: Crear migración Alembic
- [ ] Si cambia API: Actualizar schemas Pydantic y documentación de endpoints
- [ ] Si cambia frontend: Actualizar sección de componentes/páginas
- [ ] Tests (backend): pytest para nuevos endpoints
- [ ] Tests (frontend): Vitest para componentes críticos (si testing implementado)
- [ ] Verificar que no rompe features existentes
- [ ] Commit con mensaje convencional (ej: `feat: Agregar búsqueda por similitud CLIP`)

### Al arreglar un bug:

- [ ] Actualizar CHANGELOG.md en sección "Fixed"
- [ ] Si bug estaba en PENDING.md → removerlo
- [ ] Commit con mensaje: `fix: Descripción del bug arreglado`
- [ ] Verificar que fix no introduce regresiones

### Al hacer deployment:

- [ ] Verificar todas las variables de entorno configuradas
- [ ] Ejecutar migraciones: `alembic upgrade head`
- [ ] Verificar R2_PUBLIC_URL configurado
- [ ] Testear flujo completo: crear post → ver en home → filtrar → reportar
- [ ] Verificar que imágenes se muestran correctamente
- [ ] Verificar emails de reportes funcionan (si SMTP configurado)
- [ ] Monitorear logs por errores

---

**FIN DE LA GUÍA COMPLETA**

Esta documentación debe mantenerse sincronizada con el código. Actualízala después de cada cambio significativo.

**Última actualización:** 2025-12-29
**Versión del proyecto:** 2.0
**Mantenido por:** Agentes IA + Claude Code
