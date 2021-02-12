
"""
datazen - Tests for the 'RenderEnvironment' class mixin.
"""

# built-in
import os

# module under test
from datazen.classes.environment import from_manifest

# internal
from ..resources import get_resource, injected_content, scoped_environment


def test_render_common_template_dep():
    """ TODO """

    with scoped_environment("manifest.yaml", True) as env:
        # perform renders
        assert env.render("test") == (True, True)
        assert env.render("render2") == (True, True)
        env.write_cache()

        # change the template contents
        path = os.path.join("templates2", "test.j2")
        with injected_content(path, True) as template:
            template.write("test_asdf" + os.linesep)

            # update the template and re-load the manifest
            new_env = from_manifest(get_resource("manifest.yaml", True))
            assert new_env.render("test") == (True, True)
            assert new_env.render("render2") == (True, True)
            assert new_env.execute_targets(["renders-test",
                                            "renders-render2"])
            assert new_env.group("render_test") == (True, False)
