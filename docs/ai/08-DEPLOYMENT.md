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
# CLOUDFLARE AI WORKERS (opcional - mejora validación)
# ========================================
# Si no se configuran, solo se usa Python NSFW detector (local)
CLOUDFLARE_ACCOUNT_ID=your_cloudflare_account_id
CLOUDFLARE_API_TOKEN=your_cloudflare_api_token

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

### 8.3 Configuración Cloudflare AI Workers (Opcional)

**💡 Mejora la validación de contenido con IA en la nube**

Si no configurás estas variables, el sistema funciona solo con Python NSFW detector (local).

**Beneficios con Cloudflare AI:**
- ✅ Validación de 100% de imágenes (Python NSFW + ResNet-50)
- ✅ Validación de texto semántica (Llama-3-8b)
- ✅ 97% menos llamadas API (solo valida sospechosas)
- ✅ 95% de posts validados en < 300ms

**Configuración:**

1. **Cloudflare Dashboard** → AI → Workers AI
2. Copiar **Account ID**
3. Crear **API Token** con permisos:
   - Workers AI: Read
4. Agregar a `.env`:
   ```bash
   CLOUDFLARE_ACCOUNT_ID=abc123...
   CLOUDFLARE_API_TOKEN=xxx...
   ```

**Modelos utilizados:**
- **Imágenes**: `@cf/microsoft/resnet-50` (clasificación de imágenes)
- **Texto**: `@cf/meta/llama-3-8b-instruct` (detección de spam/contenido inapropiado)

### 8.4 Docker Compose (Desarrollo)

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
      PORT: 8000
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

**Nota sobre el puerto:**
- El Dockerfile usa `${PORT:-8000}` para permitir que Railway asigne dinámicamente el puerto
- En desarrollo local, `PORT: 8000` asegura que siempre use el puerto 8000
- Railway inyecta automáticamente la variable `PORT` en producción

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

> **Nota:** Para comandos frecuentes de desarrollo y debugging, ver [AGENTS.md](../../AGENTS.md) sección "Comandos Frecuentes"

