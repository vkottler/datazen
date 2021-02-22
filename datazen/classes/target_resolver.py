
"""
datazen - Orchestrates the "parameterized target" capability.
"""

# built-in
from typing import Dict, List, Optional

# internal
from datazen.targets import parse_targets


class TargetResolver:
    """
    A class for managing resolution of literal and templated target
    definitions.
    """

    def __init__(self) -> None:
        """ Constuct a new target resolver. """

        self.data: Dict[str, dict] = {}

    def clear(self) -> None:
        """
        Re-initialize target dataset, in case a new manifest is reloaded.
        """

        self.data = {}

    def get_literal(self, group: str, name: str) -> Optional[dict]:
        """
        Attempt to get a literal target from what has been loaded so far.
        """

        if group not in self.data or name not in self.data[group]:
            # this is probably where we try to pattern match, if we can match
            # we should actually add the concrete target and return it
            return None

        data = self.data[group][name]
        assert data["literal"]
        return data["data"]

    def register_group(self, name: str, targets: List[dict]) -> None:
        """
        From a name of a group that contains targets, initialize it by also
        providing its target datset.
        """

        self.data[name] = parse_targets(targets)
