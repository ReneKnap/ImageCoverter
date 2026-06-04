"""Load an image and scale it down to a manageable size.

First stage of the pipeline: open an image file, normalize it to RGBA, and
proportionally downscale it so the longest edge fits within a limit. The alpha
channel is kept so the later pixel-to-LaTeX stage can skip fully transparent
pixels; images without transparency gain a fully opaque alpha channel.
"""

from pathlib import Path

from PIL import Image

DEFAULT_MAX_EDGE = 64


def load_and_scale(
    path: str | Path,
    max_edge: int = DEFAULT_MAX_EDGE,
    resample: Image.Resampling = Image.Resampling.LANCZOS,
) -> Image.Image:
    """Load ``path`` as RGBA and downscale it to fit within ``max_edge``.

    The aspect ratio is preserved and images already within the limit are left
    unchanged (no upscaling). ``resample`` selects the downscaling filter. The
    alpha channel is preserved; images without transparency get a fully opaque
    one.
    """
    with Image.open(path) as opened:
        image = opened.convert("RGBA")
    image.thumbnail((max_edge, max_edge), resample=resample)
    return image
