"""Tests for the pixel-to-LaTeX mapping and stacking stage (img2dots.latex).

Pin the behavioral contract:
- a single pixel maps to ``\\textcolor[RGB]{r,g,b}{\\rule[<raise>]{1pt}{1pt}}``,
  with a default raise of 10pt and a selectable per-call raise,
- ``stack_image`` renders a whole image as one inline ``$…$`` block: each row is
  drawn one dot-height lower than the previous, rows separated by a negative
  ``\\hspace`` that resets to the left edge, with no trailing ``\\hspace``,
- the rule geometry constants (string and numeric) hold their expected values.

Test images are generated in-memory with Pillow; no fixture files or disk I/O
are needed because the functions operate directly on the ``Image`` object.
"""

from PIL import Image

from img2dots.latex import (
    RULE_HEIGHT,
    RULE_HEIGHT_PT,
    RULE_RAISE,
    RULE_RAISE_PT,
    RULE_WIDTH,
    RULE_WIDTH_PT,
    pixel_to_rule,
    stack_image,
)


# --- constants ---------------------------------------------------------------


def test_rule_string_constants():
    assert RULE_RAISE == "10pt"
    assert RULE_WIDTH == "1pt"
    assert RULE_HEIGHT == "1pt"


def test_rule_numeric_constants():
    assert RULE_RAISE_PT == 10
    assert RULE_WIDTH_PT == 1
    assert RULE_HEIGHT_PT == 1


# --- pixel_to_rule -----------------------------------------------------------


def test_pixel_to_rule_default_raise():
    assert pixel_to_rule((255, 0, 0)) == r"\textcolor[RGB]{255,0,0}{\rule[10pt]{1pt}{1pt}}"


def test_pixel_to_rule_custom_raise():
    assert pixel_to_rule((0, 0, 0), raise_pt="3pt") == r"\textcolor[RGB]{0,0,0}{\rule[3pt]{1pt}{1pt}}"


def test_pixel_to_rule_negative_raise():
    assert r"\rule[-5pt]" in pixel_to_rule((1, 2, 3), raise_pt="-5pt")


def test_pixel_to_rule_has_no_spaces():
    result = pixel_to_rule((12, 34, 56))
    assert " " not in result


# --- stack_image -------------------------------------------------------------


def test_stack_image_wraps_in_dollar():
    block = stack_image(Image.new("RGB", (2, 2), (0, 0, 0)))
    assert block.startswith("$")
    assert block.endswith("$")


def test_stack_image_single_pixel():
    image = Image.new("RGB", (1, 1), (255, 0, 0))
    assert stack_image(image) == "$" + pixel_to_rule((255, 0, 0), raise_pt="10pt") + "$"


def test_stack_image_single_row_no_hspace():
    block = stack_image(Image.new("RGB", (5, 1), (0, 0, 0)))
    assert "\\hspace" not in block


def test_stack_image_hspace_count_equals_rows_minus_one():
    block = stack_image(Image.new("RGB", (2, 4), (0, 0, 0)))
    assert block.count("\\hspace") == 3


def test_stack_image_hspace_width_from_image_width():
    block = stack_image(Image.new("RGB", (3, 2), (0, 0, 0)))
    assert "\\hspace{-3pt}" in block


def test_stack_image_row_raises_decrease():
    block = stack_image(Image.new("RGB", (1, 3), (0, 0, 0)))
    assert "\\rule[10pt]" in block
    assert "\\rule[9pt]" in block
    assert "\\rule[8pt]" in block


def test_stack_image_preserves_pixel_colors():
    image = Image.new("RGB", (2, 1))
    image.putpixel((0, 0), (255, 0, 0))
    image.putpixel((1, 0), (0, 255, 0))
    block = stack_image(image)
    assert block.index("\\textcolor[RGB]{255,0,0}") < block.index("\\textcolor[RGB]{0,255,0}")


def test_stack_image_empty_returns_empty():
    assert stack_image(Image.new("RGB", (0, 0))) == ""


def test_stack_image_rule_count():
    block = stack_image(Image.new("RGB", (3, 2), (10, 20, 30)))
    assert block.count("\\rule") == 6
