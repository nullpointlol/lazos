# Documentación de Arquitectura de Validación e Interpretación de Imágenes

La arquitectura de validación y análisis de imágenes en LAZOS API está diseñada para proveer una experiencia rápida, segura y rica en contexto. Utiliza una combinación de estrategias heurísticas locales y modelos de Inteligencia Artificial (IA) avanzados de Cloudflare Workers AI para procesar, moderar y extraer información de las imágenes subidas por los usuarios.

## 1. Flujo General de Creación de Publicaciones (`/api/v1/posts`)

Cuando un usuario sube un avistamiento o reporte con imágenes, el backend ejecuta un pipeline multi-fase:

### Fase 1: Validación Básica (Síncrona)
- **Servicio:** `ImageService` (`app/services/image.py`)
- **Acción:** Verifica el peso máximo de la imagen (10 MB por defecto) y formato de archivo (mediante lectura de cabeceras). 
- **Objetivo:** Evitar que archivos malformados o excesivamente grandes saturen la memoria y los servicios de validación.

### Fase 2: Validación Híbrida de Contenido (Asíncrona)
- **Servicio:** `HybridImageValidator` (`app/services/hybrid_image_validator.py`)
- **Estrategia (2 Pasos):**
  1. **Filtro Rápido Local (Python NSFW):** Todas las imágenes pasan por `detect_nsfw` (`app/services/nsfw_detector.py`) en paralelo. Este validador heurístico local detecta patrones de tonos de piel, procesando en ~200ms sin costo de red.
  2. **Validación Profunda (Cloudflare AI):** Solo si el filtro rápido marca una imagen como sospechosa, la imagen se envía a Cloudflare Workers AI (`app/services/image_validation_ai.py` usando `ResNet-50`). Si la IA confirma que la imagen contiene contenido inapropiado, se rechaza la imagen o se marca con `pending_approval = True` dependiendo de la severidad (NSFW explícito se rechaza).

### Fase 3: Procesamiento y Almacenamiento
- **Servicio:** `ImageService` y `StorageService` (`app/services/storage.py`)
- **Acción:** 
  1. Redimensionamiento y compresión usando Pillow (tamaño original optimizado y un `thumbnail` cuadrado).
  2. Eliminación de datos EXIF (privacidad de geolocalización original).
  3. Carga en paralelo a Cloudflare R2.
- **Resultado:** URL pública completa para la imagen principal y su miniatura.

### Fase 4: Validación de Texto y Guardado en Base de Datos
- **Servicio:** `TextValidationAI` (`app/services/text_validation_ai.py`)
- **Acción:** Si el usuario incluye texto de descripción, se valida semánticamente usando `Llama-3-8b` en Cloudflare Workers AI para detectar spam, violencia explícita u ofuscaciones. Si el modelo detecta contenido dudoso, el post se guarda con `pending_approval = True`.
- **Resultado:** Se guarda el `Post` y los registros `PostImage` asociados en la base de datos PostgreSQL/PostGIS.

---

## 2. Flujo de Auto-completado de Formulario (OCR e IA Multimodal)

El frontend de LAZOS facilita el reporte de avistamientos mediante la ruta dedicada `POST /api/v1/posts/analyze-image`. 
Esto ocurre **antes** de que el usuario envíe el formulario final, mejorando la UX al autocompletar campos clave basados en el análisis visual.

### Endpoint de Análisis
- **Servicio:** `ImageAnalysisAI` (`app/services/image_analysis_ai.py`)
- **Modelo:** `@cf/meta/llama-3.2-11b-vision-instruct` (Cloudflare Workers AI Multimodal)

### Lógica y Modificaciones Recientes
El modelo de visión analiza la imagen base64 para retornar un JSON estricto (garantizado con parsing tolerante y validaciones manuales de fallback en Python). La IA evalúa la imagen extrayendo **dos** piezas principales de información que antes estaban fusionadas:

1. **`extracted_text`:** Transcripción literal de cualquier texto visible (ej: "Buscamos a Bobby, tel: 1234"). Muy útil para carteles de mascotas perdidas.
2. **`image_interpretation`:** Descripción visual que la IA hace del animal (ej: "Perro mediano, pelaje marrón oscuro, collar verde...").

### Manejo en Frontend (`NewPost.jsx`)
Cuando el frontend recibe la respuesta exitosa:
- Se autocompletan los metadatos (tipo de animal, tamaño, fecha deducida, datos de contacto).
- **Descripción Concatenada:** Se concatena inteligentemente el texto extraído (`extracted_text`) con la interpretación de la imagen (`image_interpretation`), unidas por un doble salto de línea (`\n\n`), inyectando ambos directamente en la caja de texto `description` del formulario de React. Esto le permite al usuario revisar y ajustar todo el contexto que la IA ha podido deducir, mejorando la completitud del reporte.

---

## 3. Pruebas de Integración y End-to-End (E2E)

La validación del sistema está reforzada por un robusto conjunto de tests E2E y de integración.

- **Tests de Endpoints Simples:** `test_endpoints.py` verifica la estructura correcta del API y comprueba las reglas de parseo, permitiendo un desarrollo veloz simulando las respuestas de Cloudflare AI con `AsyncMock`.
- **Tests E2E Reales (`test_e2e_validation.py`):** Estos tests **NO mockean los servicios de Cloudflare AI**. Ejecutan el flujo completo de validación y extracción utilizando las variables de entorno reales provistas en `.env`. 
  - `test_e2e_create_post_with_image`: Valida que una imagen estandar (`img_test.jpg`) pueda pasar por el validador híbrido y las validaciones de texto y subir correctamente (mockeando únicamente la persistencia a R2 y DB para no generar basura en producción).
  - `test_e2e_analyze_image`: Consume directamente el endpoint de análisis multimodal asegurando que `extracted_text` e `image_interpretation` regresen correctamente desde el servicio remoto en vivo.

## 4. Estructura de Respaldo (Fallback)
Si Cloudflare AI se encuentra inactivo, no configurado en `.env` (ausencia del API token) o lanza timeout:
1. **En validación:** El sistema confía en el validador local de Python (Fase 1) como fuente única de verdad.
2. **En auto-completado:** Retornará diccionarios vacíos sin bloquear la carga del formulario, asegurando degradación grácil. El usuario no podrá aprovechar la IA, pero el formulario seguirá siendo funcional y manual.
