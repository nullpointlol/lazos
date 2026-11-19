# AGENTS.md — Lazos

Reglas para cualquier agente que trabaje en este repo. Documentación técnica: [docs/ai/](docs/ai/README.md).

## Stack
- `lazos-api/`: Python 3.11+, FastAPI, SQLAlchemy 2.0, Pydantic v2, `async/await` en E/S, tipado obligatorio.
- `lazos-web/`: React 18 con hooks, TypeScript, Tailwind, shadcn/ui, mobile-first.
- Orden de trabajo: base de datos → backend → API → frontend.

## Reglas
- Solo lo pedido, sin sobreingeniería. Ediciones puntuales: no se reescriben archivos enteros.
- Cada feature con su test. Tests y linters solo de lo tocado (`pytest`, `vitest`, `ruff`, `eslint`).
- Imágenes: `R2_PUBLIC_URL` en `.env` y bucket público. Puerto del backend: `$PORT` u `8000`.
- Migraciones: los modelos se importan en `alembic/env.py` (`target_metadata`).
- Secretos y datos personales: nunca en código, tests, docs ni commits.

## Commits y PRs
- Conventional Commits: `tipo(ámbito): resumen`, ≤ 60 caracteres, en español.
- Sin cuerpo, salvo contexto técnico imprescindible (≤ 3 líneas). Sin trailers, fechas ni nombres.
- Nunca a `main` directo. Un PR por cambio; se integra con squash: el título del PR es el commit. Descripción ≤ 2 líneas.
- Comentarios: qué y por qué técnico. Nunca quién lo pidió ni cuándo.
- Planes, estado y notas de proceso: fuera de este repo.
