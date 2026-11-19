import httpx
import logging
import json
import base64
import re
from typing import Optional, Dict, Any
from app.config import settings # Import settings

logger = logging.getLogger(__name__)

def clean_ai_text(text: str) -> str:
    if not text:
        return ""
    # Remove phrases like "Basado en la imagen", "Aquí tienes", "El texto dice:" at the start of lines, case insensitive
    prefixes = [
        r"(?i)^basado en la imagen,?\s*",
        r"(?i)^aqu[ií] tienes(?: la descripci[oó]n| el texto)?:?\s*",
        r"(?i)^el texto (?:dice|indica|muestra):?\s*",
        r"(?i)^en la imagen se ve:?\s*",
        r"(?i)^la imagen muestra:?\s*",
        r"(?i)^texto extra[ií]do:?\s*",
        r"(?i)^transcripci[oó]n:?\s*"
    ]
    cleaned = text.strip()
    
    # Apply substitutions
    for p in prefixes:
        cleaned = re.sub(p, "", cleaned).strip()
    
    # Strip enclosing quotes if any
    if (cleaned.startswith('"') and cleaned.endswith('"')) or (cleaned.startswith("'") and cleaned.endswith("'")):
        cleaned = cleaned[1:-1].strip()
        
    return cleaned

class ImageAnalysisAI:
    """Servicio de análisis de imágenes usando Cloudflare Workers AI para extraer información de reportes de mascotas."""

    def __init__(self, account_id: Optional[str] = None, api_token: Optional[str] = None):
        self.account_id = account_id
        self.api_token = api_token
        # Usamos el modelo multimodal oficial de Cloudflare Workers AI para vision
        self.model = "@cf/meta/llama-3.2-11b-vision-instruct"

        self.endpoint: Optional[str] = None
        if self.account_id and self.api_token and settings.CLOUDFLARE_AI_GATEWAY_URL:
            self.endpoint = f"{settings.CLOUDFLARE_AI_GATEWAY_URL.format(account_id=self.account_id)}/{self.model}"

    async def analyze_image_for_post(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Analiza la imagen utilizando un modelo multimodal de Cloudflare Workers AI.
        Retorna un diccionario con los campos extraídos y un fallback de descripción en español.
        """
        if not self.account_id or not self.api_token or not self.endpoint:
            logger.warning("Cloudflare AI no configurado, devolviendo análisis vacío.")
            return {
                "extracted_text_description": "No se pudo analizar la imagen automáticamente porque la IA no está configurada.",
                "animal_type": "dog",
                "sex": "unknown",
                "size": "medium",
                "location_name": None,
                "contact_method": None,
                "sighting_date": None
            }

        try:
            # Para Cloudflare Workers AI, llama-3.2-11b-vision-instruct acepta base64 o array de enteros.
            # El uso de base64 es altamente optimizado para red/memoria y evita payloads excesivos de texto.
            image_b64 = base64.b64encode(image_bytes).decode('utf-8')

            prompt = (
                "Analiza detalladamente esta imagen de una mascota o de un cartel de mascota perdida/encontrada. "
                "Tu objetivo es extraer y estructurar la información del reporte en español. "
                "Genera una transcripción completa del texto en la imagen y describe visualmente al animal en la interpretación. "
                "No uses frases introductorias como 'Basado en la imagen' ni explicaciones en tus campos de texto, ve directamente a la descripción e información real.\n"
                "Para 'contact_method', extrae activamente cualquier número de teléfono (por ejemplo, celular, whatsapp), email, o red social que figure en el cartel u hoja.\n"
                "Debes retornar ÚNICAMENTE un objeto JSON con los siguientes campos exactamente, sin rodeos, sin bloques de código ```json, "
                "simplemente texto plano JSON:\n\n"
                "{\n"
                '  "extracted_text": "Transcripción completa de todo el texto que veas en la imagen (cartel, collar, etc.) en español sin textos introductorios. Si no hay texto, usa un string vacío.",\n'
                '  "image_interpretation": "Descripción visual detallada del animal (su color, raza aparente, estado, pose, etc.) en español.",\n'
                '  "animal_type": "dog" o "cat" o "other" (elige uno basado en la imagen),\n'
                '  "sex": "male" o "female" o "unknown" (elige uno basado en el texto o características visuales si son claras),\n'
                '  "size": "small" o "medium" o "large" (elige uno basado en la imagen o texto),\n'
                '  "location_name": "Nombre del lugar, dirección, barrio o intersección mencionado en el cartel o inferido",\n'
                '  "contact_method": "Número de teléfono, email, redes sociales o cualquier medio de contacto mencionado",\n'
                '  "sighting_date": "Fecha del avistamiento en formato YYYY-MM-DD o null si no se menciona"\n'
                "}"
            )

            payload = {
                "prompt": prompt,
                "image": image_b64
            }

            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(self.endpoint, headers=headers, json=payload)

                if response.status_code != 200:
                    logger.error(f"Cloudflare Vision AI error: {response.status_code} - {response.text}")
                    return {
                        "extracted_text": "",
                        "image_interpretation": "",
                        "animal_type": "dog", # Default to dog
                        "sex": "unknown", # Default
                        "size": "medium", # Default
                        "location_name": None,
                        "contact_method": None,
                        "sighting_date": None,
                        "error": None
                    }

                try:
                    result = response.json()
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to decode JSON from Cloudflare Vision AI response: {response.text}")
                    return {
                        "extracted_text": "",
                        "image_interpretation": "",
                        "animal_type": "dog",
                        "sex": "unknown",
                        "size": "medium",
                        "location_name": None,
                        "contact_method": None,
                        "sighting_date": None,
                        "error": None
                    }
                logger.debug(f"Cloudflare Vision AI response: {result}")

                # La respuesta suele estar en result["result"]["response"] para modelos LLM
                # Para modelos de chat multimodal, es result["result"]["response"] o result["result"]["messages"][0]["content"]
                ai_response = result.get("result", {}).get("response", "")
                if not ai_response:
                    # Try to get from messages if it's a chat-like response
                    messages = result.get("result", {}).get("messages", [])
                    if messages and len(messages) > 0 and "content" in messages[0]:
                        ai_response = messages[0]["content"]

                if isinstance(ai_response, dict):
                    ai_response = json.dumps(ai_response)
                elif not isinstance(ai_response, str):
                    ai_response = str(ai_response)

                ai_response = ai_response.strip()



                # Intentar parsear el JSON retornado por la IA
                # Limpiar posibles bloques de código markdown si la IA no obedeció la instrucción de no incluirlos
                if ai_response.startswith("```"):
                    lines = ai_response.splitlines()
                    if lines[0].startswith("```json") or lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines and lines[-1].startswith("```"):
                        lines = lines[:-1]
                    ai_response = "\n".join(lines).strip()

                try:
                    # Intento de extracción más robusto del JSON
                    start_idx = ai_response.find('{')
                    end_idx = ai_response.rfind('}')
                    
                    if start_idx != -1 and end_idx != -1 and end_idx >= start_idx:
                        json_str = ai_response[start_idx:end_idx+1]
                    else:
                        json_str = ai_response

                    data = json.loads(json_str)
                    
                    # Normalizar tipo de animal
                    animal_type = data.get("animal_type", "dog")
                    if animal_type not in ["dog", "cat", "other"]:
                        animal_type = "dog"
                    data["animal_type"] = animal_type
                    
                    # Normalizar sexo (ej. 'male' / 'macho' / 'm' -> 'male')
                    sex_val = str(data.get("sex", "unknown")).lower()
                    if sex_val in ["macho", "male", "m"]:
                        data["sex"] = "male"
                    elif sex_val in ["hembra", "female", "f"]:
                        data["sex"] = "female"
                    else:
                        data["sex"] = "unknown"
                        
                    # Normalizar tamaño
                    size = data.get("size", "medium")
                    if size not in ["small", "medium", "large"]:
                        size = "medium"
                    data["size"] = size
                    
                    # Limpiar textos de meta-texto de IA
                    data["extracted_text"] = clean_ai_text(data.get("extracted_text", ""))
                    data["image_interpretation"] = clean_ai_text(data.get("image_interpretation", ""))
                    
                    # Normalizar campos opcionales para evitar strings que rompan Pydantic
                    for field in ["sighting_date", "location_name", "contact_method"]:
                        val = data.get(field)
                        if isinstance(val, str):
                            val_lower = val.lower().strip()
                            if val_lower in ["null", "none", "n/a", "na", "no mencionado", "unknown", "no", "false", "", "undefined"]:
                                data[field] = None
                    
                    # Asegurar que sighting_date sea una fecha válida YYYY-MM-DD
                    s_date = data.get("sighting_date")
                    if isinstance(s_date, str):
                        if not re.match(r"^\d{4}-\d{2}-\d{2}$", s_date.strip()):
                            data["sighting_date"] = None
                    
                    return data
                except json.JSONDecodeError as e:
                    logger.error(f"{e} | {ai_response}")
                    
                    # Intentar extraer usando expresiones regulares para evitar mostrar JSON roto en la descripción
                    extracted_text = ""
                    image_interpretation = ""
                    animal_type = "dog"
                    sex = "unknown"
                    size = "medium"
                    location_name = None
                    contact_method = None
                    sighting_date = None
                    
                    # Regex matching
                    ext_text_match = re.search(r'"extracted_text"\s*:\s*"([^"]*)"', ai_response)
                    if ext_text_match:
                        extracted_text = ext_text_match.group(1)
                        
                    img_interp_match = re.search(r'"image_interpretation"\s*:\s*"([^"]*)"', ai_response)
                    if img_interp_match:
                        image_interpretation = img_interp_match.group(1)
                    else:
                        # Fallback: quitar llaves y nombres de claves JSON para dar una descripción limpia
                        image_interpretation = re.sub(r'["\{\}\[\]]', '', ai_response).strip()
                        image_interpretation = re.sub(r'(extracted_text|image_interpretation|animal_type|sex|size|location_name|contact_method|sighting_date)\s*:\s*', '', image_interpretation)

                    anim_match = re.search(r'"animal_type"\s*:\s*"([^"]*)"', ai_response)
                    if anim_match:
                        animal_type = anim_match.group(1)
                        
                    sex_match = re.search(r'"sex"\s*:\s*"([^"]*)"', ai_response)
                    if sex_match:
                        sex = sex_match.group(1)
                        
                    size_match = re.search(r'"size"\s*:\s*"([^"]*)"', ai_response)
                    if size_match:
                        size = size_match.group(1)
                        
                    loc_match = re.search(r'"location_name"\s*:\s*"([^"]*)"', ai_response)
                    if loc_match:
                        location_name = loc_match.group(1)
                        
                    contact_match = re.search(r'"contact_method"\s*:\s*"([^"]*)"', ai_response)
                    if contact_match:
                        contact_method = contact_match.group(1)
                        
                    date_match = re.search(r'"sighting_date"\s*:\s*"([^"]*)"', ai_response)
                    if date_match:
                        sighting_date = date_match.group(1)

                    # Normalizar campos extraídos
                    if animal_type not in ["dog", "cat", "other"]:
                        animal_type = "dog"
                        
                    sex_val = str(sex).lower()
                    if sex_val in ["macho", "male", "m"]:
                        sex = "male"
                    elif sex_val in ["hembra", "female", "f"]:
                        sex = "female"
                    else:
                        sex = "unknown"
                        
                    if size not in ["small", "medium", "large"]:
                        size = "medium"
                        
                    if isinstance(location_name, str) and location_name.lower().strip() in ["null", "none", "n/a", "na", "no mencionado", "unknown", "no", "false", "", "undefined"]:
                        location_name = None
                    if isinstance(contact_method, str) and contact_method.lower().strip() in ["null", "none", "n/a", "na", "no mencionado", "unknown", "no", "false", "", "undefined"]:
                        contact_method = None
                    if isinstance(sighting_date, str):
                        sighting_date_val = sighting_date.strip()
                        if sighting_date_val.lower() in ["null", "none", "n/a", "na", "no mencionado", "unknown", "no", "false", "", "undefined"] or not re.match(r"^\d{4}-\d{2}-\d{2}$", sighting_date_val):
                            sighting_date = None

                    return {
                        "extracted_text": clean_ai_text(extracted_text),
                        "image_interpretation": clean_ai_text(image_interpretation),
                        "animal_type": animal_type,
                        "sex": sex,
                        "size": size,
                        "location_name": location_name,
                        "contact_method": contact_method,
                        "sighting_date": sighting_date,
                        "error": None
                    }

        except httpx.TimeoutException as e:
            logger.error(f"Timeout al analizar imagen con Cloudflare AI (60s excedidos): {str(e)}")
            return {
                "extracted_text": "",
                "image_interpretation": "El análisis de la imagen tardó demasiado y expiró. Intente con otra imagen.",
                "animal_type": "dog",
                "sex": "unknown",
                "size": "medium",
                "location_name": None,
                "contact_method": None,
                "sighting_date": None,
                "error": "timeout"
            }
        except httpx.RequestError as e:
            logger.error(f"Error de red/petición al conectar con Cloudflare AI: {str(e)}")
            return {
                "extracted_text": "",
                "image_interpretation": "Error de conexión al analizar la imagen. Por favor, intente nuevamente.",
                "animal_type": "dog",
                "sex": "unknown",
                "size": "medium",
                "location_name": None,
                "contact_method": None,
                "sighting_date": None,
                "error": "network_error"
            }
        except Exception as e:
            logger.exception("Error inesperado analizando imagen con Cloudflare AI")
            return {
                "extracted_text": "",
                "image_interpretation": "", # No description on unexpected errors
                "animal_type": "dog",
                "sex": "unknown",
                "size": "medium",
                "location_name": None,
                "contact_method": None,
                "sighting_date": None,
                "error": str(e)
            }

_instance = None

def get_image_analysis_ai() -> ImageAnalysisAI:
    """Singleton para obtener la instancia de ImageAnalysisAI."""
    global _instance
    if _instance is None:
        from app.config import settings
        _instance = ImageAnalysisAI(
            account_id=getattr(settings, 'CLOUDFLARE_ACCOUNT_ID', None),
            api_token=getattr(settings, 'CLOUDFLARE_WORKERSAI_API_TOKEN', None),
        )
    return _instance
