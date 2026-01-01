# Instrucciones de Migración - Sistema de Moderación de Contenido

## 📋 Resumen

Este documento describe cómo aplicar la migración de base de datos para el sistema de moderación de contenido con validación de imágenes usando IA.

## 🗄️ Migración de Base de Datos

### Opción 1: Usando Supabase Dashboard

1. Accede a tu proyecto en Supabase Dashboard
2. Ve a la sección **SQL Editor**
3. Crea una nueva query
4. Copia y pega el contenido del archivo `/lazos-api/migrations/add_pending_approval.sql`
5. Ejecuta la query
6. Verifica que se hayan creado las columnas:
   - `pending_approval` (boolean)
   - `moderation_reason` (text)
   - `moderation_date` (timestamp)

### Opción 2: Usando CLI de Supabase

```bash
# Si tienes Supabase CLI instalado
supabase db push

# O ejecuta directamente el archivo SQL
psql $DATABASE_URL -f lazos-api/migrations/add_pending_approval.sql
```

### Opción 3: Usando psql directamente

```bash
psql -h [SUPABASE_HOST] -U postgres -d postgres -f lazos-api/migrations/add_pending_approval.sql
```

## ✅ Verificación

Después de aplicar la migración, verifica que todo funcione correctamente:

### 1. Verificar columnas en la tabla

```sql
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'posts'
AND column_name IN ('pending_approval', 'moderation_reason', 'moderation_date');
```

Deberías ver 3 columnas nuevas.

### 2. Verificar índices

```sql
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'posts'
AND indexname LIKE '%pending%';
```

Deberías ver 2 índices nuevos.

### 3. Verificar que posts existentes están aprobados

```sql
SELECT COUNT(*) as total_posts,
       COUNT(CASE WHEN pending_approval = false THEN 1 END) as approved_posts,
       COUNT(CASE WHEN pending_approval = true THEN 1 END) as pending_posts
FROM posts;
```

Todos los posts existentes deberían tener `pending_approval = false`.

## 🧪 Testing

### Test 1: Crear post normal (sin validación)
1. Abre el formulario de nuevo post
2. Sube una imagen clara de un animal
3. Completa el formulario
4. El post debería aparecer inmediatamente en el feed

### Test 2: Crear post con validación
1. Abre el formulario de nuevo post
2. Sube una imagen ambigua
3. Completa el formulario
4. El post podría quedar pendiente de aprobación

### Test 3: Panel de Admin
1. Ve a `/admin`
2. Ingresa la contraseña de admin
3. Ve a la pestaña "Pendientes"
4. Deberías ver los posts pendientes de aprobación
5. Prueba aprobar y rechazar posts

## 📦 Dependencias Instaladas

Las siguientes dependencias fueron agregadas al proyecto:

```json
{
  "nsfwjs": "^2.4.2",
  "@tensorflow/tfjs": "^4.11.0"
}
```

**Tamaño aproximado:** ~18MB agregados al bundle de producción.

## 🔧 Configuración Adicional

### Variables de Entorno

No se requieren nuevas variables de entorno para esta funcionalidad.

### Modelo NSFW.js

El modelo NSFW.js se carga automáticamente desde CDN la primera vez que un usuario intenta crear un post. No requiere configuración adicional.

## 🚨 Rollback

Si necesitas revertir la migración:

```sql
-- Eliminar columnas agregadas
ALTER TABLE posts DROP COLUMN IF EXISTS pending_approval;
ALTER TABLE posts DROP COLUMN IF EXISTS moderation_reason;
ALTER TABLE posts DROP COLUMN IF EXISTS moderation_date;

-- Eliminar índices
DROP INDEX IF EXISTS idx_posts_pending_approval;
DROP INDEX IF EXISTS idx_posts_active_approved;
```

## 📝 Notas

- Los posts existentes se marcan automáticamente como aprobados (`pending_approval = false`)
- El sistema es compatible hacia atrás - si no se usa validación, los posts se crean normalmente
- La validación de imágenes ocurre en el frontend antes de enviar al servidor
- Los posts rechazados por contenido NSFW nunca llegan al servidor

## 🤝 Soporte

Si encuentras problemas durante la migración:
1. Verifica que tengas permisos de admin en Supabase
2. Revisa los logs del servidor para errores
3. Consulta la documentación de Supabase sobre migraciones
