"""
datazen - An interface for parsing and matching targets.
"""

# built-in
from copy import deepcopy
from typing import Dict, List, Tuple

# third-party
from vcorelib.dict import merge
from vcorelib.target import Substitutions, Target

# internal
from datazen.paths import (
    advance_dict_by_path,
    format_resolve_delims,
    unflatten_dict,
)


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
        data: dict = {"data": target}
        assert "name" in target
        name = target["name"]
        parsed = Target(name)
        data["parsed"] = parsed
        data["literal"] = parsed.literal
        dest_set = literals if data["literal"] else patterns

        dest_set[name] = data

    return literals, patterns


def resolve_target_list(target_list: list, match_data: Substitutions) -> list:
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


def resolve_target_data(target_data: dict, match_data: Substitutions) -> dict:
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
