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

import warnings

from PIL import Image

from img2dots.latex import (
    DEFAULT_ALPHA_THRESHOLD,
    DEFAULT_DOT_SIZE,
    DEFAULT_RAISE,
    _pt,
    pixel_to_rule,
    stack_image,
)


# --- constants ---------------------------------------------------------------


def test_constants():
    assert DEFAULT_RAISE == 0.0
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
    assert pixel_to_rule((255, 0, 0)) == r"\textcolor[RGB]{255,0,0}{\rule[0pt]{1pt}{1pt}}"


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
    # 1x1, dot_size 1, raise 0: raise = 0 + 1/2 - 1 = -0.5pt (dot centered on baseline).
    assert stack_image(image) == "$" + pixel_to_rule((255, 0, 0), raise_pt="-0.5pt", size="1pt") + "$"


def test_stack_image_single_row_no_hspace():
    assert "\\hspace" not in stack_image(Image.new("RGB", (5, 1), (0, 0, 0)))


def test_stack_image_hspace_count_equals_rows_minus_one():
    assert stack_image(Image.new("RGB", (2, 4), (0, 0, 0))).count("\\hspace") == 3


def test_stack_image_default_hspace_width():
    assert "\\hspace{-3pt}" in stack_image(Image.new("RGB", (3, 2), (0, 0, 0)))


def test_stack_image_default_row_raises_decrease():
    # 1x3, dot_size 1, raise 0: raises 0.5 / -0.5 / -1.5 (step 1, centered on baseline).
    block = stack_image(Image.new("RGB", (1, 3), (0, 0, 0)))
    assert "\\rule[0.5pt]" in block
    assert "\\rule[-0.5pt]" in block
    assert "\\rule[-1.5pt]" in block


def test_stack_image_preserves_pixel_colors():
    image = Image.new("RGB", (2, 1))
    image.putpixel((0, 0), (255, 0, 0))
    image.putpixel((1, 0), (0, 255, 0))
    block = stack_image(image)
    assert block.index("\\textcolor[RGB]{255,0,0}") < block.index("\\textcolor[RGB]{0,255,0}")


def test_stack_image_empty_returns_empty():
    assert stack_image(Image.new("RGB", (0, 0))) == ""


def test_stack_image_emits_no_deprecation_warning():
    # Regression guard: stack_image must not use deprecated Pillow APIs.
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        stack_image(Image.new("RGBA", (2, 2), (1, 2, 3, 255)))


def test_stack_image_rule_count():
    assert stack_image(Image.new("RGB", (3, 2), (10, 20, 30))).count("\\rule") == 6


# --- stack_image: dot_size scaling -------------------------------------------


def test_stack_image_dot_size_in_rule():
    assert "{2pt}{2pt}" in stack_image(Image.new("RGB", (2, 2), (0, 0, 0)), dot_size=2)


def test_stack_image_hspace_scales_with_dot_size():
    assert "\\hspace{-6pt}" in stack_image(Image.new("RGB", (3, 2), (0, 0, 0)), dot_size=2)


def test_stack_image_raise_step_scales_with_dot_size():
    # 1x3, dot_size 2, raise 0: raises 1 / -1 / -3 (step 2, centered on baseline).
    block = stack_image(Image.new("RGB", (1, 3), (0, 0, 0)), dot_size=2)
    assert "\\rule[1pt]" in block
    assert "\\rule[-1pt]" in block
    assert "\\rule[-3pt]" in block


def test_stack_image_fractional_dot_size():
    # 1x2, dot_size 1.5, raise 0: raises 0 / -1.5 (step 1.5, centered on baseline).
    block = stack_image(Image.new("RGB", (1, 2), (0, 0, 0)), dot_size=1.5)
    assert "{1.5pt}{1.5pt}" in block
    assert "\\rule[0pt]" in block
    assert "\\rule[-1.5pt]" in block
    assert "\\hspace{-1.5pt}" in block


# --- stack_image: raise_offset -----------------------------------------------


def test_stack_image_default_raise_is_centered():
    # 1x2, dot_size 1, raise 0: raises 0 / -1. Image spans [-1, 1], centered on baseline.
    block = stack_image(Image.new("RGB", (1, 2), (0, 0, 0)))
    assert "\\rule[0pt]" in block
    assert "\\rule[-1pt]" in block


def test_stack_image_raise_offset_shifts_all_raises():
    # 1x3, dot_size 1, raise 5: every raise lifted by 5 -> 5.5 / 4.5 / 3.5.
    block = stack_image(Image.new("RGB", (1, 3), (0, 0, 0)), raise_offset=5)
    assert "\\rule[5.5pt]" in block
    assert "\\rule[4.5pt]" in block
    assert "\\rule[3.5pt]" in block


def test_stack_image_negative_raise_offset():
    # 1x1, dot_size 1, raise -3: raise = -3 + 0.5 - 1 = -3.5 (image lowered).
    block = stack_image(Image.new("RGB", (1, 1), (0, 0, 0)), raise_offset=-3)
    assert "\\rule[-3.5pt]" in block


def test_stack_image_raise_offset_defaults_to_zero():
    image = Image.new("RGB", (2, 3), (10, 20, 30))
    assert stack_image(image) == stack_image(image, raise_offset=0.0)


