from __future__ import annotations

import subprocess
import sys
import os
from pathlib import Path

from model_provenance_validator.validator import load_envelope, load_schema, validate_envelope


FIXTURES = Path(__file__).parent / "fixtures"


def test_valid_envelope_passes() -> None:
    errors = validate_envelope(load_envelope(FIXTURES / "valid.json"), load_schema())

    assert errors == []


def test_invalid_envelope_reports_specific_errors() -> None:
    errors = validate_envelope(load_envelope(FIXTURES / "invalid.json"), load_schema())
    messages = {(error.path, error.message) for error in errors}

    assert ("$.subject", "expected non-empty string") in messages
    assert any(error.path == "$.references" for error in errors)
    assert any(error.path == "$.source.kind" for error in errors)
    assert ("$.validation.extra", "unexpected field") in messages


def test_module_cli_returns_nonzero_for_invalid_envelope() -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).parents[1] / "src")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "model_provenance_validator",
            str(FIXTURES / "invalid.json"),
        ],
        check=False,
        capture_output=True,
        env=env,
        text=True,
    )

    assert result.returncode == 1
    assert "invalid" in result.stdout
