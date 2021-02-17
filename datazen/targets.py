
"""
datazen - An interface for parsing and matching targets.
"""

# built-in
import re
from typing import Tuple, List

KW_OPEN = "{"
KW_CLOSE = "}"
KW_PATTERN = "[a-zA-Z0-9]+"


def parse_target(name: str) -> Tuple[re.Pattern, List[str]]:
    """
    From a target name, provide a compiled pattern and an in-order list of
    the names of the keyword arguments that will appear (group order).
    """

    open_len = name.count(KW_OPEN)
    assert open_len == name.count(KW_CLOSE)

    pattern = "^"
    keys = []
    for _ in range(open_len):
        start = name.index(KW_OPEN) + 1
        end = name.index(KW_CLOSE)
        pattern += name[:start - 1]
        pattern += "({})".format(KW_PATTERN)
        keys.append(name[start:end])
        name = name[end + 1:]
    pattern += name + "$"

    assert len(keys) == open_len
    return re.compile(pattern), keys
