from scripts.ci_scope import runtime_for_event, runtime_required


def test_docs_and_repository_policy_changes_skip_released_stack_acceptance():
    assert not runtime_required(
        [
            "docs/plan.md",
            "AGENTS.md",
            "README.md",
            "ci.yml",
            "modules/merge-policy/src/cad_model_merge_policy/policy.py",
        ]
    )


def test_runtime_package_and_acceptance_changes_require_released_stack():
    for path in (
        "src/forge_mcp/runtime.py",
        "src/forge_mcp/skills/forge-modeling/SKILL.md",
        "pyproject.toml",
        ".github/workflows/ci.yml",
        "scripts/ci_scope.py",
        "scripts/prepare_acceptance.py",
        "tests/fixtures/acceptance_box.py",
        "tests/test_compiler.py",
        "tests/test_runtime.py",
        "tests/test_conversion.py",
    ):
        assert runtime_required([path]), path


def test_main_push_and_manual_runs_always_require_released_stack():
    assert runtime_for_event("push")
    assert runtime_for_event("workflow_dispatch")


def test_pull_request_scope_uses_changed_paths():
    assert not runtime_for_event("pull_request", ["docs/design.md"])
    assert runtime_for_event("pull_request", ["src/forge_mcp/compiler.py"])
