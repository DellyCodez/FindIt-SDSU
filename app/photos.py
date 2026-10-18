"""Validate and normalize report photos before they touch persistent storage."""

from io import BytesIO
from pathlib import Path
import warnings

from PIL import Image, ImageOps, UnidentifiedImageError


MAX_PHOTOS = 3
MAX_UPLOAD_BYTES = 8 * 1024 * 1024
MAX_PIXELS = 20_000_000
MAX_EDGE = 1800
Image.MAX_IMAGE_PIXELS = MAX_PIXELS
FORMATS = {".jpg": "JPEG", ".jpeg": "JPEG", ".png": "PNG", ".webp": "WEBP"}


class PhotoValidationError(ValueError):
    pass


def prepare_photos(files):
    """Return re-encoded WebP bytes and dimensions, in the submitted order."""
    files = [file for file in files if file.filename]
    if len(files) > MAX_PHOTOS:
        raise PhotoValidationError("Choose no more than three photos.")
    prepared = []
    for file in files:
        expected = FORMATS.get(Path(file.filename).suffix.lower())
        if expected is None:
            raise PhotoValidationError("Photos must be JPEG, PNG, or WebP files.")
        raw = file.stream.read(MAX_UPLOAD_BYTES + 1)
        if len(raw) > MAX_UPLOAD_BYTES:
            raise PhotoValidationError("Each photo must be 8 MB or smaller.")
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error", Image.DecompressionBombWarning)
                with Image.open(BytesIO(raw)) as source:
                    if source.format != expected or getattr(source, "n_frames", 1) != 1:
                        raise PhotoValidationError("A photo has invalid or unsupported image content.")
                    if source.width * source.height > MAX_PIXELS:
                        raise PhotoValidationError("A photo has too many pixels.")
                    upright = ImageOps.exif_transpose(source)
                    image = upright.convert("RGBA" if "A" in upright.getbands() else "RGB")
                    image.thumbnail((MAX_EDGE, MAX_EDGE), Image.Resampling.LANCZOS)
                    output = BytesIO()
                    image.save(output, format="WEBP", quality=82, method=6)
                    prepared.append({"content": output.getvalue(), "width": image.width,
                                     "height": image.height})
        except (Image.DecompressionBombError, Image.DecompressionBombWarning) as error:
            raise PhotoValidationError("A photo has too many pixels.") from error
        except (OSError, ValueError, UnidentifiedImageError) as error:
            if isinstance(error, PhotoValidationError):
                raise
            raise PhotoValidationError("A photo could not be read as a valid image.") from error
    return prepared
