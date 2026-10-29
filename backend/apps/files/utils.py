import io
import logging
from PIL import Image, ImageOps

logger = logging.getLogger(__name__)

def generate_compressed_thumbnail(image_bytes: bytes, max_size=(480, 480), quality=80) -> bytes | None:
    """
    Generate a high-efficiency compressed WebP thumbnail from raw image bytes.
    Preserves aspect ratio, auto-orients based on EXIF, and restricts dimensions to max_size.
    Produces crisp, lightweight (~15KB-30KB) thumbnails that load lightning fast.
    """
    if not image_bytes:
        return None
    try:
        with Image.open(io.BytesIO(image_bytes)) as img:
            # Handle orientation from EXIF if present
            try:
                img = ImageOps.exif_transpose(img)
            except Exception:
                pass

            # Convert color mode
            if img.mode in ('RGBA', 'LA'):
                pass
            elif img.mode == 'P':
                if 'transparency' in img.info:
                    img = img.convert('RGBA')
                else:
                    img = img.convert('RGB')
            elif img.mode != 'RGB':
                img = img.convert('RGB')

            # Lanczos downsampling for high-fidelity photographer thumbnails
            img.thumbnail(max_size, Image.Resampling.LANCZOS)

            out_io = io.BytesIO()
            img.save(out_io, format='WEBP', quality=quality, method=4)
            return out_io.getvalue()
    except Exception as e:
        logger.error(f"Failed to generate compressed thumbnail: {e}")
        return None
