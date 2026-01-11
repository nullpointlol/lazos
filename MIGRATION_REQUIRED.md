# ⚠️ MIGRACIÓN PENDIENTE EN PRODUCCIÓN

## Problema Actual

El modelo `Post` incluye nuevos campos que requieren una migración de base de datos:
- `validation_service` (String)
- `post_number` (Integer, secuencial)

El campo `post_number` está **temporalmente comentado** en el modelo (`app/models/post.py`) para evitar errores en producción.

## Solución

### Paso 1: Correr migración en Railway

```bash
# Conectarse a Railway (desde tu máquina local)
railway login

# Seleccionar el proyecto lazos
railway link

# Correr la migración
railway run alembic upgrade head
```

O directamente en Railway:
1. Ve al proyecto en Railway dashboard
2. Abre la terminal del servicio API
3. Ejecuta: `alembic upgrade head`

### Paso 2: Descomentar `post_number` en el modelo

Una vez que la migración se ejecute correctamente en producción:

**Archivo**: `lazos-api/app/models/post.py` (líneas 72-82)

**Cambiar de**:
```python
# NOTE: Commented out until migration 20260111_0000 is run in production
# Uncomment after running: alembic upgrade head
# post_number_seq = Sequence('posts_post_number_seq', optional=True)
# post_number = Column(
#     Integer,
#     post_number_seq,
#     nullable=True,
#     unique=True,
#     index=True
# )
```

**A**:
```python
# Sequential post number for display (e.g., #1, #2, #3)
post_number_seq = Sequence('posts_post_number_seq', optional=True)
post_number = Column(
    Integer,
    post_number_seq,
    nullable=True,
    unique=True,
    index=True
)
```

### Paso 3: Asignar números a posts existentes

Después de descomentar, ejecuta esta query en PostgreSQL para asignar números secuenciales a los posts existentes:

```sql
-- Asignar números en orden de created_at
WITH numbered_posts AS (
  SELECT
    id,
    ROW_NUMBER() OVER (ORDER BY created_at ASC) as row_num
  FROM posts
  WHERE post_number IS NULL
)
UPDATE posts
SET post_number = numbered_posts.row_num
FROM numbered_posts
WHERE posts.id = numbered_posts.id;

-- Actualizar la secuencia para continuar desde el último número
SELECT setval('posts_post_number_seq', (SELECT COALESCE(MAX(post_number), 0) FROM posts));
```

## Archivos Involucrados

- **Migración**: `lazos-api/migrations/versions/20260111_0000-add_validation_and_post_number.py`
- **Modelo**: `lazos-api/app/models/post.py`
- **Este archivo**: `MIGRATION_REQUIRED.md` (eliminar después de completar)

## Estado Actual

- ❌ Migración NO corrida en Railway
- ✅ Migración corrida en desarrollo local
- ⚠️ Campo `post_number` comentado temporalmente en modelo
- ✅ Campo `validation_service` funcionando (nullable)
- ✅ Sistema de validación híbrida funcionando

---

**Fecha**: 2026-01-11
**Responsable**: Agustín Arena
