"""Write assembled LaTeX rows to a Markdown file.

Final stage before the CLI: take the inline-LaTeX ``$…$`` blocks produced by
:func:`img2dots.latex.assemble_rows` and persist them as a Markdown file. Each
image row becomes its own Markdown paragraph (rows separated by a blank line),
so a renderer lays the dot grid out line by line.
"""

from pathlib import Path


def write_markdown(lines: list[str], path: str | Path) -> None:
    """Write ``lines`` to ``path`` as Markdown, one paragraph per row.

    Rows are separated by a blank line and the file ends with a trailing
    newline when there is content. An empty ``lines`` list yields an empty
    (0-byte) file. An existing file at ``path`` is overwritten.
    """
    content = "\n\n".join(lines)
    if content:
        content += "\n"
    Path(path).write_text(content, encoding="utf-8")
