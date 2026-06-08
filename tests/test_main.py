"""Tests for the ``python -m img2dots`` entry point (img2dots.__main__).

These exercise the module entry point as a real subprocess, so the
``if __name__ == "__main__": sys.exit(main())`` wiring is actually run and its
exit code observed — something an in-process import cannot cover.

The subprocess gets ``PYTHONPATH`` pointed at the repo's ``src/`` directory
(src-layout) so ``python -m img2dots`` resolves without an editable install.
Test images are generated in-memory with Pillow and written to ``tmp_path``.
"""

import os
import subprocess
import sys
from pathlib import Path

from PIL import Image

_REPO_ROOT = Path(__file__).resolve().parents[1]
_SRC = _REPO_ROOT / "src"


def _run_module(*args):
    """Run ``python -m img2dots <args>`` with src on PYTHONPATH; return the result."""
    env = {**os.environ, "PYTHONPATH": str(_SRC)}
    return subprocess.run(
        [sys.executable, "-m", "img2dots", *args],
        capture_output=True,
        text=True,
        env=env,
    )


def _write_image(tmp_path, size=(4, 3), color=(255, 0, 0)):
    path = tmp_path / "input.png"
    Image.new("RGB", size, color).save(path)
    return path


def test_module_invocation_succeeds(tmp_path):
    image = _write_image(tmp_path)
    out = tmp_path / "out.md"
    result = _run_module(str(image), "-o", str(out))
    assert result.returncode == 0
    assert out.is_file()
    assert out.stat().st_size > 0


def test_module_invocation_missing_input_fails(tmp_path):
    out = tmp_path / "out.md"
    result = _run_module(str(tmp_path / "nope.png"), "-o", str(out))
    assert result.returncode == 1
    assert result.stderr.strip()
