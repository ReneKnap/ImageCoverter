"""Command-line interface for img2dots.

Scaffold entry point: it parses arguments and reports that the conversion is
not implemented yet. The actual image-to-LaTeX pipeline lands in later work
items.
"""

import argparse
from collections.abc import Sequence

from img2dots import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="img2dots",
        description="Convert an image into Markdown-embedded LaTeX \\rule dots.",
    )
    parser.add_argument("input", help="path to the input image")
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="path to the Markdown output file",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    print(
        f"img2dots: conversion not implemented yet "
        f"(input={args.input!r}, output={args.output!r})."
    )
    return 0
