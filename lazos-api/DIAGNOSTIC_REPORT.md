# REPORTE DE DIAGNÓSTICO - DESINCRONIZACIÓN BASE DE DATOS

**Fecha**: 2025-12-31
**Problema**: `psycopg2.errors.UndefinedColumn: column posts.pending_approval does not exist`
**Entorno afectado**: Railway (backend) + Supabase (base de datos)

---

## 📋 RESUMEN EJECUTIVO

El backend en Railway falla porque el modelo Python SQLAlchemy (`Post`) tiene 3 columnas de moderación que **NO existen** en la base de datos de producción en Supabase:

1. `pending_approval` (BOOLEAN)
2. `moderation_reason` (VARCHAR(500))
3. `moderation_date` (TIMESTAMP WITH TIME ZONE)

**Causa raíz**: Se creó una migración de Alembic (`20251231_0000-add_moderation_to_posts.py`) pero Railway **NO ejecuta migraciones automáticamente**. La DB de producción está en Supabase, no en Railway.

**Solución**: Ejecutar manualmente el script SQL en Supabase.

---

## 🔍 DIAGNÓSTICO DETALLADO

### 1. COLUMNAS DEL MODELO POST (Python)

**Archivo**: `lazos-api/app/models/post.py`

| # | Columna | Tipo | Nullable | Default | Index |
|---|---------|------|----------|---------|-------|
| 1 | `id` | UUID | NO | `uuid.uuid4` | ✅ |
| 2 | `image_url` | String(500) | NO | - | ❌ |
| 3 | `thumbnail_url` | String(500) | NO | - | ❌ |
| 4 | `sex` | Enum(SexEnum) | NO | `unknown` | ✅ |
| 5 | `size` | Enum(SizeEnum) | NO | - | ✅ |
| 6 | `animal_type` | Enum(AnimalEnum) | NO | `dog` | ✅ |
| 7 | `description` | Text | YES | - | ❌ |
| 8 | `location` | Geography(POINT) | NO | - | ✅ (GIST) |
| 9 | `location_name` | String(200) | YES | - | ❌ |
| 10 | `sighting_date` | Date | NO | - | ✅ |
| 11 | `created_at` | DateTime(TZ) | NO | `utcnow` | ✅ |
| 12 | `updated_at` | DateTime(TZ) | YES | `utcnow` | ❌ |
| 13 | `is_active` | Boolean | NO | `True` | ✅ |
| 14 | **`pending_approval`** | **Boolean** | **NO** | **`False`** | **✅** |
| 15 | **`moderation_reason`** | **String(500)** | **YES** | **-** | **❌** |
| 16 | **`moderation_date`** | **DateTime(TZ)** | **YES** | **-** | **❌** |
| 17 | `contact_method` | String(200) | YES | - | ❌ |
| 18 | `embedding` | Vector(512) | YES | - | ✅ (HNSW) |

**Total**: 18 columnas (3 de moderación faltantes en DB)

---

### 2. MIGRACIONES DE ALEMBIC

**Directorio**: `lazos-api/migrations/versions/`

| Archivo | Revision ID | Revises | Descripción | Columnas afectadas |
|---------|-------------|---------|-------------|-------------------|
| `20251225_0000-initial_schema.py` | `001` | `None` | Schema inicial | Todas las columnas base de `posts` (15 columnas) |
| `20251226_1359-bd61a4fb8a8b_add_alerts_table.py` | `20251226_1359` | `001` | Tabla `alerts` | N/A (nueva tabla) |
| `20251227_1917-add_reports_table.py` | `20251227_1917` | `20251226_1359` | Tabla `reports` | N/A (nueva tabla) |
| `20251228_0000-add_alert_id_to_reports.py` | `20251228_0000` | `20251227_1917` | Campo `alert_id` en reports | `reports.alert_id`, `reports.post_id` (ahora nullable) |
| **`20251231_0000-add_moderation_to_posts.py`** | **`20251231_0000`** | **`20251228_0000`** | **Campos de moderación** | **`posts.pending_approval`, `posts.moderation_reason`, `posts.moderation_date`** |

**Estado actual**: Migración creada ✅ | Aplicada a Supabase ❌

---

### 3. MODELOS VERIFICADOS

#### 3.1 Alert Model
**Archivo**: `lazos-api/app/models/alert.py`

| Columna | Tipo | Nullable | Default | En DB |
|---------|------|----------|---------|-------|
| `id` | UUID | NO | `gen_random_uuid()` | ✅ |
| `description` | Text | NO | - | ✅ |
| `animal_type` | Enum(AnimalEnum) | NO | - | ✅ |
| `direction` | String(200) | YES | - | ✅ |
| `location` | Geography(POINT) | NO | - | ✅ |
| `location_name` | String(200) | YES | - | ✅ |
| `created_at` | DateTime(TZ) | NO | `now()` | ✅ |
| `is_active` | Boolean | NO | `true` | ✅ |

**Status**: ✅ Modelo sincronizado con DB

#### 3.2 Report Model
**Archivo**: `lazos-api/app/models/report.py`

