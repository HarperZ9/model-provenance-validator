# model-provenance-validator

`model-provenance-validator` validates compact JSON envelopes that describe
where model reference claims came from and how they were checked.

The package has no runtime dependencies. It includes a small schema validator
for the envelope shape used by the CLI.

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
```

The command exits with status `1` when any envelope fails validation.

## Authorship

Created and maintained by Zain Dana Harper. Claude Code contributed to the
initial implementation.

