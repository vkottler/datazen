"""
datazen - An interface for parsing and matching targets.
"""

# built-in
from collections import defaultdict
from copy import deepcopy
import re
from typing import Dict, List, NamedTuple, Tuple

# internal
from datazen.parsing import merge
from datazen.paths import (
    advance_dict_by_path,
    format_resolve_delims,
    unflatten_dict,
)

KW_OPEN = "{"
KW_CLOSE = "}"
KW_PATTERN = "[a-zA-Z0-9-_.]+"


def target_is_literal(name: str) -> bool:
    """
    Determine if a named target has keywords or not (is otherwise literal).
    """

    return name.count(KW_OPEN) == name.count(KW_CLOSE) == 0


class ParseResult(NamedTuple):
    """
    An encapsulation for a regular expression and the in-order keywords that
    can be mapped to 'group' indices.
    """

    pattern: re.Pattern
    keys: List[str]


def parse_target(name: str) -> ParseResult:
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
        pattern += name[: start - 1]
        pattern += f"({KW_PATTERN})"
        keys.append(name[start:end])
        name = name[end + 1 :]
    pattern += name + "$"

    assert len(keys) == open_len
    return ParseResult(re.compile(pattern), keys)


def parse_targets(
    targets: List[dict],
) -> Tuple[Dict[str, dict], Dict[str, dict]]:
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
        data["pattern"] = parsed.pattern
        data["keys"] = parsed.keys
        dest_set[target["name"]] = data

    return literals, patterns


MatchData = Dict[str, str]


class TargetMatch(NamedTuple):
    """
    An encapsulation of results when attempting to patch a target name to a
    pattern. If a target was matched and had keyword substitutions, the actual
    values used will be set as match data.
    """

    found: bool
    substitutions: MatchData


def match_target(
    name: str, pattern: re.Pattern, keys: List[str]
) -> TargetMatch:
    """
    From a target name, attempt to match against a pattern and resolve a set
    of key names.
    """

    data: MatchData = defaultdict(str)
    result = pattern.fullmatch(name)

    if result is None:
        return TargetMatch(False, data)

    for idx, key in enumerate(keys):
        data[key] = result.group(1 + idx)

    return TargetMatch(True, data)


def resolve_target_list(target_list: list, match_data: MatchData) -> list:
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
            result.append(format_resolve_delims(value, match_data))
        else:
            result.append(value)

    assert len(result) == len(target_list)
    return result


def resolve_dep_data(entry: dict, data: dict) -> dict:
    """
    Implements the business logic for applying match data to manifest entries.
    """

    if "overrides" in entry and "override_path" in entry:
        data = deepcopy(data)
        to_update = advance_dict_by_path(
            entry["override_path"].split("."), data
        )
        if isinstance(to_update, dict):
            merge(
                to_update,
                unflatten_dict(entry["overrides"]),
                expect_overwrite=True,
            )

    return data


def resolve_target_data(target_data: dict, match_data: MatchData) -> dict:
    """Resolve matched-target data into a target's data from a manifest."""

    result: dict = {}

    for key, value in target_data.items():
        if isinstance(value, dict):
            result[key] = resolve_target_data(value, match_data)
        elif isinstance(value, list):
            result[key] = resolve_target_list(value, match_data)
        elif isinstance(value, str):
            result[key] = format_resolve_delims(value, match_data)
        else:
            result[key] = value

    assert len(result.keys()) == len(target_data.keys())
    return result
