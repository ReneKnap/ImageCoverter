"""Tests for the img2dots CLI (img2dots.cli).

Pin the behavioral contract of the wired-up CLI:
- ``cli.main(argv) -> int`` returns an exit code,
- ``--help`` exits 0 and a missing input errors (argparse defaults),
- a valid invocation runs the full pipeline, writes Markdown, returns 0,
- ``--max-size`` bounds the dot grid and defaults to 64,
- ``convert`` orchestrates the pipeline and lets errors propagate,
- expected failures (missing/invalid input, bad output path, non-positive
  ``--max-size``) print to stderr and return 1 without a traceback.

Test images are generated in-memory with Pillow and written to ``tmp_path``;
no fixture files are needed.
"""

import pytest
from PIL import Image

import img2dots
from img2dots import cli
from img2dots.cli import convert, main


def _write_image(tmp_path, size=(10, 10), mode="RGB", color=(255, 0, 0)):
    path = tmp_path / "input.png"
    Image.new(mode, size, color).save(path)
    return path


def _row_count(text):
    """Number of image rows in the stacked single-block output.

    Rows are separated by a negative ``\\hspace``; H rows yield H-1 of them.
    """
    return text.count("\\hspace") + 1


# --- argparse-level contract -------------------------------------------------


def test_version_is_nonempty_string():
    assert isinstance(img2dots.__version__, str)
    assert img2dots.__version__


def test_help_exits_zero():
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0


def test_missing_input_errors():
    with pytest.raises(SystemExit) as exc:
        main([])
    assert exc.value.code != 0


# --- happy path --------------------------------------------------------------


def test_converts_and_returns_zero(tmp_path):
    image = _write_image(tmp_path, (4, 3))
    out = tmp_path / "out.md"
    assert main([str(image), "-o", str(out)]) == 0
    content = out.read_text(encoding="utf-8")
    assert "$" in content
    assert "\\rule" in content
    assert "\\textcolor" in content


def test_success_message_reports_output_path(tmp_path, capsys):
    image = _write_image(tmp_path, (4, 3))
    out = tmp_path / "out.md"
    main([str(image), "-o", str(out)])
    assert str(out) in capsys.readouterr().out


# --- convert() pipeline integration -----------------------------------------


def test_convert_stacks_rows_in_one_block(tmp_path):
    image = _write_image(tmp_path, (1, 2))  # width 1, height 2 -> two rows
    out = tmp_path / "out.md"
    convert(image, out, max_size=64)
    content = out.read_text(encoding="utf-8")
    assert "\n\n" not in content  # a single block, not paragraph-per-row
    assert _row_count(content) == 2


def test_convert_raises_on_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        convert(tmp_path / "nope.png", tmp_path / "out.md", max_size=64)


# --- --max-size --------------------------------------------------------------


def test_max_size_limits_row_count(tmp_path):
    image = _write_image(tmp_path, (100, 100))
    out = tmp_path / "out.md"
    main([str(image), "-o", str(out), "--max-size", "8"])
    assert _row_count(out.read_text(encoding="utf-8")) == 8


def test_default_max_size_is_64(tmp_path):
    image = _write_image(tmp_path, (128, 128))
    out = tmp_path / "out.md"
    main([str(image), "-o", str(out)])
    assert _row_count(out.read_text(encoding="utf-8")) == 64


# --- --dot-size --------------------------------------------------------------


def test_dot_size_enlarges_dots(tmp_path):
    image = _write_image(tmp_path, (4, 3))
    out = tmp_path / "out.md"
    assert main([str(image), "-o", str(out), "--dot-size", "2"]) == 0
    assert "{2pt}{2pt}" in out.read_text(encoding="utf-8")


def test_convert_accepts_dot_size(tmp_path):
    image = _write_image(tmp_path, (4, 3))
    out = tmp_path / "out.md"
    convert(image, out, max_size=64, dot_size=2)
    assert "{2pt}{2pt}" in out.read_text(encoding="utf-8")


# --- --raise -----------------------------------------------------------------


def test_raise_option_shifts_image(tmp_path):
    # 1x1 image, dot_size 1, raise 5: raise = 5 + 0.5 - 1 = 4.5pt.
    image = _write_image(tmp_path, (1, 1))
    out = tmp_path / "out.md"
    assert main([str(image), "-o", str(out), "--raise", "5"]) == 0
    assert "\\rule[4.5pt]" in out.read_text(encoding="utf-8")


def test_raise_defaults_to_zero(tmp_path):
    image = _write_image(tmp_path, (3, 2))
    default_out = tmp_path / "default.md"
    explicit_out = tmp_path / "explicit.md"
    main([str(image), "-o", str(default_out)])
    main([str(image), "-o", str(explicit_out), "--raise", "0"])
    assert default_out.read_text(encoding="utf-8") == explicit_out.read_text(encoding="utf-8")


def test_convert_accepts_raise_offset(tmp_path):
    image = _write_image(tmp_path, (1, 1))
    out = tmp_path / "out.md"
    convert(image, out, max_size=64, raise_offset=5)
    assert "\\rule[4.5pt]" in out.read_text(encoding="utf-8")


def test_negative_raise_returns_zero(tmp_path):
    # 1x1, dot_size 1, raise -3: raise = -3 + 0.5 - 1 = -3.5pt; negative is valid.
    image = _write_image(tmp_path, (1, 1))
    out = tmp_path / "out.md"
    assert main([str(image), "-o", str(out), "--raise", "-3"]) == 0
    assert "\\rule[-3.5pt]" in out.read_text(encoding="utf-8")


def test_raise_zero_is_valid(tmp_path):
    image = _write_image(tmp_path, (4, 3))
    out = tmp_path / "out.md"
    assert main([str(image), "-o", str(out), "--raise", "0"]) == 0


# --- error paths -------------------------------------------------------------


def test_missing_input_file_returns_1(tmp_path, capsys):
    out = tmp_path / "out.md"
    assert main([str(tmp_path / "nope.png"), "-o", str(out)]) == 1
    assert capsys.readouterr().err.strip()


def test_invalid_image_returns_1(tmp_path, capsys):
    bogus = tmp_path / "input.png"
    bogus.write_text("not an image", encoding="utf-8")
    out = tmp_path / "out.md"
    assert main([str(bogus), "-o", str(out)]) == 1
    assert capsys.readouterr().err.strip()


def test_max_size_zero_returns_1(tmp_path, capsys):
    image = _write_image(tmp_path, (4, 3))
    out = tmp_path / "out.md"
    assert main([str(image), "-o", str(out), "--max-size", "0"]) == 1
    assert "size" in capsys.readouterr().err.lower()


def test_dot_size_zero_returns_1(tmp_path, capsys):
    image = _write_image(tmp_path, (4, 3))
    out = tmp_path / "out.md"
    assert main([str(image), "-o", str(out), "--dot-size", "0"]) == 1
    assert "size" in capsys.readouterr().err.lower()


def test_missing_output_dir_returns_1(tmp_path, capsys):
    image = _write_image(tmp_path, (4, 3))
    out = tmp_path / "missing" / "out.md"
    assert main([str(image), "-o", str(out)]) == 1
    assert capsys.readouterr().err.strip()
