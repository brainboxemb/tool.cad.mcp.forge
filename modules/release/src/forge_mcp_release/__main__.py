"""Validate or publish one exact Forge CAD MCP release from stable main."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from .policy import ReleasePolicyError
from .service import preflight, publish


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", required=True)
    parser.add_argument("--command", required=True)
    parser.add_argument("--actor", required=True)
    parser.add_argument("--owner", required=True)
    parser.add_argument("--issue-number", required=True, type=int)
    parser.add_argument("--source-root", type=Path, default=Path("."))
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()

    token = os.environ.get("GH_TOKEN")
    if not token:
        raise ReleasePolicyError("GH_TOKEN is required")

    source_root = args.source_root.resolve()
    if args.check_only:
        tag, target_sha = preflight(
            repository=args.repository,
            command=args.command,
            actor=args.actor,
            owner=args.owner,
            token=token,
            source_root=source_root,
        )
        print(f"{tag}: {target_sha}")
        return 0

    tag, url = publish(
        repository=args.repository,
        command=args.command,
        actor=args.actor,
        owner=args.owner,
        issue_number=args.issue_number,
        token=token,
        source_root=source_root,
    )
    print(f"{tag}: {url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
