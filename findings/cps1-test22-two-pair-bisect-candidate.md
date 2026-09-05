# CPS1 Test22 — 68000 ROM-pair bisection candidate

Purpose: bisect the SFII 68000 program-ROM phase after Test21 proved the stall occurs before the end of that phase.

SFII pinned-driver program ROM order:

1. `sf2e_30g.11e` + `sf2e_37g.11f`
2. `sf2e_31g.12e` + `sf2e_38g.12f`
3. `sf2e_28g.9e` + `sf2e_35g.9f`
4. `sf2_29b.10e` + `sf2_36b.10f`

All eight are 0x20000-byte CPS1 68000 byteswapped program ROMs.

Test22 forces `return 1` after pair 2 completes (`i == 4`) and before pair 3 begins.

No trace calls and no filesystem I/O.

Interpretation:
- `Loading..... -> black screen -> freeze`: pairs 1-2 completed; stall is in pairs 3-4.
- remains on `Loading.....`: stall is in pairs 1-2.

Commits:
- Test21 hardware result: `b3a348764a6a954dcde5dc3625ad1a1ea2e93c85`
- Test22 patch: `5f3f8d5320310551820145715727ad4b1fe1fa5e`
- Test22 workflow: `12609732a3726a111460457d4d4b5fa60d0f08ac`

GitHub Actions:
- run `33974034773`
- artifact `9971776852`
- build result: success

Packaged candidate:
`xgo-core3-cps1-test22-two-pair-bisect-v19-snes.zip`

ZIP SHA-256:
`784e19c8dc2f34e888bc74fb9ffd24a34d59974a9f8378321ba0a2175f1c3191`

CPS1 core SHA-256:
`768678d5ff39b1f4570fdbd13f518e07f5ce22d6c5046c6cbe1f855640db19b0`

Package is based on the exact uploaded protected Test17 SD package. Only `cores/fbalpha2012_cps1/core.xgc` changes, aside from candidate README/manifest metadata.
