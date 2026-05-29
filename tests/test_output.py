"""Tests for the Markdown file-writing stage (img2dots.output).

These pin the behavioral contract before the implementation exists:
- rows are joined by a blank line (one Markdown paragraph per image row),
- the file ends with a trailing newline when there is content,
- an empty line list yields a truly empty (0-byte) file,
- writing overwrites any existing file,
- both ``str`` and ``Path`` targets are accepted,
- content is written as UTF-8.

Output is written to ``tmp_path`` and read back; no fixture files are needed.
"""

from img2dots.output import write_markdown


def test_happy_path_joins_with_blank_line(tmp_path):
    path = tmp_path / "out.md"
    write_markdown(["$a$", "$b$"], path)
    assert path.read_text(encoding="utf-8") == "$a$\n\n$b$\n"


def test_rows_do_not_merge(tmp_path):
    path = tmp_path / "out.md"
    write_markdown(["$a$", "$b$"], path)
    content = path.read_text(encoding="utf-8")
    assert "$a$$b$" not in content
    assert "$a$\n\n$b$" in content


def test_single_line(tmp_path):
    path = tmp_path / "out.md"
    write_markdown(["$x$"], path)
    assert path.read_text(encoding="utf-8") == "$x$\n"


def test_empty_list_yields_empty_file(tmp_path):
    path = tmp_path / "out.md"
    write_markdown([], path)
    assert path.read_bytes() == b""


def test_overwrites_existing_file(tmp_path):
    path = tmp_path / "out.md"
    path.write_text("stale content\n", encoding="utf-8")
    write_markdown(["$new$"], path)
    assert path.read_text(encoding="utf-8") == "$new$\n"


def test_accepts_str_path(tmp_path):
    path = tmp_path / "out.md"
    write_markdown(["$a$"], str(path))
    assert path.read_text(encoding="utf-8") == "$a$\n"


def test_writes_utf8(tmp_path):
    path = tmp_path / "out.md"
    write_markdown(["$\\text{Grüße}$"], path)
    assert path.read_text(encoding="utf-8") == "$\\text{Grüße}$\n"
