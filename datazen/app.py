"""
datazen - This package's command-line entry-point application.
"""

# built-in
import argparse

# internal
from datazen.classes.environment import from_manifest
from datazen import DEFAULT_MANIFEST


def entry(args: argparse.Namespace) -> int:
    """Execute the requested task."""

    result = 0
    env = from_manifest(args.manifest)
    if env.get_valid():
        # clean, if requested
        if args.sync:
            env.write_cache()
        if args.clean:
            env.clean_cache()
        elif args.describe:
            env.describe_cache()
        else:
            # execute targets
            result = int(not env.execute_targets(args.targets))
    else:
        result = 1
    return result


def add_app_args(parser: argparse.ArgumentParser) -> None:
    """Add application-specific arguments to the command-line parser."""

    parser.add_argument(
        "-m",
        "--manifest",
        default=DEFAULT_MANIFEST,
        help=("manifest to execute tasks from (default: " + "'%(default)s')"),
    )
    parser.add_argument(
        "-c",
        "--clean",
        action="store_true",
        help="clean the manifest's cache and exit",
    )
    parser.add_argument(
        "--sync",
        action="store_true",
        help=(
            "sync the manifest's cache (write-through) "
            + "with the state of the file system before "
            + "execution"
        ),
    )
    parser.add_argument(
        "-d",
        "--describe",
        action="store_true",
        help="describe the manifest's cache and exit",
    )
    parser.add_argument("targets", nargs="*", help="target(s) to execute")
