"""Validate and re-encode optional report photos before storing them locally."""

from io import BytesIO
from pathlib import Path
import warnings

from PIL import Image, ImageOps, UnidentifiedImageError


MAX_PHOTOS = 3
MAX_INPUT_BYTES = 5 * 1024 * 1024
MAX_PIXELS = 20_000_000
MAX_EDGE = 1600
FORMATS = {".jpg": "JPEG", ".jpeg": "JPEG", ".png": "PNG", ".webp": "WEBP"}
Image.MAX_IMAGE_PIXELS = MAX_PIXELS


class PhotoError(ValueError):
    """A photo cannot be accepted; show the message beside the upload field."""


def prepare_photos(files):
    selected = [file for file in files if file and file.filename]
    if len(selected) > MAX_PHOTOS:
        raise PhotoError("Choose no more than three photos.")
    photos = []
    for upload in selected:
        extension = Path(upload.filename).suffix.lower()
        if extension not in FORMATS:
            raise PhotoError("Photos must be JPEG, PNG, or WebP files.")
        raw = upload.stream.read(MAX_INPUT_BYTES + 1)
        if len(raw) > MAX_INPUT_BYTES:
            raise PhotoError("Each photo must be 5 MB or smaller.")
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error", Image.DecompressionBombWarning)
                with Image.open(BytesIO(raw)) as check:
                    if check.format != FORMATS[extension]:
                        raise PhotoError("The photo content does not match its file type.")
                    if check.width * check.height > MAX_PIXELS:
                        raise PhotoError("The photo is too large to process.")
                    check.verify()
                with Image.open(BytesIO(raw)) as source:
                    image = ImageOps.exif_transpose(source)
                    image.thumbnail((MAX_EDGE, MAX_EDGE), Image.Resampling.LANCZOS)
                    if "A" in image.getbands() or "transparency" in image.info:
                        background = Image.new("RGBA", image.size, "white")
                        image = Image.alpha_composite(background, image.convert("RGBA")).convert("RGB")
                    else:
                        image = image.convert("RGB")
                    output = BytesIO()
                    image.save(output, format="WEBP", quality=83, method=6)
                    encoded = output.getvalue()
                    if len(encoded) > 8 * 1024 * 1024:
                        raise PhotoError("The processed photo is too large.")
                    photos.append(dict(data=encoded, width=image.width, height=image.height,
                                       byte_count=len(encoded), mime_type="image/webp"))
        except (UnidentifiedImageError, OSError, ValueError,
                Image.DecompressionBombWarning, Image.DecompressionBombError) as error:
            if isinstance(error, PhotoError):
                raise
            raise PhotoError("One photo could not be read. Choose a valid JPEG, PNG, or WebP image.") from error
    return photos