def test_stack_image_raise_offset_preserves_gapless_step():
    # raise only shifts the anchor; the per-row step stays one dot height (gapless).
    block = stack_image(Image.new("RGB", (1, 3), (0, 0, 0)), raise_offset=7)
    assert "\\rule[7.5pt]" in block
    assert "\\rule[6.5pt]" in block
    assert "\\rule[5.5pt]" in block


# --- stack_image: transparency (skip fully transparent pixels) ---------------


def test_stack_image_skips_fully_transparent_pixel():
    # 1x1 RGBA with alpha 0: no drawn dot, advance preserved with a same-size phantom.
    block = stack_image(Image.new("RGBA", (1, 1), (255, 0, 0, 0)))
    assert "\\textcolor" not in block
    assert "\\phantom{\\rule{1pt}{1pt}}" in block


def test_stack_image_transparent_pixel_replaced_by_phantom_keeps_visible():
    # 2x1: left pixel transparent, right pixel opaque -> one drawn dot, one phantom.
    image = Image.new("RGBA", (2, 1))
    image.putpixel((0, 0), (10, 20, 30, 0))
    image.putpixel((1, 0), (255, 0, 0, 255))
    block = stack_image(image)
    assert block.count("\\textcolor") == 1
    assert "\\phantom{\\rule{1pt}{1pt}}" in block
    assert "\\textcolor[RGB]{255,0,0}" in block


def test_stack_image_skip_phantom_scales_with_dot_size():
    # A skipped pixel reserves exactly one dot width.
    block = stack_image(Image.new("RGBA", (1, 1), (0, 0, 0, 0)), dot_size=2)
    assert "\\phantom{\\rule{2pt}{2pt}}" in block


def test_stack_image_opaque_rgba_draws_rule():
    # Fully opaque RGBA renders a drawn dot and adds no phantom.
    block = stack_image(Image.new("RGBA", (1, 1), (12, 34, 56, 255)))
    assert "\\textcolor[RGB]{12,34,56}" in block
    assert "\\phantom" not in block


def test_stack_image_default_threshold_skips_faint_pixels():
    # Default threshold is 50%: a barely-visible pixel is skipped, a near-opaque one drawn.
    image = Image.new("RGBA", (2, 1))
    image.putpixel((0, 0), (1, 2, 3, 1))
    image.putpixel((1, 0), (4, 5, 6, 254))
    block = stack_image(image)
    assert block.count("\\textcolor") == 1
    assert "\\textcolor[RGB]{4,5,6}" in block
    assert "\\phantom" in block


def test_stack_image_rgb_input_unaffected():
    # RGB input has no alpha -> every pixel drawn, no phantom (single row).
    block = stack_image(Image.new("RGB", (4, 1), (0, 0, 0)))
    assert block.count("\\textcolor") == 4
    assert "\\phantom" not in block


def test_stack_image_fully_transparent_row_preserves_reset():
    # A fully transparent row still resets the cursor for the next row (geometry intact).
    image = Image.new("RGBA", (3, 2), (0, 0, 0, 255))
    for x in range(3):
        image.putpixel((x, 0), (0, 0, 0, 0))
    block = stack_image(image)
    assert block.count("\\phantom{\\rule{1pt}{1pt}}") == 3  # three skipped pixels, top row
    assert "\\hspace{-3pt}" in block  # row reset still spans the full row width
    assert block.count("\\textcolor") == 3  # only the opaque bottom row draws dots


# --- stack_image: alpha threshold --------------------------------------------


def test_alpha_threshold_default_constant():
    assert DEFAULT_ALPHA_THRESHOLD == 127.5


def test_stack_image_default_threshold_boundary():
    # Default 50% of 255 = 127.5: alpha 127 is skipped, alpha 128 is drawn.
    image = Image.new("RGBA", (2, 1))
    image.putpixel((0, 0), (10, 20, 30, 127))
    image.putpixel((1, 0), (40, 50, 60, 128))
    block = stack_image(image)
    assert block.count("\\textcolor") == 1
    assert "\\textcolor[RGB]{40,50,60}" in block
    assert "\\phantom" in block


def test_stack_image_threshold_zero_draws_fully_transparent():
    # Threshold 0: a >= 0 is always true, so even a fully transparent pixel is drawn.
    block = stack_image(Image.new("RGBA", (1, 1), (10, 20, 30, 0)), alpha_threshold=0)
    assert "\\textcolor[RGB]{10,20,30}" in block
    assert "\\phantom" not in block


def test_stack_image_threshold_custom_cutoff():
    # Threshold 200: alpha 199 is skipped, alpha 200 is drawn.
    image = Image.new("RGBA", (2, 1))
    image.putpixel((0, 0), (10, 20, 30, 199))
    image.putpixel((1, 0), (40, 50, 60, 200))
    block = stack_image(image, alpha_threshold=200)
    assert block.count("\\textcolor") == 1
    assert "\\textcolor[RGB]{40,50,60}" in block
    assert "\\phantom" in block


def test_stack_image_threshold_255_draws_only_opaque():
    # Threshold 255: only fully opaque pixels are drawn.
    image = Image.new("RGBA", (2, 1))
    image.putpixel((0, 0), (10, 20, 30, 254))
    image.putpixel((1, 0), (40, 50, 60, 255))
    block = stack_image(image, alpha_threshold=255)
    assert block.count("\\textcolor") == 1
    assert "\\textcolor[RGB]{40,50,60}" in block
    assert "\\phantom" in block
