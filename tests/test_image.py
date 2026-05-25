"""Tests for the image loading and scaling stage (img2dots.image).

These pin the behavioral contract before the implementation exists:
- images are loaded and normalized to RGB mode,
- downscaling preserves aspect ratio and bounds the longest edge,
- images already within the limit are left untouched (no upscaling),
- the resampling filter is selectable, defaulting to LANCZOS.

Test images are generated in-memory with Pillow and written to ``tmp_path``;
no fixture files are needed.
"""

from PIL import Image

from img2dots.image import DEFAULT_MAX_EDGE, load_and_scale


def _write_image(tmp_path, size, mode="RGB", color=(255, 0, 0)):
    path = tmp_path / "input.png"
    Image.new(mode, size, color).save(path)
    return path


def test_landscape_downscaled_to_max_edge(tmp_path):
    path = _write_image(tmp_path, (200, 100))
    result = load_and_scale(path, max_edge=64)
    assert result.size == (64, 32)


def test_portrait_downscaled_to_max_edge(tmp_path):
    path = _write_image(tmp_path, (100, 200))
    result = load_and_scale(path, max_edge=64)
    assert result.size == (32, 64)


def test_small_image_not_upscaled(tmp_path):
    path = _write_image(tmp_path, (40, 30))
    result = load_and_scale(path, max_edge=64)
    assert result.size == (40, 30)


def test_result_mode_is_rgb_from_rgba(tmp_path):
    path = _write_image(tmp_path, (10, 10), mode="RGBA", color=(255, 0, 0, 128))
    result = load_and_scale(path)
    assert result.mode == "RGB"


def test_result_mode_is_rgb_from_palette(tmp_path):
    path = _write_image(tmp_path, (10, 10), mode="P", color=5)
    result = load_and_scale(path)
    assert result.mode == "RGB"


def test_nearest_resample_is_selectable(tmp_path):
    path = _write_image(tmp_path, (200, 100))
    result = load_and_scale(path, max_edge=64, resample=Image.Resampling.NEAREST)
    assert result.size == (64, 32)


def test_default_max_edge_is_64(tmp_path):
    assert DEFAULT_MAX_EDGE == 64
    path = _write_image(tmp_path, (128, 64))
    result = load_and_scale(path)
    assert result.size == (64, 32)
