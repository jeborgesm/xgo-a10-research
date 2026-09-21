# Test80 — corrected MD dispatcher no-op bisect

## Status

**OFFLINE AUDITED / AWAITING HARDWARE**

Instruction-level comparison of Test79 against exact Test75 exposed a deterministic construction error in the Test79 diagnostic itself.

## Test79 root cause

At runtime `0x80A38540`, Test79 used:

`j 0x80A38598`

The intended continuation jump is actually at `0x80A38594`:

- `0x80A38594: j 0x807DB5CC` — stock Refresh scanner continuation
- `0x80A38598: nop` — its delay slot
- `0x80A3859C: j 0x807DB718` — Refresh Failed trampoline

By landing on `0x80A38598`, Test79 skipped the continuation jump, executed its NOP, then fell directly into the failure trampoline. Thus the observed **Refresh Failed** result was deterministic and does not demonstrate a dispatcher-state failure.

## Test80 correction

Test80 is Test79 with only the bypass jump corrected (plus the required firmware CRC and README):

- old instruction at file offset `0xA38540`: `0x0828E166` -> `j 0x80A38598`
- new instruction: `0x0828E165` -> `j 0x80A38594`

No MD helper is loaded/called and the added MD stage performs no filesystem work. Existing staged MD files and `ignore_file.xyz` remain an inert control fixture.

## Identity

- ZIP: `xgo-stock-test80-md-dispatcher-noop-corrected.zip`
- ZIP SHA-256: `adee48faaa01a3e7c63379f129774a303f5264739f0b8134d5c1db53b75aee9c`
- firmware SHA-256: `f4590d483ee255250e255ad4b5294807b2250b259887d515611fe25768552cbd`
- firmware CRC-32/MPEG-2: `0x1E585E6E`
- ZIP integrity passed.

## Expected hardware result

With the unchanged controlled SD-card fixture: **No New Games**, frontend responsive.

If Test80 passes, Test79 is explained completely by its off-by-one-instruction branch target and the investigation returns to the Test78 finding: adding the MD external-helper load/call boundary causes the freeze.
