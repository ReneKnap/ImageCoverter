"""Build colored LaTeX from image pixels and stack them into one math block.

Two responsibilities:

- :func:`pixel_to_rule` translates a single ``(r, g, b)`` pixel into a colored
  ``\\textcolor[RGB]{r,g,b}{\\rule[<raise>]{...}{...}}`` snippet. The vertical
  ``raise`` is selectable so a caller can place the dot at any height.
- :func:`stack_image` renders a whole RGB image as a single inline-LaTeX ``$…$``
  block. Each image row is drawn one dot-height lower than the previous one, and
  rows are separated by a negative ``\\hspace`` that returns the cursor to the
  left edge — so the dots stack directly on top of one another with no vertical
  gap. This output format is recorded in ADR-0003 and targets MathJax.
"""

from PIL import Image

RULE_RAISE_PT = 10
RULE_WIDTH_PT = 1
RULE_HEIGHT_PT = 1

RULE_RAISE = f"{RULE_RAISE_PT}pt"
RULE_WIDTH = f"{RULE_WIDTH_PT}pt"
RULE_HEIGHT = f"{RULE_HEIGHT_PT}pt"


def pixel_to_rule(rgb: tuple[int, int, int], raise_pt: str = RULE_RAISE) -> str:
    """Return the colored LaTeX ``\\rule`` snippet for one ``(r, g, b)`` pixel.

    ``raise_pt`` is the rule's vertical offset above the baseline (a LaTeX
    dimension such as ``"10pt"`` or ``"-5pt"``); it defaults to ``RULE_RAISE``.
    """
    r, g, b = rgb
    return f"\\textcolor[RGB]{{{r},{g},{b}}}{{\\rule[{raise_pt}]{{{RULE_WIDTH}}}{{{RULE_HEIGHT}}}}}"


def stack_image(image: Image.Image) -> str:
    """Render ``image`` as one inline-LaTeX ``$…$`` block of stacked dot rows.

    Each row is drawn one dot-height lower than the row above it, and rows are
    separated by a negative ``\\hspace`` that resets to the left edge, so the
    pixels form a contiguous grid with no vertical gap. An image with no pixels
    yields an empty string.
    """
    width, height = image.width, image.height
    if width == 0 or height == 0:
        return ""

    pixels = list(image.getdata())
    hspace = f"\\hspace{{-{width * RULE_WIDTH_PT}pt}}"
    rows = []
    for row in range(height):
        raise_pt = f"{RULE_RAISE_PT - row * RULE_HEIGHT_PT}pt"
        cells = pixels[row * width:(row + 1) * width]
        rows.append("".join(pixel_to_rule(pixel, raise_pt) for pixel in cells))
    return f"${hspace.join(rows)}$"
