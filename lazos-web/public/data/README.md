# Datos de Localidades - API Georef

Este directorio contiene los datos de localidades de Argentina para autocomplete offline.

## Archivos

- **localidades.json**: ~52,000 localidades de todas las provincias de Argentina
  - Incluye TODAS las localidades del país
  - Datos organizados por provincia
  - Fuente: API Georef (datos oficiales del INDEC)
  - Fecha de actualización: 2025-12-27

- **provincias.json**: 24 provincias argentinas
  - Listado completo de provincias
  - Códigos y nombres oficiales

## ¿Cuándo actualizar?

Los datos de localidades cambian raramente. Se recomienda actualizar:

- **Cada 6-12 meses**: Para mantener datos actualizados
- **Al agregar soporte para otra provincia**: Descargar datos de esa provincia
- **Si notan localidades faltantes**: Actualizar manualmente o re-descargar

## Cómo actualizar los datos

### Descargar todas las localidades de Argentina

```bash
# Desde el directorio raíz del proyecto
# ~52,000 localidades de todo el país
curl "https://apis.datos.gob.ar/georef/api/localidades?max=55000&campos=id,nombre,provincia.nombre,departamento.nombre" \
  -o lazos-web/public/data/localidades.json
```

### Descargar provincias

```bash
curl "https://apis.datos.gob.ar/georef/api/provincias?campos=id,nombre" \
  -o lazos-web/public/data/provincias.json
```

### Script Python para descargar y organizar

```python
import requests
import json

# Descargar todas las localidades
url = "https://apis.datos.gob.ar/georef/api/localidades"
params = {
    "max": 55000,
    "campos": "id,nombre,provincia.nombre,departamento.nombre"
}

response = requests.get(url, params=params)
data = response.json()

# Organizar por provincia
localidades_por_provincia = {}
for loc in data.get("localidades", []):
    provincia = loc.get("provincia", {}).get("nombre")
    if provincia:
        if provincia not in localidades_por_provincia:
            localidades_por_provincia[provincia] = []
        localidades_por_provincia[provincia].append(loc)

# Guardar
with open("localidades.json", "w", encoding="utf-8") as f:
    json.dump(localidades_por_provincia, f, ensure_ascii=False, indent=2)

print(f"✅ Descargadas localidades de {len(localidades_por_provincia)} provincias")
```

## Formato del JSON

**localidades.json** (organizado por provincia):
```json
{
  "Buenos Aires": [
    {
      "id": "06784020000",
      "nombre": "Martínez",
      "provincia": {
        "id": "06",
        "nombre": "Buenos Aires"
      },
      "departamento": {
        "id": "06784",
        "nombre": "San Isidro"
      }
    }
  ],
  "Córdoba": [
    {
      "id": "14014010000",
      "nombre": "Córdoba",
      "provincia": {
        "id": "14",
        "nombre": "Córdoba"
      },
      "departamento": {
        "id": "14014",
        "nombre": "Capital"
      }
    }
  ]
}
```

**provincias.json**:
```json
{
  "provincias": [
    {
      "id": "06",
      "nombre": "Buenos Aires"
    },
    {
      "id": "14",
      "nombre": "Córdoba"
    }
  ]
}
```

## Documentación de API Georef

- **Sitio oficial**: https://www.argentina.gob.ar/georef
- **Documentación**: https://datosgobar.github.io/georef-ar-api/
- **Endpoint de localidades**: https://apis.datos.gob.ar/georef/api/localidades
- **Endpoint de direcciones**: https://apis.datos.gob.ar/georef/api/direcciones

## Ejemplos de uso de la API

### Buscar localidades con autocompletado

```bash
curl "https://apis.datos.gob.ar/georef/api/localidades?nombre=marti&provincia=buenos%20aires&max=10"
```

### Geocodificar una dirección

```bash
curl "https://apis.datos.gob.ar/georef/api/direcciones?direccion=Florida%202950&localidad=Martinez&provincia=buenos%20aires"
```

### Obtener información de una localidad específica

```bash
curl "https://apis.datos.gob.ar/georef/api/localidades?id=06784020000"
```

## Notas técnicas

- La API Georef **no tiene límite de requests** (es pública y gratuita)
- Los datos son actualizados periódicamente por el gobierno
- La API normaliza nombres automáticamente ("Bs.As." → "Buenos Aires")
- Incluye coordenadas geográficas precisas (WGS84)
- Soporta búsqueda fuzzy y autocompletado

## Troubleshooting

### Error: "No se encontraron localidades"

1. Verificar que el archivo JSON existe en `/public/data/`
2. Verificar que el JSON tiene el formato correcto
3. Revisar la consola del navegador para errores de fetch

### La API Georef no responde

1. Verificar conexión a internet
2. Intentar acceder directamente: https://apis.datos.gob.ar/georef/api/localidades
3. La API puede tener mantenimiento ocasional

### Localidad específica no aparece

1. Verificar que la localidad existe en el JSON local
2. Si es una localidad muy pequeña, puede no estar en el dataset
3. Considerar usar geocoding en tiempo real con API Georef
