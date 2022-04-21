from __future__ import annotations

import argparse
import json
import os
import shutil

from . import ContributterRanking, __version__


class CustomHelpFormatter(
    argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter
):
    pass


def check_file(s: str) -> str:
    if os.path.isfile(s):
        return s
    else:
        raise argparse.ArgumentTypeError(f"{repr(s)} is not a file.")


def parse_args() -> argparse.Namespace:
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
    parser.add_argument("-q", "--quiet", action="store_true", help="suppress log print")
    parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {__version__}"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    CR = ContributterRanking(args.key)
    status_code, response_json, _ = CR.run()
    status = 0
    if status_code == 200:
        print(
            "# Running Bot was successful!\n"
            f"# See at: https://twitter.com/{response_json['user']['screen_name']}/status/{response_json['id']}"
        )
    else:
        print("# Running Bot was failed!")
        status = 1

    if not args.quiet:
        print(json.dumps(response_json, sort_keys=False, indent=4))
    exit(status)


if __name__ == "__main__":
    main()
