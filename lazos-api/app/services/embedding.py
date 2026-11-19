from sentence_transformers import SentenceTransformer
from PIL import Image
import io
import logging

logger = logging.getLogger(__name__)

# Usamos clip-ViT-B-32 que genera vectores de 512 dimensiones (coincide con VECTOR(512) en DB)
DEVICE = "cpu"
MODEL_NAME = "clip-ViT-B-32"
_model = None

def get_model():
    global _model
    if _model is None:
        try:
            logger.info(f"Cargando modelo {MODEL_NAME} en {DEVICE}...")
            _model = SentenceTransformer(MODEL_NAME, device=DEVICE)
        except Exception as e:
            logger.error(f"Error cargando modelo CLIP: {e}")
            raise e
    return _model

def generate_image_embedding(image_bytes: bytes) -> list[float]:
    """
    Generar un embedding de 512 dimensiones para la imagen dada usando CLIP.
    Retorna el embedding como una lista de floats.
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))  # type: ignore
        
        # CLIP requiere imágenes RGB
        if image.mode != "RGB":
            image = image.convert("RGB")  # type: ignore
            
        model = get_model()
        # Generar embedding
        embedding = model.encode(image)
        
        return embedding.tolist()
    except Exception as e:
        logger.error(f"Fallo al generar el embedding de la imagen: {e}")
        return []
