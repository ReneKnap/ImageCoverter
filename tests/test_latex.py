"""Tests for the pixel-to-LaTeX mapping and stacking stage (img2dots.latex).

Pin the behavioral contract:
- ``_pt`` formats a float as a LaTeX pt dimension, dropping a trailing ``.0``,
- ``pixel_to_rule`` maps a pixel to a colored ``\\rule`` with a selectable raise
  and dot size,
- ``stack_image`` renders an image as one inline ``$…$`` block whose geometry
  (rule size, ``\\hspace`` reset width, per-row raise step) all scale with
  ``dot_size`` so the dots stay gap-free,
- the geometry constants hold their expected values.

Test images are generated in-memory with Pillow; no fixture files or disk I/O
are needed.
"""

from PIL import Image

from img2dots.latex import (
    DEFAULT_DOT_SIZE,
    RULE_RAISE_PT,
    _pt,
    pixel_to_rule,
    stack_image,
)


# --- constants ---------------------------------------------------------------


def test_constants():
    assert RULE_RAISE_PT == 10
    assert DEFAULT_DOT_SIZE == 1.0


# --- _pt formatter -----------------------------------------------------------


def test_pt_strips_trailing_zero():
    assert _pt(1.0) == "1pt"
    assert _pt(2.0) == "2pt"


def test_pt_keeps_fraction():
    assert _pt(1.5) == "1.5pt"


def test_pt_negative():
    assert _pt(-5.0) == "-5pt"


# --- pixel_to_rule -----------------------------------------------------------


def test_pixel_to_rule_default():
    assert pixel_to_rule((255, 0, 0)) == r"\textcolor[RGB]{255,0,0}{\rule[10pt]{1pt}{1pt}}"


def test_pixel_to_rule_custom_raise():
    assert pixel_to_rule((0, 0, 0), raise_pt="3pt") == r"\textcolor[RGB]{0,0,0}{\rule[3pt]{1pt}{1pt}}"


def test_pixel_to_rule_custom_size():
    assert pixel_to_rule((0, 0, 0), raise_pt="10pt", size="2pt") == (
        r"\textcolor[RGB]{0,0,0}{\rule[10pt]{2pt}{2pt}}"
    )


def test_pixel_to_rule_negative_raise():
    assert r"\rule[-5pt]" in pixel_to_rule((1, 2, 3), raise_pt="-5pt")


def test_pixel_to_rule_has_no_spaces():
    assert " " not in pixel_to_rule((12, 34, 56))


# --- stack_image: default geometry (byte-identical to the 1pt baseline) ------


def test_stack_image_wraps_in_dollar():
    block = stack_image(Image.new("RGB", (2, 2), (0, 0, 0)))
    assert block.startswith("$")
    assert block.endswith("$")


def test_stack_image_single_pixel():
    image = Image.new("RGB", (1, 1), (255, 0, 0))
    assert stack_image(image) == "$" + pixel_to_rule((255, 0, 0), raise_pt="10pt", size="1pt") + "$"


def test_stack_image_single_row_no_hspace():
    assert "\\hspace" not in stack_image(Image.new("RGB", (5, 1), (0, 0, 0)))


def test_stack_image_hspace_count_equals_rows_minus_one():
    assert stack_image(Image.new("RGB", (2, 4), (0, 0, 0))).count("\\hspace") == 3


def test_stack_image_default_hspace_width():
    assert "\\hspace{-3pt}" in stack_image(Image.new("RGB", (3, 2), (0, 0, 0)))


def test_stack_image_default_row_raises_decrease():
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
    assert stack_image(Image.new("RGB", (3, 2), (10, 20, 30))).count("\\rule") == 6


# --- stack_image: dot_size scaling -------------------------------------------


def test_stack_image_dot_size_in_rule():
    assert "{2pt}{2pt}" in stack_image(Image.new("RGB", (2, 2), (0, 0, 0)), dot_size=2)


def test_stack_image_hspace_scales_with_dot_size():
    assert "\\hspace{-6pt}" in stack_image(Image.new("RGB", (3, 2), (0, 0, 0)), dot_size=2)


def test_stack_image_raise_step_scales_with_dot_size():
    block = stack_image(Image.new("RGB", (1, 3), (0, 0, 0)), dot_size=2)
    assert "\\rule[10pt]" in block
    assert "\\rule[8pt]" in block
    assert "\\rule[6pt]" in block


def test_stack_image_fractional_dot_size():
    block = stack_image(Image.new("RGB", (1, 2), (0, 0, 0)), dot_size=1.5)
    assert "{1.5pt}{1.5pt}" in block
    assert "\\rule[10pt]" in block
    assert "\\rule[8.5pt]" in block
    assert "\\hspace{-1.5pt}" in block
