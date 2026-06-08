"""Tests for the shipped example asset (``examples/``).

Guard the committed example against silent drift:
- the ``examples/`` directory ships exactly one input image plus its rendered
  ``.md`` output, both non-empty,
- re-running the pipeline on that image with default options reproduces the
  committed ``.md`` byte-for-byte (so a pipeline change can never leave a stale
  example in the repo unnoticed).

The example must be generated with default options
(``img2dots examples/<image> -o examples/<image>.md``) for the reproduction
check to hold.
"""

from pathlib import Path

from img2dots.cli import convert
from img2dots.image import DEFAULT_MAX_EDGE

_REPO_ROOT = Path(__file__).resolve().parents[1]
_EXAMPLES_DIR = _REPO_ROOT / "examples"
_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}


def _example_images():
    """All input image files shipped in ``examples/`` (empty if none/missing)."""
    if not _EXAMPLES_DIR.is_dir():
        return []
    return sorted(
        path
        for path in _EXAMPLES_DIR.iterdir()
        if path.is_file() and path.suffix.lower() in _IMAGE_SUFFIXES
    )


def test_example_assets_exist():
    images = _example_images()
    assert len(images) == 1, f"expected exactly one example image, found {len(images)}"
    image = images[0]
    assert image.stat().st_size > 0  # input image is not empty

    rendered = image.with_suffix(".md")
    assert rendered.is_file(), f"missing rendered output {rendered.name}"
    assert rendered.stat().st_size > 0  # rendered output is not empty


def test_example_output_is_reproducible(tmp_path):
    images = _example_images()
    assert images, "no example image to verify"
    image = images[0]
    expected = image.with_suffix(".md")
    assert expected.is_file(), f"missing rendered output {expected.name}"

    regenerated = tmp_path / "regenerated.md"
    convert(image, regenerated, max_size=DEFAULT_MAX_EDGE)

    assert regenerated.read_text(encoding="utf-8") == expected.read_text(encoding="utf-8")
