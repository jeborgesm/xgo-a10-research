# Test125 hardware candidate emission

Date: 2026-09-22
Branch: research-refresh-gb-gbc-gba

Candidate:
`xgo-test125-gb-gbc-gba-test08-selective-discovery-HARDWARE-CANDIDATE.zip`

ZIP SHA-256:
`f3e4498237bb7c191b02581f7e0db2aa6bc1d03ed76ada1ed32ba5f22f0b1d12`

Exact parent Test123 firmware:
`7becafa3372e7b511bd8f05d0f378ca6397d72c6cc5c075f2e0d650cba2a86b5`

Emitted Test125 firmware:
`4e5eb643ede9aa9883fa0ddf5590f92098af4baf369682bfa9ef3d4e185fd6c8`

LCFG CRC-32/MPEG-2:
`0xB34148B3`

The six handheld helpers were independently emitted by GitHub Actions run
`35805742400`, artifact `10727792884`, and matched all pinned source hashes.
The firmware was composed locally from the exact preserved Test123 parent using
the source-controlled deterministic Test125 adapter contract and matched the
pinned firmware SHA/CRC exactly.

SD payload:
- `bios/bisrv.asd`
- `GB/catalog.xgc`
- `GB/catalog-saf.xgc`
- `GBC/catalog.xgc`
- `GBC/catalog-saf.xgc`
- `GBA/catalog.xgc`
- `GBA/catalog-saf.xgc`

No CLASSIC helper/core is included because Test125 inherits the existing
Test123/Test72 CLASSIC installation already present on the test SD. This
candidate does not replace or modify it.

Hardware question remains bounded: can Test08-style raw discovery be invoked
selectively for GB/GBC/GBA from the Test123 selector?

Recommended sequence:
1. install candidate over the existing cumulative Test123 SD;
2. boot;
3. run GBC Refresh once; pending raw Mario should appear and status should be
   Games Updated;
4. launch it;
5. run GBC Refresh once again; expect No New Games and responsive UI;
6. repeat for GBA;
7. optional unchanged GB run should return No New Games;
8. verify CLASSIC still launches.

Do not repeatedly spam Refresh.

PASS does not close the branch. It unlocks the already recorded Test74/Test75
`import/art/meta -> .zgb -> catalog` enrichment propagation.
