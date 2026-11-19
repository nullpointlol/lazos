"""
Servicio de procesamiento de imágenes
Redimensiona y comprime imágenes para optimizar almacenamiento
"""
from PIL import Image, ImageOps
from io import BytesIO
from typing import Tuple, Any


class ImageService:
    """Servicio para procesar imágenes de mascotas"""

    # Configuración según spec
    MAX_SIZE = 2000  # px máximo del lado mayor
    THUMBNAIL_SIZE = 400  # px para thumbnail
    QUALITY = 85  # calidad JPEG

    # Optimización para Cloudflare Workers AI para evitar OOM y payloads grandes (>200k base64)
    AI_MAX_SIZE = 512
    AI_QUALITY = 60

    @staticmethod
    def process_for_ai(image_bytes: bytes) -> bytes:
        """
        Procesa una imagen para enviarla a Cloudflare Workers AI:
        1. Convierte a RGB (elimina transparencias)
        2. Redimensiona agresivamente para mantener la resolución ideal para OCR pero con un tamaño <100KB
        3. Comprime con menor calidad (70%) para reducir el tamaño de la cadena Base64 a <133k caracteres

        Args:
            image_bytes: Bytes de la imagen original

        Returns:
            bytes: Bytes de la imagen altamente comprimida
        """
        try:
            # Abrir imagen y convertir a RGB
            img: Any = Image.open(BytesIO(image_bytes))

            # Aplicar rotación EXIF automáticamente
            img = ImageOps.exif_transpose(img)

            # Convertir a RGB (maneja PNG con transparencia, RGBA, etc.)
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')

            # Redimensionar si supera el tamaño máximo para la IA
            if max(img.size) > ImageService.AI_MAX_SIZE:
                img.thumbnail(
                    (ImageService.AI_MAX_SIZE, ImageService.AI_MAX_SIZE),
                    Image.Resampling.LANCZOS
                )

            # Comprimir
            buffer = BytesIO()
            img.save(
                buffer,
                format='JPEG',
                quality=ImageService.AI_QUALITY,
                optimize=True
            )

            return buffer.getvalue()

        except Exception as e:
            raise ValueError(f"Error procesando imagen para la IA: {str(e)}")

    @staticmethod
    def process_upload(image_bytes: bytes) -> Tuple[bytes, bytes]:
        """
        Procesa una imagen subida:
        1. Convierte a RGB (elimina transparencias)
        2. Redimensiona si supera MAX_SIZE
        3. Genera thumbnail
        4. Comprime ambas imágenes

        Args:
            image_bytes: Bytes de la imagen original

        Returns:
            Tuple[bytes, bytes]: (imagen_procesada, thumbnail)

        Raises:
            ValueError: Si la imagen es inválida
        """
        try:
            # Abrir imagen y convertir a RGB
            img: Any = Image.open(BytesIO(image_bytes))

            # Aplicar rotación EXIF automáticamente (fix para imágenes de celular)
            img = ImageOps.exif_transpose(img)

            # Convertir a RGB (maneja PNG con transparencia, RGBA, etc.)
            if img.mode in ('RGBA', 'LA', 'P'):
                # Crear fondo blanco
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')

            # Redimensionar imagen principal si es muy grande
            if max(img.size) > ImageService.MAX_SIZE:
                img.thumbnail(
                    (ImageService.MAX_SIZE, ImageService.MAX_SIZE),
                    Image.Resampling.LANCZOS
                )

            # Generar thumbnail
            thumb = img.copy()
            thumb.thumbnail(
                (ImageService.THUMBNAIL_SIZE, ImageService.THUMBNAIL_SIZE),
                Image.Resampling.LANCZOS
            )

            # Comprimir imagen principal
            main_buffer = BytesIO()
            img.save(
                main_buffer,
                format='JPEG',
                quality=ImageService.QUALITY,
                optimize=True
            )

            # Comprimir thumbnail
            thumb_buffer = BytesIO()
            thumb.save(
                thumb_buffer,
                format='JPEG',
                quality=ImageService.QUALITY,
                optimize=True
            )

            return main_buffer.getvalue(), thumb_buffer.getvalue()

        except Exception as e:
            raise ValueError(f"Error procesando imagen: {str(e)}")

    @staticmethod
    def validate_image(image_bytes: bytes, max_size_mb: int = 10) -> None:
        """
        Valida que la imagen sea válida y no supere el tamaño máximo

        Args:
            image_bytes: Bytes de la imagen
            max_size_mb: Tamaño máximo en MB

        Raises:
            ValueError: Si la imagen es inválida o muy grande
        """
        # Verificar tamaño
        size_mb = len(image_bytes) / (1024 * 1024)
        if size_mb > max_size_mb:
            raise ValueError(f"Imagen muy grande: {size_mb:.1f}MB. Máximo: {max_size_mb}MB")

        # Verificar que sea una imagen válida
        try:
            img = Image.open(BytesIO(image_bytes))  # type: ignore
            img.verify()
        except Exception as e:
            raise ValueError(f"Archivo no es una imagen válida: {str(e)}")
