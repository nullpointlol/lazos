# Desarrollo

## Stack

- **Web:** React 18, Vite, Tailwind CSS, Leaflet.
- **API:** Python 3.11, FastAPI, SQLAlchemy 2, PostgreSQL con PostGIS y pgvector.
- **Servicios:** Cloudflare R2 para las imágenes y Cloudflare Workers AI para moderar fotos y textos.

## Cómo levantarlo

Necesitás Python 3.11, Node.js 18 y Docker (para la base de datos).

1. Base de datos: `docker compose up -d db`
2. API:
   ```bash
   cd lazos-api
   python -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env            # completá DATABASE_URL y, para subir fotos, los datos de R2
   alembic upgrade head
   uvicorn app.main:app --reload
   ```
3. Web, en otra terminal:
   ```bash
   cd lazos-web
   npm install
   cp .env.example .env
   npm run dev
   ```
4. Entrá a <http://localhost:5173>. La documentación de la API queda en <http://localhost:8000/docs>.

## Más

- Configuración completa (R2, moderación, variables): [ai/08-DEPLOYMENT.md](ai/08-DEPLOYMENT.md).
- Arquitectura, modelos y API: [ai/README.md](ai/README.md).
- Lo que falta: [roadmap.md](roadmap.md).
