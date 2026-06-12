from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

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
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    schema = load_schema(args.schema)
    results = []
    has_errors = False

    for path in args.envelopes:
        errors = validate_envelope(load_envelope(path), schema)
        has_errors = has_errors or bool(errors)
        results.append(
            {
                "path": str(path),
                "valid": not errors,
                "errors": [asdict(error) for error in errors],
            }
        )

    if args.json:
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

