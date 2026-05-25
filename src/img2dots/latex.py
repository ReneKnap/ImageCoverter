"""Map image pixels to colored LaTeX ``\\rule`` snippets.

Second stage of the pipeline: take the RGB image produced by
:func:`img2dots.image.load_and_scale` and translate every pixel into a
``\\textcolor[RGB]{r,g,b}{\\rule[...]{...}{...}}`` snippet. The snippets are
returned as a 2D grid (rows top-to-bottom, pixels left-to-right) that the next
stage assembles into ``$ … $`` line blocks.
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
