"""Build colored LaTeX from image pixels.

Covers two pipeline stages:

- :func:`image_to_snippets` takes the RGB image produced by
  :func:`img2dots.image.load_and_scale` and translates every pixel into a
  ``\\textcolor[RGB]{r,g,b}{\\rule[...]{...}{...}}`` snippet, returned as a 2D
  grid (rows top-to-bottom, pixels left-to-right).
- :func:`assemble_rows` joins each grid row into a single inline-LaTeX
  ``$…$`` block — one block per image row — ready for the file-writing stage to
  emit as Markdown lines.
"""

from PIL import Image

RULE_RAISE = "10pt"
RULE_WIDTH = "1pt"
RULE_HEIGHT = "1pt"

_RULE = f"\\rule[{RULE_RAISE}]{{{RULE_WIDTH}}}{{{RULE_HEIGHT}}}"


def pixel_to_rule(rgb: tuple[int, int, int]) -> str:
    """Return the colored LaTeX ``\\rule`` snippet for a single ``(r, g, b)`` pixel."""
    r, g, b = rgb
    return f"\\textcolor[RGB]{{{r},{g},{b}}}{{{_RULE}}}"


def image_to_snippets(image: Image.Image) -> list[list[str]]:
    """Map an RGB image to a 2D grid of ``\\rule`` snippets.

    The outer list holds image rows (top to bottom), each inner list holds the
    pixels of that row (left to right), matching natural reading order.
    """
    width = image.width
    flat = [pixel_to_rule(pixel) for pixel in image.getdata()]
    return [flat[row * width:(row + 1) * width] for row in range(image.height)]


def assemble_rows(grid: list[list[str]]) -> list[str]:
    """Join each row of snippets into a single inline-LaTeX ``$…$`` block.

    The outer list order is preserved (image top to bottom), so every returned
    string is one image row, ready to become one Markdown line downstream.
    Snippets are concatenated directly (no separator) and wrapped without inner
    padding. An empty row yields ``"$$"``; an empty grid yields ``[]``.
    """
    return [f"${''.join(row)}$" for row in grid]