| Columna | Tipo | Nullable | Default | En DB |
|---------|------|----------|---------|-------|
| `id` | UUID | NO | `uuid.uuid4` | ✅ |
| `post_id` | UUID (FK) | YES | - | ✅ |
| `alert_id` | UUID (FK) | YES | - | ✅ |
| `reason` | Enum(ReportReasonEnum) | NO | - | ✅ |
| `description` | Text | YES | - | ✅ |
| `reporter_ip` | String(45) | YES | - | ✅ |
| `created_at` | DateTime(TZ) | NO | `utcnow` | ✅ |
| `resolved` | Boolean | NO | `False` | ✅ |

**Status**: ✅ Modelo sincronizado con DB

---

### 4. DISCREPANCIAS ENCONTRADAS

| Columna | En modelo Python | En migración Alembic | En DB Supabase | Estado |
|---------|------------------|---------------------|----------------|--------|
| `pending_approval` | ✅ (Boolean, default=False) | ✅ (20251231_0000) | ❌ | **FALTANTE** |
| `moderation_reason` | ✅ (String(500), nullable) | ✅ (20251231_0000) | ❌ | **FALTANTE** |
| `moderation_date` | ✅ (DateTime(TZ), nullable) | ✅ (20251231_0000) | ❌ | **FALTANTE** |

**Total de discrepancias**: 3 columnas

---

### 5. CONFIGURACIÓN DE RAILWAY

**Archivo de entrada**: `lazos-api/app/main.py`

**Comando de inicio** (inferido por Railway):
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Migraciones automáticas**: ❌ NO HABILITADO

Railway **NO ejecuta** `alembic upgrade head` automáticamente. Las migraciones deben:
1. Aplicarse manualmente en Supabase (SQL directo), O
2. Configurar un script de inicio que ejecute migraciones antes de iniciar la app

---

## ✅ SOLUCIÓN IMPLEMENTADA

### Archivo creado: `lazos-api/scripts/sync_database.sql`

Este script SQL:
- ✅ Es **idempotente** (usa `IF NOT EXISTS`)
- ✅ Agrega las 3 columnas de moderación
- ✅ Crea índices para optimizar queries
- ✅ Migra datos existentes (set `pending_approval = FALSE`)
- ✅ Agrega comentarios de documentación

**Cómo ejecutar**:
1. Ir a Supabase Dashboard
2. SQL Editor → New Query
3. Copiar y pegar el contenido de `sync_database.sql`
4. Ejecutar

---

## 📝 INSTRUCCIONES PARA EVITAR ESTO EN EL FUTURO

### Opción A: Ejecutar migraciones automáticamente en Railway

Crear archivo `lazos-api/start.sh`:

```bash
#!/bin/bash
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Starting FastAPI server..."
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Configurar en Railway:
- Settings → Deploy → Start Command: `bash start.sh`

### Opción B: Workflow manual (actual)

1. **Desarrollador crea migración**:
   ```bash
   cd lazos-api
   alembic revision --autogenerate -m "descripción"
   ```

2. **Desarrollador revisa migración generada**:
   - Verificar que las columnas sean correctas
   - Ajustar índices si es necesario

3. **Desarrollador aplica en Supabase**:
   - Generar SQL equivalente
   - Ejecutar en Supabase SQL Editor

4. **Desarrollador commitea migración**:
   ```bash
   git add migrations/versions/XXXXX.py
   git commit -m "migration: descripción"
   git push
   ```

### Opción C: CI/CD con scripts (recomendado)

1. Crear `lazos-api/scripts/generate_migration_sql.py`:
   - Script que convierte migraciones Alembic → SQL directo
   - Genera archivo `.sql` para ejecutar en Supabase

2. Configurar GitHub Actions:
   - Al hacer push de nueva migración
   - Generar SQL automáticamente
   - Notificar al desarrollador para aplicar en Supabase

---

## 🎯 ACCIONES INMEDIATAS REQUERIDAS

1. **Ejecutar script SQL en Supabase** ← ⚠️ URGENTE
   - Archivo: `lazos-api/scripts/sync_database.sql`
   - Esto resolverá el error de producción

2. **Verificar en Railway logs**:
   - Después de ejecutar SQL, reiniciar deployment
   - Verificar que el error `column does not exist` desaparezca

3. **Decidir estrategia de migraciones**:
   - Implementar Opción A, B, o C
   - Documentar en README

---

## 📊 ESTADÍSTICAS

- **Total de modelos**: 5 (Post, Alert, Report, User, PostImage)
- **Modelos sincronizados**: 4 ✅
- **Modelos desincronizados**: 1 ❌ (Post)
- **Columnas faltantes**: 3
- **Migraciones totales**: 5
- **Migraciones no aplicadas**: 1

---

## 🔗 ARCHIVOS RELACIONADOS

- Script SQL: `lazos-api/scripts/sync_database.sql`
- Migración Alembic: `lazos-api/migrations/versions/20251231_0000-add_moderation_to_posts.py`
- Modelo afectado: `lazos-api/app/models/post.py`
- Este reporte: `lazos-api/DIAGNOSTIC_REPORT.md`

---

**Reporte generado**: 2025-12-31
**Por**: Claude Code (Diagnóstico automático)
