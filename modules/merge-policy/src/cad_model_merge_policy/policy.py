"""Classify allowed branch integrations."""

class MergePolicyError(RuntimeError):
    """Branch integration violates project policy."""


_TEMPORARY_PREFIXES = ("issue/", "fix/", "feature/", "docs/", "chore/", "release/")


def merge_method(*, head: str, base: str) -> str:
    if base == "main" and head.startswith(_TEMPORARY_PREFIXES):
        return "squash"
    raise MergePolicyError(f"unsupported branch integration: {head} -> {base}")
