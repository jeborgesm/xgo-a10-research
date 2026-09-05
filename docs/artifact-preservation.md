# Binary Artifact Preservation

## Why this exists

The public research repository intentionally does not contain proprietary XGO firmware binaries. That protects the repository, but hashes alone are not enough to reconstruct a hardware-confirmed build if the researcher's local copy is later deleted.

The project therefore uses two repositories with different responsibilities:

```text
jeborgesm/xgo-a10-research      public
  source, patchers, findings, manifests, hashes, reproducibility

jeborgesm/xgo-a10-artifacts     PRIVATE
  exact hardware-tested ZIPs and proprietary binary payloads
```

The private repository is the durable binary vault. It must never be made public.

## Golden artifact rule

A candidate is promoted to **golden** only after a physical-device PASS.

For every golden artifact preserve:

1. the exact user-tested ZIP, byte-for-byte;
2. SHA-256 of the ZIP;
3. SHA-256 and size of every ZIP member;
4. the firmware SHA-256;
5. the public research commit/PR documenting the hardware result;
6. the parent/protected baseline from which it was composed;
7. a short hardware observation;
8. a stable private-vault filename.

Failed experiments may be kept temporarily but are not required to become golden artifacts.

## Canonical filenames

Use stable names without browser-added suffixes such as `(1)`.

Example:

```text
xgo-cps1-scheduler-v1-on-snes-test02.zip
```

The original local filename is irrelevant once the SHA-256 matches the manifest.

## Public manifest

`artifacts/golden-artifacts.json` is the authoritative public index.

It contains no proprietary bytes. It records identity, provenance, protected-baseline relationships, and the intended private-vault path.

A future handoff should identify a baseline by artifact ID rather than expecting the researcher to remember a filename.

Example:

```text
protected_baseline: cps1-scheduler-v1-on-snes-test02
firmware_sha256: 913647...
```

## Private vault layout

Recommended private repository:

```text
golden/
  mapper-v19/
    xgo-interactive-mapper-v19-card.zip
  snes-test02/
    xgo-native-snes-core2-test02-v19.zip
  cps1-scheduler-v1/
    xgo-cps1-scheduler-v1-on-snes-test02.zip
```

Do not unpack the canonical ZIP in the vault. The ZIP itself is the preserved artifact.

## Verification

Use:

```text
python tools/artifacts/verify_golden_artifact.py \
  artifacts/golden-artifacts.json \
  cps1-scheduler-v1-on-snes-test02 \
  path/to/xgo-cps1-scheduler-v1-on-snes-test02.zip
```

The verifier checks the ZIP hash, exact member set, member sizes, and member SHA-256 values.

## Promotion workflow

When hardware confirms a candidate:

```text
hardware PASS
  -> normalize artifact filename
  -> hash ZIP and every member
  -> add/update golden-artifacts.json
  -> upload exact ZIP to private xgo-a10-artifacts vault
  -> commit finding + manifest update
  -> HANDOFF-CURRENT references artifact ID
```

This makes artifact preservation part of branch closure rather than an optional cleanup step.

## Important privacy rule

GitHub Release assets on a public repository are public. Do not upload XGO firmware to a Release on `xgo-a10-research`.

The binary vault itself must be private.
