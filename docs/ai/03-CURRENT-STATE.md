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

**Sistema de Validación Híbrida de Contenido:**
- **Validación de Imágenes (2 fases en paralelo)**:
  - Fase 1 (rápida): Python NSFW detector valida TODAS las imágenes (~200ms)
  - Fase 2 (precisa): Cloudflare AI Workers (ResNet-50) valida solo sospechosas (~1-2s)
  - 95% de posts validados en < 300ms
  - Ahorro del 97% en llamadas API de Cloudflare
- **Validación de Texto Semántica**:
  - Cloudflare AI Workers con Llama-3-8b
  - Detecta spam, contenido inapropiado, URLs sospechosas
  - Análisis contextual del contenido
- **Sistema de Aprobación**:
  - Posts sospechosos → `pending_approval=True`
  - Campo `moderation_reason` con detalles de validación
  - Panel admin con información detallada para moderación

**Sistema de Reportes Unificado:**
- Endpoint POST `/api/v1/reports` para reportar posts o alerts
- Razones: `not_animal`, `inappropriate`, `spam`, `other`
- Campo `description` opcional para detalles
- Guarda `reporter_ip` automáticamente
- Notificación automática por email al moderador (SMTP)
- Panel admin: GET `/admin/reports`, POST `/admin/reports/{id}/resolve`, DELETE `/admin/posts/{id}`
- Estadísticas: GET `/admin/stats`

**Numeración Secuencial de Posts:**
- Campo `post_number` autoincrementable (1, 2, 3...)
- Trigger PostgreSQL para asignación automática
- Migración ejecutada para posts existentes
- URLs tipo `/post/123` más amigables

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

**Infraestructura CLIP (Preparada pero NO implementada):**
- Campo `embedding VECTOR(512)` en DB
- Índice HNSW para búsqueda rápida
- ❌ Endpoint `/search/similar` NO existe en código real
- ❌ No se generan embeddings al crear posts
- **PENDIENTE:** Integrar modelo CLIP completamente (backend + frontend)

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
   - Popups con thumbnail, info básica y botones de reporte
   - Botón reportar contenido inapropiado
   - Botón reportar ubicación incorrecta
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
   - Dashboard con stats (posts totales, activos, reportes pendientes, posts pendientes de aprobación)
   - **Pestaña Posts Pendientes**: Lista de posts con `pending_approval=True`
     - Muestra motivo de moderación (validación de imágenes o texto)
     - Botones: Aprobar / Rechazar
     - Preview de imágenes y contenido
   - **Pestaña Reportes**: Lista de reportes con preview
     - Tipos: contenido inapropiado, spam, ubicación incorrecta
     - Contador de reportes por post
     - Botones: Ignorar / Resolver
   - Link directo para ver post/aviso

**Componentes:**

- **PostCard**: Tarjeta de post con thumbnail, indicador de múltiples imágenes, iconos de sexo (♂♀?), truncado de descripción, fecha relativa
- **FilterBar**: Barra de filtros colapsable con badge de filtros activos, contador de publicaciones, chips de filtros activos con botón X, dropdowns de provincia y localidad con conteos, presets de fecha
- **ReportModal**: Modal para reportar contenido con radio buttons (no es animal, inapropiado, spam, otro), textarea opcional, loading y success states
- **Layout + BottomNav**: Navegación inferior fija con 4 botones (Home, Avisos, Buscar, Mapa)
- **FAB**: Floating Action Button para crear nueva publicación
- **HelpModal**: Modal con información del proyecto, privacidad y datos abiertos

**Hooks:**

- `usePosts(filters)`: Fetch posts con filtros, retorna `{ posts, loading, error, meta, availableFilters, refetch }`
- `useAlerts(filters)`: Fetch alerts
- `usePullToRefresh()`: Pull-to-refresh gesture
- `useAutoRefresh(callback, interval)`: Auto-refresh periódico con timestamp
- `useContentValidation()`: Validación de imágenes con NSFW.js (detección client-side)

**Utilities:**

- `validateText(text)`: Validación de texto con 9 reglas (spam, contenido inapropiado, caracteres mínimos, etc.)
- `sanitizeText(text)`: Sanitización de texto antes de enviar
- `containsContactInfo(text)`: Detección de teléfonos/emails en texto

**Tema Día/Noche:**
- Sistema completo con CSS variables
- Tonos cálidos para día, oscuros para noche
- Mejor contraste en ambos temas
- Variaciones de hover sutiles
- Toggle en header

**Datos Estáticos (Offline-First):**
- Provincias y localidades cargadas desde JSON local (`/data/provincias.json`, `/data/localidades.json`)
- 24 provincias argentinas
- 3,979 localidades
- Mejora performance y funciona offline

### 3.2 Features No Implementadas

**Búsqueda por Similitud CLIP:**
- ❌ Endpoint `/search/similar` NO existe en código (solo documentado)
- ❌ No se generan embeddings al crear posts
- ❌ Frontend: No hay UI de upload de imagen para búsqueda
- **PENDIENTE:** Implementar completamente (backend + frontend + generación de embeddings)

**PWA Completo:**
- ⚠️ Componente PWAInstallPrompt existe pero sin verificar funcionalidad
- Falta verificar: manifest.json con iconos, service worker para offline, cache de imágenes

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

