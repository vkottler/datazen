
"""
datazen - An interface for parsing and matching targets.
"""

# built-in
from collections import defaultdict
import re
from typing import Dict, Tuple, List

KW_OPEN = "{"
KW_CLOSE = "}"
KW_PATTERN = "[a-zA-Z0-9]+"


def target_is_literal(name: str) -> bool:
    """
    Determine if a named target has keywords or not (is otherwise literal).
    """

    return name.count(KW_OPEN) == name.count(KW_CLOSE) == 0


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


def parse_targets(targets: List[dict]) -> Tuple[Dict[str, dict],
                                                Dict[str, dict]]:
    """
    From a list of target structures, parse them into a dictionary with keys
    as target names and data initialization to support future interaction.
    """

    literals: Dict[str, dict] = {}
    patterns: Dict[str, dict] = {}

    for target in targets:
        data: dict = {}
        assert "name" in target
        data["literal"] = target_is_literal(target["name"])
        dest_set = literals if data["literal"] else patterns
        data["data"] = target
        parsed = parse_target(target["name"])
        data["pattern"] = parsed[0]
        data["keys"] = parsed[1]
        dest_set[target["name"]] = data

    return literals, patterns


def match_target(name: str, pattern: re.Pattern,
                 keys: List[str]) -> Tuple[bool, Dict[str, str]]:
    """
    From a target name, attempt to match against a pattern and resolve a set
    of key names.
    """

    data: Dict[str, str] = defaultdict(str)
    result = pattern.fullmatch(name)

    if result is None:
        return False, data

    for idx, key in enumerate(keys):
        data[key] = result.group(1 + idx)

    return True, data


def resolve_target_list(target_list: list, match_data: Dict[str, str]) -> list:
    """
    Resovle matched-target data into a list form of target data from a
    manifest.
    """

    result: list = []

    for value in target_list:
        if isinstance(value, dict):
            result.append(resolve_target_data(value, match_data))
        elif isinstance(value, list):
            result.append(resolve_target_list(value, match_data))
        elif isinstance(value, str):
            result.append(value.format(**match_data))
        else:
            result.append(value)

    assert len(result) == len(target_list)
    return result


def resolve_target_data(target_data: dict, match_data: Dict[str, str]) -> dict:
    """ Resolve matched-target data into a target's data from a manifest. """

    result: dict = {}

    for key, value in target_data.items():
        if isinstance(value, dict):
            result[key] = resolve_target_data(value, match_data)
        elif isinstance(value, list):
            result[key] = resolve_target_list(value, match_data)
        elif isinstance(value, str):
            result[key] = value.format(**match_data)
        else:
            result[key] = value

    assert len(result.keys()) == len(target_data.keys())
    return result
