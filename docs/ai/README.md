# LAZOS - Documentación para Agentes IA

**Versión**: 2.0
**Última actualización**: 2026-01-10
**Propósito**: Documentación completa y modular para agentes IA que desarrollan o mantienen el proyecto LAZOS

---

## 🚀 Inicio Rápido

**¿Primera vez en el proyecto?** → Lee **[AGENTS.md](../../AGENTS.md)** primero para una guía rápida con:
- Stack y estructura del proyecto
- Comandos frecuentes
- Configuración crítica
- Errores comunes y debugging
- Checklist de desarrollo

Luego profundiza en la documentación modular según tu tarea específica.

---

## 📚 Guías de Desarrollo

Esta documentación está dividida en módulos temáticos para facilitar la navegación y el mantenimiento:

### 1️⃣ [Visión del Proyecto](./01-PROJECT-OVERVIEW.md)
- Origen y descripción del proyecto
- Propuesta de valor y diferenciadores
- Usuarios objetivo

### 2️⃣ [Arquitectura Técnica](./02-ARCHITECTURE.md)
- Stack tecnológico completo
- Estructura de directorios
- Dependencias del proyecto

### 4️⃣ [Modelos de Base de Datos](./04-DATABASE-MODELS.md)
- Esquemas de tablas (Post, Alert, Report)
- Relaciones y constraints
- Índices y optimizaciones

### 5️⃣ [Referencia de API](./05-API-REFERENCE.md)
- Endpoints REST completos
- Request/Response schemas
- Ejemplos de uso

### 6️⃣ [Guía de Frontend](./06-FRONTEND-GUIDE.md)
- Componentes principales
- Páginas y rutas
- Hooks personalizados
- Gestión de estado

### 7️⃣ [Flujos de Usuario](./07-USER-WORKFLOWS.md)
- Creación de posts
- Búsqueda y filtros
- Sistema de reportes
- Panel de moderación

### 8️⃣ [Deployment](./08-DEPLOYMENT.md)
- Configuración de variables de entorno
- Deployment en producción (Railway, Vercel, Supabase)
- Troubleshooting común

### 9️⃣ [Decisiones de Arquitectura](./09-ARCHITECTURE-DECISIONS.md)
- ADRs (Architecture Decision Records)
- Justificación de tecnologías elegidas
- Trade-offs importantes

### 🔟 [Validación de Imágenes](./10-IMAGE-VALIDATION.md)
- Validación heurística local e IA
- OCR y auto-completado (Cloudflare Vision)
- Estructura de pruebas E2E

---

## 🎯 Cómo Usar Esta Documentación

### Para agentes IA nuevos en el proyecto:
1. **Lee** [AGENTS.md](../../AGENTS.md) para contexto rápido y comandos esenciales
2. **Profundiza según tu tarea**:
   - Trabajando en backend → [04-DATABASE-MODELS.md](./04-DATABASE-MODELS.md) + [05-API-REFERENCE.md](./05-API-REFERENCE.md)
   - Trabajando en frontend → [06-FRONTEND-GUIDE.md](./06-FRONTEND-GUIDE.md)
   - Configurando deployment → [08-DEPLOYMENT.md](./08-DEPLOYMENT.md)
   - Entender el contexto del negocio → [01-PROJECT-OVERVIEW.md](./01-PROJECT-OVERVIEW.md)
   - Comprender decisiones técnicas → [09-ARCHITECTURE-DECISIONS.md](./09-ARCHITECTURE-DECISIONS.md)

### Para actualizar la documentación:
- **Cambio en API**: Actualizar [05-API-REFERENCE.md](./05-API-REFERENCE.md)
- **Nuevo componente**: Actualizar [06-FRONTEND-GUIDE.md](./06-FRONTEND-GUIDE.md)
- **Cambio en DB**: Actualizar [04-DATABASE-MODELS.md](./04-DATABASE-MODELS.md)
- **Decisión arquitectónica**: Documentar en [09-ARCHITECTURE-DECISIONS.md](./09-ARCHITECTURE-DECISIONS.md)

---

## 📝 Convenciones

- Todos los archivos usan Markdown con syntax highlighting
- Los ejemplos de código incluyen comentarios explicativos
- Las rutas de archivos son absolutas desde la raíz del proyecto
- Los diagramas usan formato ASCII art para portabilidad

---

## 🔗 Enlaces Rápidos

- **[AGENTS.md](../../AGENTS.md)** - Reglas para agentes
- **[README Principal](../../README.md)** - Quickstart para usuarios
- **[08-DEPLOYMENT.md](08-DEPLOYMENT.md)** - Guía de deployment detallada
- **[API Docs (Swagger)](http://localhost:8000/docs)** - Documentación interactiva (requiere backend corriendo)

