"""Generic JSON Schema validator with cross-file $ref resolution.

Schema-agnostic — caller supplies the schema path. Works for any routine.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema
from referencing import Registry, Resource


class ValidationError(ValueError):
    """Raised when a payload fails schema validation."""


def validate(
    payload: dict[str, Any],
    *,
    schema_path: str | Path,
    schemas_dir: str | Path | None = None,
) -> None:
    """Validate `payload` against the schema at `schema_path`.

    If `schemas_dir` is provided, every `*.schema.json` file in that
    directory is registered under its bare filename so cross-file `$ref`
    pointers resolve.

    Raises:
        ValidationError: if any validation error is detected, with all
            errors joined into the message.
    """
    schema_path = Path(schema_path)
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    if schemas_dir is not None:
        resources = []
        for f in sorted(Path(schemas_dir).glob("*.schema.json")):
            resources.append((f.name, Resource.from_contents(
                json.loads(f.read_text(encoding="utf-8"))
            )))
        registry = Registry().with_resources(resources)
        validator = jsonschema.Draft202012Validator(schema, registry=registry)
    else:
        validator = jsonschema.Draft202012Validator(schema)

    errors = list(validator.iter_errors(payload))
    if errors:
        msgs = [f"{list(e.absolute_path)}: {e.message}" for e in errors]
        raise ValidationError("; ".join(msgs))
