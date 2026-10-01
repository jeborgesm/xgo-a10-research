# Test28 — NeoGeo canonical stage-fit candidate

Date: 2026-09-30
Status: OFFLINE AUDITED / HW CANDIDATE

## Correction
The earlier experimental .r package is withdrawn and is not part of the lineage.
Test27 remains the last legitimate HW observation.

## Root cause candidate
HW-working CPS1/CPS2/IGS construct the canonical .refresh-set marker from a
literal adjacent to the normal 0x258C region and scratch at 0x25E8.

NeoGeo's canonical string:
`/mnt/sda1/ARCADE/NEOGEO/.refresh-set/\0`
is 38 bytes. Starting at 0x258C it does not fit before the next live literal at
0x25B0, which forced the Test15 NeoGeo specialization to relocate only the
source string to 0x3000. Tests23-27 then varied relocation/scratch details
without restoring the working family geometry.

Offline byte audit found the preceding `.zip\0` ends at 0x2588. Therefore
0x2589..0x25AF provides 39 bytes, enough for the full 38-byte canonical NeoGeo
path while retaining the original 0x25E8 scratch and initialization.

## Candidate
Parent: exact HW Test21 package SHA
`f7c46930e313d02938d67bff390874dbede5a4ae8bf5bd4130b26326f7cfb03a`

Only executable changed:
`ARCADE/NEOGEO/refresh.xgc`

Parent helper:
`b8d7e99637dea8f217e062040a4550283f7542b040232e20ad54526115a36a9f`

Candidate helper:
`0f411226154475530010071bca261c4dcc52b10fb258c043d89be029ea2ebe81`

Changes:
- canonical .refresh-set source inserted at 0x2589;
- 0x21D8 `addiu a2,a2,0x3000` -> `addiu a2,a2,0x2589`;
- obsolete source literal at 0x3000 cleared.
- no firmware change;
- no catalog helper change;
- no directory-topology change;
- no scratch relocation;
- no scratch-init change;
- no marker algorithm/control-flow change.

Mechanical comparison 0x21C0..0x224F against HW-working IGS leaves exactly
one normalized difference: source pointer 0x2589 versus IGS 0x258C.

ZIP SHA-256:
`8ad2f19c06194ce81f00321f90fa192fb89156b7d86b1d9f2e3c03d9b71b88f6`

## HW setup
Preserve `/ARCADE/NEOGEO/.refresh-set/` directory.
Remove only top-level `/ARCADE/Baseball Stars Pro.zfb` and, if present,
`/ARCADE/NEOGEO/.refresh-set/Baseball Stars Pro.zfb`.
Preserve import/bstars.zip, meta/bstars.txt, art/bstars.jpg.

Expected first Refresh: Games Added/Updated and Baseball Stars Pro published.
Expected second unchanged Refresh: No New Games.
