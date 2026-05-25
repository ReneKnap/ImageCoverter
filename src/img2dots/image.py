"""Load an image and scale it down to a manageable size.

First stage of the pipeline: open an image file, normalize it to RGB, and
proportionally downscale it so the longest edge fits within a limit. The result
feeds the pixel-to-LaTeX mapping in a later stage.
"""

from pathlib import Path

from PIL import Image

DEFAULT_MAX_EDGE = 64


def load_and_scale(
    path: str | Path,
    max_edge: int = DEFAULT_MAX_EDGE,
    resample: Image.Resampling = Image.Resampling.LANCZOS,
) -> Image.Image:
    """Load ``path`` as RGB and downscale it to fit within ``max_edge``.

    The aspect ratio is preserved and images already within the limit are left
    unchanged (no upscaling). ``resample`` selects the downscaling filter.
    """
    with Image.open(path) as opened:
        image = opened.convert("RGB")
    image.thumbnail((max_edge, max_edge), resample=resample)
    return image
