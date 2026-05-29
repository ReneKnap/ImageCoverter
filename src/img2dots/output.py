"""Write assembled LaTeX content to a Markdown file.

Final stage of the pipeline: persist the inline-LaTeX produced by
:func:`img2dots.latex.stack_image` (a single ``$…$`` block holding the whole
stacked dot grid) to a Markdown file. The writer itself is generic — it joins
the given list of strings into separate Markdown paragraphs — so it also handles
the degenerate single-element list the current pipeline passes it.
"""

from pathlib import Path


def write_markdown(lines: list[str], path: str | Path) -> None:
    """Write ``lines`` to ``path`` as Markdown, one paragraph per element.

    Elements are separated by a blank line and the file ends with a trailing
    newline when there is content. An empty ``lines`` list yields an empty
    (0-byte) file. An existing file at ``path`` is overwritten.
    """
    content = "\n\n".join(lines)
    if content:
        content += "\n"
    Path(path).write_text(content, encoding="utf-8")
