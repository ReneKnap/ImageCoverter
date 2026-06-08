"""Generate the example image shipped in examples/.

Produces a rounded square with a diagonal color gradient on a transparent
background -- a license-clean, reproducible example for the README. The
transparent margin and rounded corners exercise img2dots' alpha handling
(those pixels are skipped in the output).

Run from the repository root:

    python examples/make_example.py
"""

from PIL import Image, ImageDraw

CANVAS = 512
MARGIN = 76  # transparent border around the square
RADIUS = 64  # corner radius of the rounded square
START_COLOR = (37, 99, 235)  # blue
END_COLOR = (249, 115, 22)  # orange
OUTPUT = "examples/square.png"


def build_gradient(size: tuple[int, int], start: tuple[int, int, int], end: tuple[int, int, int]) -> Image.Image:
    """Build a diagonal (top-left to bottom-right) RGB gradient of ``size``."""
    width, height = size
    gradient = Image.new("RGB", size)
    pixels = gradient.load()
    span = (width - 1) + (height - 1)
    for y in range(height):
        for x in range(width):
            ratio = (x + y) / span
            pixels[x, y] = tuple(
                round(start[channel] + (end[channel] - start[channel]) * ratio)
                for channel in range(3)
            )
    return gradient


def make_example() -> None:
    """Render the rounded gradient square and write it to ``OUTPUT``."""
    image = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    box = (MARGIN, MARGIN, CANVAS - MARGIN - 1, CANVAS - MARGIN - 1)

    mask = Image.new("L", (CANVAS, CANVAS), 0)
    ImageDraw.Draw(mask).rounded_rectangle(box, radius=RADIUS, fill=255)

    gradient = build_gradient((CANVAS, CANVAS), START_COLOR, END_COLOR).convert("RGBA")
    image.paste(gradient, (0, 0), mask)
    image.save(OUTPUT)


if __name__ == "__main__":
    make_example()
