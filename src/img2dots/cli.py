"""Command-line interface for img2dots.

Wires the full pipeline together: load and scale the input image, map every
pixel to a colored LaTeX ``\\rule`` snippet, assemble one inline-``$…$`` block
per image row, and write the rows to a Markdown file.
"""

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from PIL import UnidentifiedImageError

from img2dots import __version__
from img2dots.image import DEFAULT_MAX_EDGE, load_and_scale
from img2dots.latex import (
    DEFAULT_ALPHA_THRESHOLD,
    DEFAULT_DOT_SIZE,
    DEFAULT_RAISE,
    stack_image,
)
from img2dots.output import write_markdown

# CLI exposes the alpha threshold in percent; latex works in raw 0-255 values.
DEFAULT_ALPHA_THRESHOLD_PERCENT = DEFAULT_ALPHA_THRESHOLD / 255 * 100


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
        "--dot-size",
        type=float,
        default=DEFAULT_DOT_SIZE,
        help=f"dot edge length in pt (default: {DEFAULT_DOT_SIZE:g})",
    )
    parser.add_argument(
        "--raise",
        dest="raise_offset",
        type=float,
        default=DEFAULT_RAISE,
        help=f"vertical offset of the image in pt; 0 centers it on the line, positive lifts it (default: {DEFAULT_RAISE:g})",
    )
    parser.add_argument(
        "--alpha-threshold",
        type=float,
        default=DEFAULT_ALPHA_THRESHOLD_PERCENT,
        help=f"minimum opacity in percent (0-100) for a pixel to be drawn; fainter "
        f"pixels are skipped (default: {DEFAULT_ALPHA_THRESHOLD_PERCENT:g})",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def convert(
    input_path: str | Path,
    output_path: str | Path,
    max_size: int,
    dot_size: float = DEFAULT_DOT_SIZE,
    raise_offset: float = DEFAULT_RAISE,
    alpha_threshold: float = DEFAULT_ALPHA_THRESHOLD,
) -> None:
    """Run the full image-to-Markdown pipeline and write the result.

    Loads and downscales the image at ``input_path`` to fit within ``max_size``,
    renders it as a single inline ``$…$`` block of stacked ``dot_size``-pt dots
    shifted vertically by ``raise_offset`` pt, and writes it to ``output_path``.
    Pixels with an alpha below ``alpha_threshold`` (a raw 0-255 value) are skipped.
    Errors from any stage (missing or invalid image, unwritable output) propagate
    to the caller.
    """
    image = load_and_scale(input_path, max_edge=max_size)
    write_markdown([stack_image(image, dot_size, raise_offset, alpha_threshold)], output_path)


def _error(message: str) -> int:
    """Print a CLI error to stderr with the standard prefix and return exit code 1."""
    print(f"img2dots: {message}", file=sys.stderr)
    return 1


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    for name, value in (("--max-size", args.max_size), ("--dot-size", args.dot_size)):
        if value <= 0:
            return _error(f"{name} must be a positive size, got {value}.")

    if not 0 <= args.alpha_threshold <= 100:
        return _error(f"--alpha-threshold must be between 0 and 100, got {args.alpha_threshold:g}.")

    input_path = Path(args.input)
    if not input_path.exists():
        return _error(f"input file not found: {args.input}")
    if input_path.is_dir():
        return _error(f"input is not a file (it is a directory): {args.input}")

    output_dir = Path(args.output).parent
    if not output_dir.exists():
        return _error(f"output directory does not exist: {output_dir}")

    alpha_cutoff = args.alpha_threshold / 100 * 255
    try:
        convert(
            args.input,
            args.output,
            args.max_size,
            args.dot_size,
            args.raise_offset,
            alpha_cutoff,
        )
    except UnidentifiedImageError:
        return _error(f"{args.input} is not a recognized image file.")
    except OSError as error:
        reason = error.strerror or "could not read or write file"
        return _error(f"{reason}: {error.filename or args.input}")

    print(f"img2dots: wrote {args.output}")
    return 0
