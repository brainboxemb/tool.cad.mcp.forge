"""Command entrypoint for repository-local CI support."""

from __future__ import annotations

import argparse
from pathlib import Path

from . import acceptance, scope


def main() -> int:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)

    scope_parser = commands.add_parser("scope")
    scope_parser.add_argument("--event", required=True)
    scope_parser.add_argument("--base", default="")
    scope_parser.add_argument("--head", default="")
    scope_parser.add_argument("--manual-full", default="false")
    scope_parser.add_argument("--github-output", type=Path)

    commands.add_parser("acceptance")
    args = parser.parse_args()

    if args.command == "acceptance":
        acceptance.run()
        return 0

    required, paths = scope.classify(
        event=args.event,
        base=args.base,
        head=args.head,
        manual_full=scope.parse_bool(args.manual_full),
    )
    print(f"released_stack_acceptance={'required' if required else 'skipped'}")
    for path in paths:
        print(path)
    if args.github_output is not None:
        scope.write_github_output(args.github_output, runtime=required)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
