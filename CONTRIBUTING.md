# Guía de Contribución

¡Gracias por tu interés en contribuir a LAZOS! 🐕🐈

Esta guía te ayudará a entender cómo contribuir efectivamente al proyecto.

## 📋 Tabla de Contenidos

- [Código de Conducta](#código-de-conducta)
- [¿Cómo puedo contribuir?](#cómo-puedo-contribuir)
- [Proceso de Desarrollo](#proceso-de-desarrollo)
- [Estándares de Código](#estándares-de-código)
- [Convenciones de Commits](#convenciones-de-commits)
- [Pull Request Process](#pull-request-process)

## 📜 Código de Conducta

Este proyecto se adhiere a un código de conducta de respeto mutuo:

- **Sé respetuoso**: Trata a todos con respeto y consideración
- **Sé constructivo**: Ofrece crítica constructiva, no destructiva
- **Sé colaborativo**: Trabajamos juntos para mejorar el proyecto
- **Sé inclusivo**: Damos la bienvenida a contribuidores de todos los niveles

## 🤝 ¿Cómo puedo contribuir?

### 🐛 Reportar Bugs

Si encontrás un bug:

1. **Verificá** que no exista ya un issue abierto
2. **Abrí un nuevo issue** con:
   - Título descriptivo
   - Pasos para reproducir el bug
   - Comportamiento esperado vs actual
   - Screenshots (si aplica)
   - Información del entorno (browser, OS, etc.)

**Template:**
```markdown
## Descripción del Bug
[Descripción clara del problema]

## Pasos para Reproducir
1. Ir a '...'
2. Click en '...'
3. Scroll hasta '...'
4. Ver error

## Comportamiento Esperado
[Qué esperabas que pasara]

## Comportamiento Actual
[Qué pasó realmente]

## Screenshots
[Si aplica]

## Entorno
- OS: [ej. macOS 14.0]
- Browser: [ej. Chrome 120]
- Version: [ej. 1.0.0]
```

### 💡 Sugerir Features

Para sugerir una nueva característica:

1. **Verificá** que no exista ya una sugerencia similar
2. **Abrí un issue** con etiqueta `enhancement`
3. **Describí**:
   - El problema que resuelve
   - La solución propuesta
   - Alternativas consideradas
   - Impacto en usuarios

### 🔧 Contribuir Código

1. **Fork** el repositorio
2. **Creá una branch** desde `main`:
   ```bash
   git checkout -b feature/nombre-descriptivo
   ```
3. **Realizá tus cambios** siguiendo los estándares de código
4. **Commit** tus cambios con mensajes descriptivos
5. **Push** a tu fork
6. **Abrí un Pull Request**

## 🛠️ Proceso de Desarrollo

### Setup Local

```bash
# Clonar tu fork
git clone https://github.com/tu-usuario/lazos.git
cd lazos

# Agregar upstream
git remote add upstream https://github.com/nullpointlol01/lazos.git

# Instalar dependencias
cd lazos-api && pip install -r requirements.txt
cd ../lazos-web && npm install
```

### Workflow

```bash
# 1. Actualizar tu fork
git checkout main
git pull upstream main

# 2. Crear branch de feature
git checkout -b feature/mi-feature

# 3. Hacer cambios y commit
git add .
git commit -m "feat: agregar nueva funcionalidad"

# 4. Push a tu fork
git push origin feature/mi-feature

# 5. Abrir Pull Request en GitHub
```

### Testing

Antes de hacer commit:

```bash
# Frontend
cd lazos-web
npm run lint          # Verificar linting
npm run build         # Verificar que builda sin errores

# Backend
cd lazos-api
# (Tests pendientes de implementar)
# pytest
```

## 📝 Estándares de Código

### Python (Backend)

```python
# Usar type hints
def crear_post(data: PostCreate, db: Session) -> Post:
    pass

# Docstrings para funciones públicas
def validar_imagen(archivo: UploadFile) -> bool:
    """
    Valida que una imagen sea válida y segura.

    Args:
        archivo: Archivo subido por el usuario

    Returns:
        True si la imagen es válida
    """
    pass

# PEP 8 para naming
class PostService:  # PascalCase para clases
    def crear_post(self):  # snake_case para funciones
        MAX_SIZE = 5_000_000  # UPPER_SNAKE_CASE para constantes
```

**Herramientas:**
- `black` para formateo automático
- `flake8` para linting
- `mypy` para type checking (opcional)

### JavaScript/React (Frontend)

```jsx
// Nombres descriptivos
const PostCard = ({ post }) => {  // PascalCase para componentes
  const [isExpanded, setIsExpanded] = useState(false)  // camelCase para variables

  // Comentarios para lógica compleja
  const handleClick = () => {
    // Prevenir múltiples clicks
    if (isLoading) return

    setIsExpanded(!isExpanded)
  }

  return (
    <div className="bg-card rounded-lg">
      {/* Usar semantic HTML */}
      <h2>{post.title}</h2>
    </div>
  )
}
```

**Herramientas:**
- ESLint para linting
- Prettier para formateo (opcional)

### CSS/Tailwind

```jsx
// Preferir variables CSS sobre colores hardcodeados
<div className="bg-background text-foreground">  {/* ✅ */}
<div className="bg-white text-black">            {/* ❌ */}

// Ordenar clases de forma consistente
<div className="flex items-center gap-4 px-4 py-2 bg-card rounded-lg">
  {/* Layout → Spacing → Visual → Others */}
</div>
```

## 💬 Convenciones de Commits

Usamos [Conventional Commits](https://www.conventionalcommits.org/) para commits descriptivos y automáticos changelogs.

### Formato

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

- `feat`: Nueva característica
- `fix`: Corrección de bug
- `docs`: Cambios en documentación
- `style`: Formateo, punto y coma faltante, etc.
- `refactor`: Refactorización de código
- `perf`: Mejora de performance
- `test`: Agregar o modificar tests
- `chore`: Cambios en build, dependencias, etc.

### Ejemplos

```bash
# Feature simple
git commit -m "feat: agregar filtro por color de mascota"

# Fix con scope
git commit -m "fix(map): corregir zoom en móviles"

# Feature con body
git commit -m "feat: implementar búsqueda por similitud

- Agregar endpoint /search/similar
- Integrar CLIP embeddings
- Crear UI para upload de imagen de búsqueda"

# Breaking change
git commit -m "feat!: cambiar formato de respuesta de API

BREAKING CHANGE: El campo 'location' ahora retorna un objeto {lat, lon}
en lugar de string 'lat,lon'"
```

### Scopes Comunes

- `frontend` / `backend`
- `api` / `ui` / `db`
- `posts` / `alerts` / `map` / `search` / `admin`
- `auth` / `moderation` / `upload`

## 🔄 Pull Request Process

### Antes de Abrir el PR

- [ ] El código sigue los estándares del proyecto
- [ ] Los tests pasan (si existen)
- [ ] El build completa sin errores
- [ ] La documentación está actualizada
- [ ] Los commits siguen Conventional Commits
- [ ] La branch está actualizada con `main`

### Template de PR

```markdown
## Descripción
[Descripción clara de los cambios]

## Tipo de Cambio
- [ ] Bug fix (cambio que corrige un issue)
- [ ] Nueva feature (cambio que agrega funcionalidad)
- [ ] Breaking change (fix o feature que causaría que funcionalidad existente no funcione)
- [ ] Documentación

## ¿Cómo se Testeó?
[Describir los tests realizados]

## Screenshots (si aplica)
[Screenshots de los cambios]

## Checklist
- [ ] Mi código sigue los estándares del proyecto
- [ ] He realizado self-review de mi código
- [ ] He comentado código complejo
- [ ] He actualizado la documentación
- [ ] Mis cambios no generan warnings
- [ ] Los tests pasan
```

### Proceso de Review

1. **Automático**: GitHub Actions verifica linting y build
2. **Manual**: Un maintainer revisa el código
3. **Feedback**: Se solicitan cambios si es necesario
4. **Aprobación**: El PR es aprobado y mergeado

### Después del Merge

Tu contribución será incluida en el próximo release. ¡Gracias! 🎉

## 🎯 Áreas que Necesitan Ayuda

Siempre buscamos ayuda en:

- 🧪 **Testing**: Escribir tests unitarios y de integración
- 📝 **Documentación**: Mejorar guías y ejemplos
- 🐛 **Bug Fixes**: Resolver issues abiertos
- ♿ **Accesibilidad**: Mejorar a11y del sitio
- 🌍 **Internacionalización**: Agregar soporte para otros idiomas
- 🎨 **UI/UX**: Mejorar diseño y experiencia de usuario
- ⚡ **Performance**: Optimizar queries, carga de imágenes, etc.

Ver issues con label `good-first-issue` para empezar.

## 📞 Preguntas?

Si tenés preguntas sobre cómo contribuir:

- Abrí un [issue](https://github.com/nullpointlol01/lazos/issues) con label `question`
- Iniciá una [discusión](https://github.com/nullpointlol01/lazos/discussions)

---

**¡Gracias por hacer LAZOS mejor!** 🐾
