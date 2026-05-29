"""Command-line interface for img2dots.

Wires the full pipeline together: load and scale the input image, map every
pixel to a colored LaTeX ``\\rule`` snippet, assemble one inline-``$…$`` block
per image row, and write the rows to a Markdown file.
"""

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from img2dots import __version__
from img2dots.image import DEFAULT_MAX_EDGE, load_and_scale
from img2dots.latex import stack_image
from img2dots.output import write_markdown


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
        "--max-size",
        type=int,
        default=DEFAULT_MAX_EDGE,
        help=f"maximum edge length in pixels (default: {DEFAULT_MAX_EDGE})",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def convert(input_path: str | Path, output_path: str | Path, max_size: int) -> None:
    """Run the full image-to-Markdown pipeline and write the result.

    Loads and downscales the image at ``input_path`` to fit within ``max_size``,
    renders it as a single inline ``$…$`` block of stacked dot rows, and writes
    it to ``output_path``. Errors from any stage (missing or invalid image,
    unwritable output) propagate to the caller.
    """
    image = load_and_scale(input_path, max_edge=max_size)
    write_markdown([stack_image(image)], output_path)


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.max_size <= 0:
        print(
            f"img2dots: --max-size must be a positive size, got {args.max_size}.",
            file=sys.stderr,
        )
        return 1

    try:
        convert(args.input, args.output, args.max_size)
    except OSError as error:
        print(f"img2dots: {error}", file=sys.stderr)
        return 1

    print(f"img2dots: wrote {args.output}")
    return 0
