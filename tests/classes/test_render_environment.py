
"""
datazen - Tests for the 'RenderEnvironment' class mixin.
"""

# built-in
import os

# module under test
from datazen.classes.environment import from_manifest

# internal
from ..resources import get_resource, injected_content, scoped_environment


def test_render_simple():
    """ Test that rendering isn't always necessary. """

    with scoped_environment("manifest.yaml", True) as env:
        assert env.render("test.md") == (True, True)
        assert env.render("test.py") == (True, True)
        env.write_cache()
        new_env = from_manifest(get_resource("manifest.yaml", True))
        assert new_env.render("test.md") == (True, False)
        assert new_env.render("test.py") == (True, False)


def test_render_children():
    """
    Test render targets used to validate behavior of the 'children' key.
    """

    with scoped_environment("manifest.yaml", True) as env:
        assert env.group("test-children") == (True, True)


def test_render_common_template_dep():
    """
    Make sure that a render task can't consume the state of a template change
    for other tasks that depend on that same change.
    """

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
            assert new_env.render("test") == (True, False)
            assert new_env.render("render2") == (True, True)
            assert new_env.execute_targets(["renders-test",
                                            "renders-render2"])
            assert new_env.group("render_test") == (True, True)
            assert new_env.group("render_test") == (True, False)

            new_env.restore_cache()
