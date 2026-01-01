# SOLUCIÓN BUG IMÁGENES

## PROBLEMA
Las URLs de imágenes se guardan como `/posts/uuid.jpg` en lugar de `https://pub-XXXXXXXXXXXXX.r2.dev/posts/uuid.jpg`

## CAUSA RAÍZ
El backend NO se reinició después de agregar `R2_PUBLIC_URL` al archivo `.env`.

Pydantic Settings carga el `.env` UNA SOLA VEZ al arrancar FastAPI. Si modificas `.env` mientras el servidor está corriendo, los cambios NO se aplican hasta reiniciar.

## SOLUCIÓN

### 1. Detener el backend
Presiona `Ctrl+C` en la terminal donde corre el backend

### 2. Verificar .env
```bash
cd lazos-api
grep R2_PUBLIC_URL .env
```

Debe mostrar:
```
R2_PUBLIC_URL=https://pub-XXXXXXXXXXXXX.r2.dev
```

### 3. Reiniciar el backend
```bash
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Verificar logs de inicio

Deberías ver:
```
================================================================================
LAZOS API - CONFIGURACIÓN AL INICIO
================================================================================
R2_PUBLIC_URL: https://pub-XXXXXXXXXXXXX.r2.dev
✅ R2_PUBLIC_URL configurado correctamente
================================================================================
```

### 5. Crear un post de prueba

Al subir una imagen, deberías ver en logs del backend:
```
[StorageService] base_url = 'https://pub-XXXXXXXXXXXXX.r2.dev'
[StorageService] image_url generada: https://pub-XXXXXXXXXXXXX.r2.dev/posts/{uuid}.jpg
```

Y en logs del frontend:
```
[FRONTEND] image_url: https://pub-XXXXXXXXXXXXX.r2.dev/posts/{uuid}.jpg
[PostCard] Imagen cargada exitosamente: https://...
```

### 6. Verificar que las imágenes cargan

- Las imágenes deberían mostrarse en el feed
- No más error 404 o placeholders "Sin imagen"

## VERIFICACIÓN FINAL

Si después de reiniciar SIGUE fallando:
1. Copiar los logs completos del startup
2. Copiar los logs de [StorageService]
3. Verificar que el .env está en la ruta correcta (lazos-api/.env)
