"""
datazen - Orchestrates the "parameterized target" capability.
"""

# built-in
import logging
from typing import Dict, List, Optional, Tuple

# internal
from datazen.targets import (
    MatchData,
    match_target,
    parse_targets,
    resolve_target_data,
)


class TargetResolver:
    """
    A class for managing resolution of literal and templated target
    definitions.
    """

    def __init__(
        self, logger: logging.Logger = logging.getLogger(__name__)
    ) -> None:
        """Constuct a new target resolver."""

        self.literals: Dict[str, dict] = {}
        self.patterns: Dict[str, dict] = {}
        self.logger = logger

    def clear(self) -> None:
        """
        Re-initialize target dataset, in case a new manifest is reloaded.
        """

        self.literals = {}

    def get_target(self, group: str, name: str) -> Optional[dict]:
        """
        Attempt to get a literal target from what has been loaded so far.
        """

        # try to return an existing literal target if possible
        assert group in self.literals and group in self.patterns
        if group in self.literals and name in self.literals[group]:
            data = self.literals[group][name]
            assert data["literal"]
            return data["data"]

        # short-circuit case where we don't have any patterns for this group
        # to try
        if group not in self.patterns or not self.patterns[group]:
            return None

        # attempt to match this target to any of our patterns for this group
        matches: List[Tuple[dict, MatchData]] = []
        for pattern in self.patterns[group].values():
            result = match_target(name, pattern["pattern"], pattern["keys"])
            if result.found:
                matches.append((pattern, result.substitutions))

        # make sure we matched only one target
        if not matches or len(matches) > 1:
            log_str = (
                "couldn't match one target for '%s-%s', found "
                + "%d candidates"
            )
            self.logger.error(log_str, group, name, len(matches))
            for match in matches:
                self.logger.error("%s", match[0]["data"]["name"])
            return None

        # create a new target from the template, save it as a new literal so
        # we don't need to re-match it
        new_literal = resolve_target_data(matches[0][0]["data"], matches[0][1])
        data = {
            "literal": True,
            "data": new_literal,
            "pattern": new_literal["name"],
            "keys": [],
        }
        data["data"]["overrides"] = matches[0][1]
        self.literals[group][new_literal["name"]] = data
        return new_literal

    def register_group(self, name: str, targets: List[dict]) -> None:
        """
        From a name of a group that contains targets, initialize it by also
        providing its target datset.
        """

        self.literals[name], self.patterns[name] = parse_targets(targets)
