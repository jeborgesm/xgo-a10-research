# Test77 — MD native .md + robustness candidate

## Status

**OFFLINE AUDITED / AWAITING HARDWARE**

Test77 follows the failed Test76 diagnostic and remains additive to the hardware-passed Test75 FC baseline.

## Root cause/candidate audit findings

Binary comparison of the Test76 MD materializer against the proven SFC/FC helpers found two concrete Test76 construction defects:

1. the extension comparison had been patched to the artificial three-character `bin` proof gate;
2. one output-root string at helper offset `0x1003` was accidentally left as `/mnt/sda1/FC` instead of `/mnt/sda1/MD`.

The second defect means Test76 was not a clean MD materializer clone and is sufficient reason to reject it regardless of the hardware hang mechanism.

Test77 corrects both items:

- extension comparison now recognizes native `.md` input directly;
- output root is corrected to `/mnt/sda1/MD`.

No FC, SFC, CLASSIC helper or protected baseline file is modified by this correction.

## Candidate identity

- Artifact: `xgo-stock-test77-md-native-md-robustness.zip`
- ZIP SHA-256: `38b4723e4a828f1420e09e4d7fc63a393c33ca8f72a71f7e7604961005f20607`
- MD materializer SHA-256: `03b6402c19288de17700eb92cd209030cfc6eddb077de90db9f54b4ff7292651`
- Firmware SHA-256: `11f2faf849570ea9dc9572e86a536636ef6937dbac7fa0b85a3abc92769823b7`
- FC materializer remains `8b9607e51e4ad24cf19b92dc356f065d57081eaf93d722ccd9c65c00156fbd4e`
- SFC materializer remains `1c1706dc1974f48eb6ab8b4598f866ac74992342e2e0885c5509c5edb8fe2dde`
- ZIP integrity test passed.

## Test contract

Input:

- `/MD/import/<stem>.md`
- `/MD/art/<stem>.jpg` or `.jpeg`
- `/MD/meta/<stem>.txt`

Expected output:

- `/MD/<friendly-or-basename>.zmd`

For the robustness gate, place at least one unrelated unsupported file in `/MD/import` beside the valid `.md` files.

Expected hardware behavior:

1. unsupported file is ignored;
2. valid `.md` games are materialized and cataloged;
3. Refresh returns control to the frontend and reports **Games Updated**;
4. artwork appears and games launch;
5. second unchanged Refresh returns **No New Games** and remains responsive.

If Test77 still hangs, do not promote it. That result would localize the remaining defect downstream of Test76's extension rejection/output-root mistakes and requires another control-flow investigation before propagation.

## Scope boundary

Test77 proves `.md` only. It does not yet claim materialization support for BIN/SMD/GEN/SMS even though the stock MD scanner recognizes that wider family. Broaden only after the native MD path and graceful unsupported-input behavior are hardware-proven.
