"""Tests for the pixel-to-LaTeX mapping stage (img2dots.latex).

These pin the behavioral contract before the implementation exists:
- a single pixel maps to exactly ``\\textcolor[RGB]{r,g,b}{\\rule[10pt]{1pt}{1pt}}``
  with no stray whitespace,
- a whole image maps to a 2D grid of snippets, rows top-to-bottom and pixels
  left-to-right (natural reading order),
- each grid entry is consistent with ``pixel_to_rule`` for that pixel,
- the rule geometry constants hold their expected values.

Test images are generated in-memory with Pillow; no fixture files or disk I/O
are needed because the functions operate directly on the ``Image`` object.
"""

from PIL import Image

from img2dots.latex import (
    RULE_HEIGHT,
    RULE_RAISE,
    RULE_WIDTH,
    image_to_snippets,
    pixel_to_rule,
)


def test_pixel_to_rule_red():
    assert pixel_to_rule((255, 0, 0)) == r"\textcolor[RGB]{255,0,0}{\rule[10pt]{1pt}{1pt}}"


def test_pixel_to_rule_black():
    assert pixel_to_rule((0, 0, 0)) == r"\textcolor[RGB]{0,0,0}{\rule[10pt]{1pt}{1pt}}"


def test_pixel_to_rule_has_no_spaces():
    result = pixel_to_rule((12, 34, 56))
    assert result == r"\textcolor[RGB]{12,34,56}{\rule[10pt]{1pt}{1pt}}"
    assert " " not in result


def test_image_to_snippets_dimensions():
    image = Image.new("RGB", (2, 3), (0, 0, 0))
    grid = image_to_snippets(image)
    assert len(grid) == 3
    assert all(len(row) == 2 for row in grid)


def test_image_to_snippets_row_major_order():
    image = Image.new("RGB", (2, 2))
    image.putpixel((0, 0), (255, 0, 0))
    image.putpixel((1, 0), (0, 255, 0))
    image.putpixel((0, 1), (0, 0, 255))
    image.putpixel((1, 1), (255, 255, 255))

    grid = image_to_snippets(image)

    assert grid[0][0] == pixel_to_rule((255, 0, 0))
    assert grid[0][1] == pixel_to_rule((0, 255, 0))
    assert grid[1][0] == pixel_to_rule((0, 0, 255))
    assert grid[1][1] == pixel_to_rule((255, 255, 255))


def test_image_to_snippets_entries_match_pixel_to_rule():
    image = Image.new("RGB", (3, 2))
    for x in range(3):
        for y in range(2):
            image.putpixel((x, y), (x * 10, y * 20, 30))

    grid = image_to_snippets(image)

    for y in range(2):
        for x in range(3):
            assert grid[y][x] == pixel_to_rule((x * 10, y * 20, 30))


def test_rule_constants():
    assert RULE_RAISE == "10pt"
    assert RULE_WIDTH == "1pt"
    assert RULE_HEIGHT == "1pt"
