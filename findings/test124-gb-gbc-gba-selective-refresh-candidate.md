# Test124 — GB/GBC/GBA individual native Refresh candidate

Date: 2026-09-21
Status: OFFLINE AUDITED — hardware candidate

## Parent

Exact HW-proven Test123 firmware:
`7becafa3372e7b511bd8f05d0f378ca6397d72c6cc5c075f2e0d650cba2a86b5`.

## Change

Only the Test123 command extension allocation `0x80A38840..0x80A388FF` is replaced.

The 180-byte Test124 adapter implements:
- command 2 -> unchanged existing MD path;
- command 3 -> native scanner `0x807DAE4C(a0=3)` -> GB;
- command 4 -> native scanner `0x807DAE4C(a0=4)` -> GBC;
- command 5 -> native scanner `0x807DAE4C(a0=5)` -> GBA;
- command 6 -> native No New Games; Arcade remains deliberately inert;
- command 7 -> exact Test123 CLASSIC semantics.

For 3/4/5, scanner return maps through native Refresh status:
- `v0 < 0` -> `0x807DB718` Refresh Failed;
- `v0 == 0` -> `0x807DB6EC` No New Games;
- `v0 > 0` -> `0x807DB6C0` Games Updated.

Before every native status/CLASSIC exit, the selective dispatcher's local frame is explicitly unwound, restoring `ra`, `s0`, and `sp`. The outer native Refresh frame/workspace remains intact.

## Offline invariants

Verified against the exact Test123 binary supplied from the hardware-tested SD:
- parent SHA exact;
- free Test123 extension tail exact before use;
- FC/SFC/MD bodies unchanged;
- CLASSIC bootstrap `0x80A38000..0x80A3823F` unchanged;
- Test122/Test123 state-14 UI region unchanged;
- path strings/data beginning `0x80A38900` unchanged;
- adapter ends before `0x80A38900`;
- LCFG independently resealed and recomputed.

## Candidate identity

Firmware SHA-256:
`9b007455642c4a5ac9f2cf05b5304cdcc5a6f223f8eefc043966205cbcb6ebdc`

LCFG CRC-32/MPEG-2:
`0x01D2D7DD`

Firmware-only ZIP SHA-256:
`7f8f73018a32522bf7f93c56756042f0f3598ad4eade590c03affb9cbbbdb52d`

Deterministic source:
`tools/refresh_selector/build_test124_from_test123.py`.

## Hardware test order

First, with current SD unchanged:
1. GB -> expect No New Games if its physical directory/catalog is already converged.
2. GBC -> same.
3. GBA -> same.
4. verify Refresh Games can reopen after each operation.
5. verify CLASSIC still behaves as Test123.
6. verify normal Setup/B behavior remains responsive.

If those pass, perform a controlled addition:
- place one accepted, previously unindexed ROM in exactly one target directory;
- invoke only that row;
- expect Games Updated;
- verify only that system gains the entry;
- launch it;
- second unchanged invocation -> No New Games.

Do not test Arcade as an implemented operation; Test124 intentionally leaves command 6 inert.
