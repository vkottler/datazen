
"""
datazen - A centralized store for runtime data.
"""

# internal
from datazen.classes.config_environment import ConfigEnvironment
from datazen.classes.template_environment import TemplateEnvironment


class Environment(ConfigEnvironment, TemplateEnvironment):
    """ A wrapper for inheriting all environment-loading capabilities. """
