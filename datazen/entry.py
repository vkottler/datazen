
"""
datazen - This package's command-line entry-point.
"""

# built-in
import argparse
import logging
import os
import sys
from typing import List

# internal
from datazen.classes.environment import from_manifest
from datazen import VERSION, DESCRIPTION, DEFAULT_MANIFEST

LOG = logging.getLogger(__name__)


def main(argv: List[str] = None) -> int:
    """ Program entry-point. """

    result = 0

    # fall back on command-line arguments
    command_args = sys.argv
    if argv is not None:
        command_args = argv

    # initialize argument parsing
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument("--version", action="version",
                        version="%(prog)s {0}".format(VERSION))
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="set to increase logging verbosity")
    parser.add_argument("-m", "--manifest", default=DEFAULT_MANIFEST,
                        help=("manifest to execute tasks from (default: " +
                              "'%(default)s')"))
    parser.add_argument("-c", "--clean", action="store_true",
                        help="clean the manifest's cache and exit")
    parser.add_argument("-d", "--describe", action="store_true",
                        help="describe the manifest's cache and exit")
    parser.add_argument("-C", "--dir", default=os.getcwd(), dest="dir",
                        help=("execute from a specific directory (default: " +
                              "'%(default)s')"))
    parser.add_argument("targets", nargs="*", help="target(s) to execute")

    starting_dir = os.getcwd()

    # parse arguments and execute the requested command
    try:
        args = parser.parse_args(command_args[1:])
        args.version = VERSION

        # initialize logging
        log_level = logging.DEBUG if args.verbose else logging.INFO
        logging.basicConfig(level=log_level,
                            format=("%(name)-30s - %(levelname)-8s - "
                                    "%(message)s"))

        # change to the specified directory
        os.chdir(args.dir)

        env = from_manifest(args.manifest)

        if env.get_valid():
            # clean, if requested
            if args.clean:
                env.clean_cache()
            elif args.describe:
                env.describe_cache()
            else:
                # execute targets
                for target in args.targets:
                    if not env.execute(target)[0]:
                        LOG.error("target '%s' failed", target)
                        result = 1
                        break
        else:
            result = 1

    except SystemExit as exc:
        result = 1
        if exc.code is not None:
            result = exc.code

    # return to starting dir
    os.chdir(starting_dir)

    return result
