from __future__ import annotations

import json
import re
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Any

DEFAULT_SCHEMA = resources.files(__package__) / "schema.json"


@dataclass(frozen=True)
class ValidationError:
    path: str
    message: str


def load_schema(path: str | Path = DEFAULT_SCHEMA) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("Schema root must be a JSON object")
    return data


def load_envelope(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("Envelope root must be a JSON object")
    return data


def validate_envelope(envelope: dict[str, Any], schema: dict[str, Any]) -> list[ValidationError]:
    errors: list[ValidationError] = []
    _validate_value("$", envelope, schema, errors)
    return errors


def _validate_object(
    path: str,
    value: dict[str, Any],
    rules: dict[str, Any],
    errors: list[ValidationError],
) -> None:
    properties = rules.get("properties", {})
    required = rules.get("required", [])

    for field in required:
        if field not in value:
            errors.append(ValidationError(f"{path}.{field}", "missing required field"))

    if rules.get("additionalProperties") is False:
        allowed = set(properties)
        for field in value:
            if field not in allowed:
                errors.append(ValidationError(f"{path}.{field}", "unexpected field"))

    for field, child_rules in properties.items():
        if field in value and isinstance(child_rules, dict):
            _validate_value(f"{path}.{field}", value[field], child_rules, errors)


def _validate_array(
    path: str,
    value: list[Any],
    rules: dict[str, Any],
    errors: list[ValidationError],
) -> None:
    min_items = int(rules.get("minItems", 0))
    if len(value) < min_items:
        errors.append(ValidationError(path, f"expected at least {min_items} item(s)"))

    item_rules = rules.get("items", {})
    if isinstance(item_rules, dict):
        for index, item in enumerate(value):
            _validate_value(f"{path}[{index}]", item, item_rules, errors)


def _validate_value(
    path: str,
    value: Any,
    rules: dict[str, Any],
    errors: list[ValidationError],
) -> None:
    expected_type = rules.get("type")

    if expected_type == "object":
        if not isinstance(value, dict):
            errors.append(ValidationError(path, f"expected object, got {type(value).__name__}"))
            return
        _validate_object(path, value, rules, errors)
    elif expected_type == "array":
        if not isinstance(value, list):
            errors.append(ValidationError(path, f"expected array, got {type(value).__name__}"))
            return
        _validate_array(path, value, rules, errors)
    elif expected_type == "string":
        if not isinstance(value, str):
            errors.append(ValidationError(path, f"expected string, got {type(value).__name__}"))
            return
        if len(value) < int(rules.get("minLength", 0)):
            errors.append(ValidationError(path, "expected non-empty string"))
        pattern = rules.get("pattern")
        if isinstance(pattern, str) and re.fullmatch(pattern, value) is None:
            errors.append(ValidationError(path, f"expected string matching pattern {pattern!r}"))

    if "enum" in rules and value not in rules["enum"]:
        allowed = ", ".join(str(item) for item in rules["enum"])
        errors.append(ValidationError(path, f"invalid value {value!r}; expected one of: {allowed}"))

    if "const" in rules and value != rules["const"]:
        errors.append(ValidationError(path, f"invalid value {value!r}; expected {rules['const']!r}"))
