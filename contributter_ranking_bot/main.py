"""CLI."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys

from . import ContributterRanking, __version__


class CustomHelpFormatter(
    argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter
):
    """Custom formatter to pretty help text."""


def check_file(arg_s: str) -> str:
    """Check if given path is a file."""
    if not os.path.isfile(arg_s):
        raise argparse.ArgumentTypeError(f"{repr(arg_s)} is not a file.")
    return arg_s


def check_positive(arg_s: str) -> int:
    """Check if given str is a positive int."""
    s_int = int(arg_s)
    if s_int <= 0:
        raise argparse.ArgumentTypeError(f"{repr(arg_s)} is not a positive int.")
    return s_int


def check_natural(arg_s: str) -> int:
    """Check if given str is a natural int."""
    s_int = int(arg_s)
    if s_int < 0:
        raise argparse.ArgumentTypeError(f"{repr(arg_s)} is not a natural int. (>=0)")
    return s_int


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="crb",
        description="This command makes Contributter Ranking Bot easier to run.",
        formatter_class=(
            lambda prog: CustomHelpFormatter(
                prog,
                **{
                    "width": shutil.get_terminal_size(fallback=(120, 50)).columns,
                    "max_help_position": 40,
                },
            )
        ),
    )
    parser.add_argument("-k", "--key", type=check_file, help="key file", metavar="PATH")
    parser.add_argument(
        "-d",
        "--day-before",
        type=check_natural,
        help="n days before",
        metavar="DAY",
        default=1,
    )
    parser.add_argument(
        "-w",
        "--wait-sec",
        type=check_natural,
        help="interval of retrieving tweets",
        metavar="SEC",
        default=10,
    )
    parser.add_argument(
        "-n",
        "--top-n",
        type=check_positive,
        help="top n to tweet",
        metavar="N",
        default=3,
    )
    parser.add_argument("-q", "--quiet", action="store_true", help="suppress log print")
    parser.add_argument(
        "-D", "--dry-run", action="store_true", help="tweet without mentions"
    )
    parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {__version__}"
    )
    return parser.parse_args()


def main() -> None:
    """Run CLI."""
    args = parse_args()
    cr_ = ContributterRanking(
        key_path=args.key,
        day_before=args.day_before,
        wait_sec=args.wait_sec,
    )
    status_code, response_json, _ = cr_.run(top_n=args.top_n, dry_run=args.dry_run)
    status = 0
    if status_code == 200:
        print(
            "# Running Bot was successful!\n# See at: https://twitter.com/"
            f"{response_json['user']['screen_name']}/status/{response_json['id']}"
        )
    else:
        print("# Running Bot was failed!")
        status = 1

    if not args.quiet:
        print(json.dumps(response_json, sort_keys=False, indent=4))
    sys.exit(status)


if __name__ == "__main__":
    main()
