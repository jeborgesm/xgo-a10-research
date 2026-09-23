# GB materializer — exact Test97 MD mechanical substitution

Date: 2026-09-22
Branch: `research-refresh-gb-gbc-gba`
Status: **OFFLINE MATERIALIZER DERIVATION ONLY — not a firmware/hardware candidate**

Evidence: HW ancestor + BIN mechanical comparison.

## Exact ancestor recovered

The protected Test106 package carries `MD/refresh.xgc` byte-identical to the
HW-positive Test97 materializer.

- size: 1,056,520 (`0x101F08`)
- SHA-256: `c0af2dea8291f86b411e819356e7b6b877ca69e39a444f0780348906f610e087`

The same package also contains the protected Test75 FC and Test74 SFC helpers:
- FC SHA-256 `8b9607e51e4ad24cf19b92dc356f065d57081eaf93d722ccd9c65c00156fbd4e`
- SFC SHA-256 `1c1706dc1974f48eb6ab8b4598f866ac74992342e2e0885c5509c5edb8fe2dde`

Mechanical comparison confirms MD differs from FC in only 101 bytes / 12
contiguous ranges, overwhelmingly system strings/constants plus the known
short-extension gate.

## Exact MD -> GB materializer substitutions

The first GB helper is a length-preserving derivative of exact Test97 MD:

| helper offset | Test97 MD | GB | purpose |
|---:|---|---|---|
| `0x0114` | high half encoding of `.zmd` | high half encoding of `.zgb` | generated wrapper suffix |
| `0x02A8` | `m` | `g` | source extension char 1 |
| `0x02D4` | `d` | `b` | source extension char 2 |
| `0x0FF2` | `MD` | `GB` | import path |
| `0x100D` | `MD` | `GB` | root path |
| `0x101B` | `MD` | `GB` | temporary JPG path |
| `0x1036` | `MD` | `GB` | temporary RGB565 path |
| `0x1054` | `MD` | `GB` | metadata path |
| `0x1071` | `MD` | `GB` | JPG lookup |
| `0x108A` | `MD` | `GB` | JPEG lookup |

Critical preservation:
- Test97's NOP at `0x027C` remains exactly `00000000`.
- No Test102 stem arithmetic patch is applied.
- JPEG decoder/scaler tail remains byte-identical.
- WQW/package writer remains byte-identical.
- helper size remains exactly `0x101F08`.

The generated wrapper constant is encoded as little-endian `.zgb`; the input
source gate is `.gb`. These are separate contracts.

## Deterministic source

`tools/game_lists/build_gb_refresh_from_test97_md.py`

The builder:
- rejects any input not matching the exact Test97 MD helper hash;
- verifies every expected old byte before patching;
- permits only the enumerated substitutions;
- asserts the Test97 `0x027C` NOP survives;
- fails if any unenumerated byte changes.

Offline derivation from the recovered exact ancestor produced:

- size: 1,056,520
- SHA-256: `00addd59c2b3305e936021bb6cb7c66e03cac334816cd2a61e5c216315e19810`
- changed bytes from Test97 MD: **18**

## Boundary

This closes the **GB materializer** derivation only.

It does NOT yet authorize a hardware candidate. The next component is GB
catalog integration. That component must be selected from the proven enrichment
lineage rather than importing Test124-126 raw-scanner architecture.
