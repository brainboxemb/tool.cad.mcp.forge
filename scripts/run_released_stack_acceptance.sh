#!/usr/bin/env bash
set -euo pipefail

: "${FORGE_SOURCE_ROOT:?FORGE_SOURCE_ROOT must point to the qualified Forge checkout}"

python scripts/prepare_acceptance.py
rm -rf build/runtime-wheel
python -m pip wheel . --no-deps -w build/runtime-wheel

docker run --rm \
  -e SOLIDCRAFT_RUNTIME_ACCEPTANCE=1 \
  -e SOLIDCRAFT_CONVERSION_ACCEPTANCE=1 \
  -e SOLIDCRAFT_TEST_COMMANDS=/repo/build/runtime-fixture/build/solidcraft.json \
  -e SOLIDCRAFT_ORIGINAL_COMMANDS=/repo/tests/fixtures/existing-box.json \
  -e SOLIDCRAFT_TRANSLATED_COMMANDS=/repo/build/conversion-fixture/build/translated.json \
  -v "$PWD:/repo:ro" \
  -w /repo \
  ghcr.io/brainboxemb/cad-solidcraft:v0.3.8 \
  sh -c "python -m venv /tmp/mcp-venv && /tmp/mcp-venv/bin/pip install /repo/build/runtime-wheel/*.whl pytest\>=8,\<9 Pillow\>=10 && /tmp/mcp-venv/bin/python -m pytest -q -p no:cacheprovider tests/test_runtime.py tests/test_conversion.py"
