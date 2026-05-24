"""Smoke tests for the img2dots CLI scaffold.

These pin the CLI contract before the implementation exists:
- ``cli.main(argv) -> int`` returns an exit code,
- ``--help`` exits 0 (argparse default),
- a valid invocation prints a placeholder message and returns 0 (scaffold only),
- a missing required argument errors out.
"""

import pytest

import img2dots
from img2dots import cli


def test_version_is_nonempty_string():
    assert isinstance(img2dots.__version__, str)
    assert img2dots.__version__


def test_help_exits_zero():
    with pytest.raises(SystemExit) as exc:
        cli.main(["--help"])
    assert exc.value.code == 0


def test_placeholder_returns_zero():
    assert cli.main(["x.png", "-o", "out.md"]) == 0


def test_placeholder_message(capsys):
    cli.main(["x.png", "-o", "out.md"])
    output = "".join(capsys.readouterr()).lower()
    assert "not implemented" in output


def test_missing_input_errors():
    with pytest.raises(SystemExit) as exc:
        cli.main([])
    assert exc.value.code != 0
