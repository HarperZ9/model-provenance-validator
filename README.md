# model-provenance-validator

`model-provenance-validator` validates compact JSON envelopes that describe
where model reference claims came from and how they were checked.

The package has no runtime dependencies. It includes a small schema validator
for the envelope shape used by the CLI.

Use it when a README, report, model card note, release packet, or AI workflow
claim needs a small provenance envelope before the claim is repeated publicly.

## Install

```bash
python -m pip install model-provenance-validator
```

For local development:

```bash
python -m pip install -e ".[test]"
python -m pytest
```

## Usage

```bash
model-provenance-validator envelope.json
model-provenance-validator envelope.json --json
model-provenance-validator *.provenance.json --summary
model-provenance-validator *.provenance.json --summary --json
model-provenance-validator *.provenance.json --proof-packet
model-provenance-validator *.provenance.json
```

The command exits with status `1` when any envelope fails validation. Malformed
or unreadable envelope files are reported as invalid results so batch runs can
continue and produce a complete action list.

Use a custom schema:

```bash
model-provenance-validator envelope.json --schema schema.json
```

Run the bundled example:

```bash
model-provenance-validator examples/envelopes/release.provenance.json
```

## Envelope shape

Required top-level fields:

- `envelope_version`
- `subject`
- `source`
- `references`
- `validation`

Allowed `source.kind` values:

- `official-doc`
- `paper`
- `release-note`
- `local-fixture`
- `other`

Allowed `validation.status` values:

- `verified`
- `partial`
- `unknown`

## Minimal valid envelope

```json
{
  "envelope_version": "1",
  "subject": "public-surface-sweeper README claim",
  "source": {
    "name": "public-surface-sweeper README",
    "kind": "release-note"
  },
  "references": [
    {
      "name": "Repository README",
      "locator": "https://github.com/HarperZ9/public-surface-sweeper",
      "retrieved_at": "2026-06-13"
    }
  ],
  "validation": {
    "status": "verified",
    "notes": "Claim checked against the public README surface."
  }
}
```

## Example text output

```text
release.provenance.json: valid
draft.provenance.json: invalid
  $.references: expected at least 1 item(s)
```

## Example JSON output

```json
[
  {
    "path": "release.provenance.json",
    "valid": true,
    "errors": []
  }
]
```

## Example summary output

```text
total: 3
valid: 2
invalid: 1
error_count: 1
action_items:
- draft.provenance.json: resolve 1 validation error(s)
```

## Proof-surface packet output

Use `--proof-packet` when provenance validation should feed `repo-proof-index`
or a release-readiness report. The packet follows the shared proof-surface
interop shape: claims, checks, and action items in one JSON object. The generated
packet is self-checked before printing so producer drift fails before entering
the pipeline.

```bash
model-provenance-validator *.provenance.json --proof-packet > provenance.packet.json
repo-proof-index provenance.packet.json --summary
```

## What it validates

- required fields;
- JSON object and array shape;
- non-empty string fields where required;
- exact constants such as `envelope_version: "1"`;
- enum values for source kind and validation status;
- unexpected fields when `additionalProperties` is false.

## What it does not do

- It does not fetch the referenced source.
- It does not decide whether the underlying claim is true.
- It does not prove a model is safe.
- It does not certify provenance.
- It does not replace human review of the referenced material.

## Release-readiness use

`model-provenance-validator` is the provenance-envelope point in a proof-surface
pipeline:

```text
claim -> source reference -> provenance envelope -> validation result -> proof index
```

Its job is to keep model/reference claims from floating without a source,
retrieval date, and validation status.

## Authorship

Created and maintained by Zain Dana Harper. Claude Code contributed to the
initial implementation.
