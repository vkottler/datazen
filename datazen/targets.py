"""
datazen - An interface for parsing and matching targets.
"""

# built-in
from copy import deepcopy
from typing import Any, Dict, List, Tuple

# third-party
from vcorelib.dict import GenericStrDict, merge
from vcorelib.target import Substitutions, Target

# internal
from datazen.paths import (
    advance_dict_by_path,
    format_resolve_delims,
    unflatten_dict,
)


def parse_targets(
    targets: List[GenericStrDict],
) -> Tuple[Dict[str, GenericStrDict], Dict[str, GenericStrDict]]:
    """
    From a list of target structures, parse them into a dictionary with keys
    as target names and data initialization to support future interaction.
    """

    literals: Dict[str, GenericStrDict] = {}
    patterns: Dict[str, GenericStrDict] = {}

    for target in targets:
        data: GenericStrDict = {"data": target}
        assert "name" in target
        name = target["name"]
        parsed = Target(name)
        data["parsed"] = parsed
        data["literal"] = parsed.literal
        dest_set = literals if data["literal"] else patterns

        dest_set[name] = data

    return literals, patterns


def resolve_target_list(
    target_list: List[Any], match_data: Substitutions
) -> List[Any]:
    """
    Resovle matched-target data into a list form of target data from a
    manifest.
    """

    result: List[Any] = []

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


def resolve_dep_data(
    entry: GenericStrDict, data: GenericStrDict
) -> GenericStrDict:
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


def resolve_target_data(
    target_data: GenericStrDict, match_data: Substitutions
) -> GenericStrDict:
    """Resolve matched-target data into a target's data from a manifest."""

    result: GenericStrDict = {}

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
