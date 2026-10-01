# Arcade Test28 — NeoGeo stage-fit hardware PASS

Date: 2026-09-30
Branch: `research-arcade-refresh-four-family`

## Result — HW

Candidate:
`xgo-arcade-neogeo-stage-fit-test28.zip`

ZIP SHA-256:
`8ad2f19c06194ce81f00321f90fa192fb89156b7d86b1d9f2e3c03d9b71b88f6`

NeoGeo `refresh.xgc`:
- size: 1,056,520 bytes
- SHA-256: `0f411226154475530010071bca261c4dcc52b10fb258c043d89be029ea2ebe81`

Parent materializer was the exact Test15/Test21 NeoGeo helper:
`b8d7e99637dea8f217e062040a4550283f7542b040232e20ad54526115a36a9f`.

User hardware observation:
- NeoGeo Refresh returned **Games Added**.
- **Baseball Stars Pro** was added to the NeoGeo list.
- Correct image/artwork appeared.
- The generated game launched and ran successfully.

This closes the NeoGeo publication defect and completes HW proof for Arcade family Refresh across CPS1, CPS2, IGS and NeoGeo.

## Root cause — BIN + HW

The canonical publication path is:

`/mnt/sda1/ARCADE/NEOGEO/.refresh-set/`

including NUL it requires 38 bytes.

The ordinary family-local literal location used by the working CPS1/CPS2/IGS helpers had been treated as beginning at `+0x258C`, leaving only 36 bytes before the next live literal at `+0x25B0`. NeoGeo was therefore relocated to `+0x3000`. That relocation was the unique structural divergence in the marker-construction path.

Offline byte audit found that the preceding `.zip\0` literal ends at `+0x2588`; therefore `+0x2589..+0x25AF` supplies 39 usable bytes. The full 38-byte canonical NeoGeo path fits there without moving scratch storage or changing the filesystem contract.

Final patch:
- store canonical NeoGeo `.refresh-set/` literal at helper `+0x2589`;
- `+0x21D8`: `addiu a2,a2,0x3000` -> `addiu a2,a2,0x2589`;
- clear obsolete relocated literal at `+0x3000`;
- preserve scratch at `+0x25E8`, including its original initialization;
- preserve marker append logic, fopen/fclose logic, catalog helper, and firmware.

After normalization, the marker block `+0x21C0..+0x224F` matches the HW-working IGS control except for the expected family-specific literal pointer (`0x2589` NeoGeo vs `0x258C` IGS).

## Corrections / rejected line

Tests23–27 remain negative evidence. Scratch relocation, shortened `.r` namespace, and related marker micro-patches are rejected and are not part of the golden architecture. The briefly produced `.r` Test28 draft was withdrawn before hardware and is not an experimental result.

The golden topology remains uniform:
- `/ARCADE/CPS1/.refresh-set/`
- `/ARCADE/CPS2/.refresh-set/`
- `/ARCADE/IGS/.refresh-set/`
- `/ARCADE/NEOGEO/.refresh-set/`

## Golden promotion

Test28 is promoted to the Arcade/NeoGeo golden publication checkpoint. Future work must preserve the canonical four-family topology and this stage-fit geometry.