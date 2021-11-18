"""
datazen - Reading and writing a known header signature to output files.
"""

# built-in
import os
from typing import List, Tuple

# internal
from datazen import PKG_NAME, VERSION
from datazen.parsing import get_hash

BARRIER = "="


def get_comment_data(
    file_data: str, dynamic: bool = True
) -> List[Tuple[str, str]]:
    """
    Get tuples (key-value pairs) of data to write into the file fingerprint.
    """

    line_data = [
        (False, ("generator", PKG_NAME)),
        (True, ("version", VERSION)),
        (False, ("hash", get_hash(file_data))),
    ]

    # filter out any possibly undesired data
    resolved = []
    for line in line_data:
        if not line[0] or dynamic:
            resolved.append(line[1])

    return resolved


def apply_barriers(comment_lines: List[str], char: str) -> None:
    """
    Optionally add decoration to the comment lines by adding a barrier at
    the beginning and end.
    """

    barrier = BARRIER * max(int(len(com) / len(char)) for com in comment_lines)
    if comment_lines:
        comment_lines.insert(0, barrier)
        comment_lines.append(barrier)
        comment_lines.append("")


def resolve_encapsulation(comment_lines: List[str], file_ext: str) -> str:
    """
    Turn the requested line data into something that can be embedded in the
    target file type.
    """

    new_lines = []

    ext = file_ext.lower()
    if ext in ("py", "mk", "yaml"):
        for line in comment_lines:
            new_lines.append("# " + line if line else line)
    elif ext in ("md", "html", "svg"):
        new_lines.append("<!--")
        for line in comment_lines:
            if line:
                new_lines.append("    " + line)
        new_lines.append("-->" + os.linesep + os.linesep)

    return os.linesep.join(new_lines)


def build_fingerprint(
    file_data: str, file_ext: str, char: str = BARRIER, dynamic: bool = True
) -> str:
    """
    Build a String that should be prepended to the final file output for
    user awareness and automated interpretation.
    """

    comment_lines = []
    line_data = get_comment_data(file_data, dynamic)
    for line in line_data:
        comment_lines.append(f"{line[0]}={line[1]}")
    apply_barriers(comment_lines, char)
    return resolve_encapsulation(comment_lines, file_ext)
