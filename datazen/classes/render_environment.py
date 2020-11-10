
"""
datazen - An environment extension that exposes rendering capabilities.
"""

# built-in
import logging

# internal
from datazen.classes.manifest_cache_environment import ManifestCacheEnvironment

LOG = logging.getLogger(__name__)


class RenderEnvironment(ManifestCacheEnvironment):
    """ Leverages a cache-equipped environment to render templates. """

    def valid_render(self, render_entry: dict, namespace: str) -> bool:
        """ Perform the render specified by the entry. """

        LOG.info(self.manifest["path"])
        LOG.info(render_entry)
        LOG.info(namespace)

        # resolve dependencies

        return True
