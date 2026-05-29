"""Build colored LaTeX from image pixels and stack them into one math block.

Two responsibilities:

- :func:`pixel_to_rule` translates a single ``(r, g, b)`` pixel into a colored
  ``\\textcolor[RGB]{r,g,b}{\\rule[<raise>]{<size>}{<size>}}`` snippet. The
  vertical ``raise`` and the (square) dot ``size`` are both selectable.
- :func:`stack_image` renders a whole RGB image as a single inline-LaTeX ``$…$``
  block. Each image row is drawn one dot-size lower than the previous one, and
  rows are separated by a negative ``\\hspace`` that returns the cursor to the
  left edge — so the dots stack directly on top of one another with no vertical
  gap. The rule size, the ``\\hspace`` width and the per-row raise step all scale
  with ``dot_size``, keeping the grid gap-free at any size. This format is
  recorded in ADR-0003 and targets MathJax.
"""

from PIL import Image

RULE_RAISE_PT = 10
DEFAULT_DOT_SIZE = 1.0


def pixel_to_rule(
    rgb: tuple[int, int, int],
    raise_pt: str = f"{RULE_RAISE_PT}pt",
    size: str = f"{DEFAULT_DOT_SIZE:g}pt",
) -> str:
    """Return the colored LaTeX ``\\rule`` snippet for one ``(r, g, b)`` pixel.

    ``raise_pt`` is the rule's vertical offset above the baseline and ``size`` is
    its (square) edge length — both LaTeX dimensions such as ``"10pt"`` or
    ``"1.5pt"``.
    """
    r, g, b = rgb
    return f"\\textcolor[RGB]{{{r},{g},{b}}}{{\\rule[{raise_pt}]{{{size}}}{{{size}}}}}"


def stack_image(image: Image.Image, dot_size: float = DEFAULT_DOT_SIZE) -> str:
    """Render ``image`` as one inline-LaTeX ``$…$`` block of stacked dot rows.

    Each dot is a ``dot_size``-pt square. Each row is drawn one dot-size lower
    than the row above it, and rows are separated by a negative ``\\hspace`` of
    the row's width, so the dots form a contiguous grid with no vertical gap. An
    image with no pixels yields an empty string.
    """
    width, height = image.width, image.height
    if width == 0 or height == 0:
        return ""

    pixels = list(image.getdata())
    size = _pt(dot_size)
    hspace = f"\\hspace{{-{_pt(width * dot_size)}}}"
    rows = []
    for row in range(height):
        raise_pt = _pt(RULE_RAISE_PT - row * dot_size)
        cells = pixels[row * width:(row + 1) * width]
        rows.append("".join(pixel_to_rule(pixel, raise_pt, size) for pixel in cells))
    return f"${hspace.join(rows)}$"


def _pt(value: float) -> str:
    """Format ``value`` as a LaTeX pt dimension, dropping a trailing ``.0``."""
    return f"{value:g}pt"
