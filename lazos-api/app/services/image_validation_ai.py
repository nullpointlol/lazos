"""
Servicio de validación de imágenes usando Cloudflare Workers AI
Detecta contenido NSFW/inapropiado en imágenes
"""
import httpx
import logging
import base64
import json
from typing import Optional, Dict, Any
from app.config import settings # Import settings

logger = logging.getLogger(__name__)


class ImageValidationAI:
    """Validador de imágenes usando Cloudflare Workers AI"""

    def __init__(self, account_id: Optional[str] = None, api_token: Optional[str] = None):
        self.account_id = account_id
        self.api_token = api_token
        # Modelo de Cloudflare AI para detección NSFW
        self.model = "@cf/microsoft/resnet-50"  # Modelo de clasificación de imágenes

        self.endpoint: Optional[str] = None
        if self.account_id and self.api_token and settings.CLOUDFLARE_AI_GATEWAY_URL:
            self.endpoint = f"{settings.CLOUDFLARE_AI_GATEWAY_URL.format(account_id=self.account_id)}/{self.model}"

    async def validate_image(self, image_bytes: bytes) -> Optional[Dict[str, Any]]:
        """
        Valida si la imagen contiene contenido apropiado para publicación.

        Args:
            image_bytes: Bytes de la imagen a validar

        Returns:
            dict: {
                "is_valid": bool,
                "reason": str,
                "confidence": float (0.0-1.0),
                "service": str  # "cloudflare_ai"
            }
        """
        if not self.account_id or not self.api_token:
            logger.warning("Cloudflare AI no configurado, aprobando imagen por defecto")
            return {
                "is_valid": True,
                "reason": "AI no configurada",
                "confidence": 0.0,
                "service": "none"
            }

        try:
            # Para modelos de clasificacion como ResNet-50 en Cloudflare Workers AI,
            # enviar los bytes binarios directamente como el cuerpo de la peticion es el metodo mas limpio,
            # eficiente y estandar, evitando codificacion innecesaria en JSON/base64.
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/octet-stream"
            }

            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(self.endpoint, headers=headers, content=image_bytes)  # type: ignore

                if response.status_code != 200:
                    logger.error(f"Cloudflare AI error: {response.status_code} - {response.text}")
                    # En caso de error de API, retornar None para triggear fallback
                    return None

                try:
                    result = response.json()
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to decode JSON from Cloudflare NSFW classifier response: {response.text}")
                    return None

                # Analizar respuesta de Cloudflare AI
                # El modelo ResNet-50 devuelve clasificaciones
                # Buscamos etiquetas relacionadas con NSFW o contenido inapropiado
                predictions = result.get("result", [])

                # Lista de etiquetas que indican contenido inapropiado
                nsfw_labels = [
                    "bikini", "swimsuit", "underwear", "brassiere",
                    "miniskirt", "abaya", "academic_gown"
                ]

                # Verificar si hay predicciones con alta confianza de contenido inapropiado
                max_nsfw_confidence = 0.0
                detected_label = None

                for pred in predictions:
                    label = pred.get("label", "").lower()
                    score = pred.get("score", 0.0)

                    # Si encontramos una etiqueta NSFW con alta confianza
                    if any(nsfw_term in label for nsfw_term in nsfw_labels):
                        if score > max_nsfw_confidence:
                            max_nsfw_confidence = score
                            detected_label = label

                # Umbral de confianza para rechazar (70%)
                is_valid = max_nsfw_confidence < 0.7

                logger.info(f"[Cloudflare AI] Imagen validada: valid={is_valid}, label={detected_label}, confidence={max_nsfw_confidence}")

                return {
                    "is_valid": is_valid,
                    "reason": f"Contenido inapropiado detectado: {detected_label}" if not is_valid else "Imagen apropiada",
                    "confidence": max_nsfw_confidence if not is_valid else (1.0 - max_nsfw_confidence),
                    "service": "cloudflare_ai"
                }

        except httpx.TimeoutException:
            logger.error("Cloudflare AI timeout después de 15s")
            return None
        except httpx.RequestError as e:
            logger.error(f"Cloudflare AI request error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error validando imagen con Cloudflare AI: {str(e)}")
            return None


_instance = None


def get_image_validation_ai() -> ImageValidationAI:
    """
    Singleton para obtener instancia de ImageValidationAI.
    Carga credenciales desde settings en primera llamada.
    """
    global _instance
    if _instance is None:
        from app.config import settings
        _instance = ImageValidationAI(
            account_id=getattr(settings, 'CLOUDFLARE_ACCOUNT_ID', None),
            api_token=getattr(settings, 'CLOUDFLARE_WORKERSAI_API_TOKEN', None)
        )
    return _instance
