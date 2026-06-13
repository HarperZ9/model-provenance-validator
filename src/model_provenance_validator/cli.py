from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .validator import DEFAULT_SCHEMA, load_envelope, load_schema, validate_envelope


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate model-reference provenance JSON envelopes."
    )
    parser.add_argument("envelopes", nargs="+", type=Path, help="Envelope JSON files.")
    parser.add_argument(
        "--schema",
        type=Path,
        default=DEFAULT_SCHEMA,
        help="Schema JSON file. Defaults to the bundled schema.",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON results.")
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print a batch validation summary instead of per-file detail.",
    )
    return parser


def _load_schema_or_error(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        return load_schema(path), None
    except (FileNotFoundError, OSError, ValueError, json.JSONDecodeError) as exc:
        return None, str(exc)


def _validate_path(path: Path, schema: dict[str, Any]) -> dict[str, Any]:
    try:
        errors = validate_envelope(load_envelope(path), schema)
    except (FileNotFoundError, OSError, ValueError, json.JSONDecodeError) as exc:
        errors = [{"path": "$", "message": str(exc)}]
    else:
        errors = [asdict(error) for error in errors]
    return {"path": str(path), "valid": not errors, "errors": errors}


def _summarize_results(results: list[dict[str, Any]]) -> dict[str, Any]:
    invalid = [result for result in results if not result["valid"]]
    return {
        "total": len(results),
        "valid": len(results) - len(invalid),
        "invalid": len(invalid),
        "error_count": sum(len(result["errors"]) for result in invalid),
        "action_items": [
            f"{result['path']}: resolve {len(result['errors'])} validation error(s)"
            for result in invalid[:8]
        ],
    }


def _format_summary(summary: dict[str, Any]) -> str:
    lines = [
        f"total: {summary['total']}",
        f"valid: {summary['valid']}",
        f"invalid: {summary['invalid']}",
        f"error_count: {summary['error_count']}",
        "action_items:",
    ]
    actions = summary["action_items"] or ["none"]
    lines.extend(f"- {action}" for action in actions)
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    schema, schema_error = _load_schema_or_error(args.schema)
    if schema is None:
        print(json.dumps({"error": schema_error}, indent=2) if args.json else f"error: {schema_error}")
        return 1

    results = [_validate_path(path, schema) for path in args.envelopes]
    has_errors = any(not result["valid"] for result in results)

    if args.summary:
        summary = _summarize_results(results)
        print(json.dumps(summary, indent=2) if args.json else _format_summary(summary))
    elif args.json:
        print(json.dumps(results, indent=2))
    else:
        for result in results:
            if result["valid"]:
                print(f"{result['path']}: valid")
            else:
                print(f"{result['path']}: invalid")
                for error in result["errors"]:
                    print(f"  {error['path']}: {error['message']}")

    return 1 if has_errors else 0
