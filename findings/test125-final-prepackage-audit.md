# Test125 final pre-package audit

Date: 2026-09-22
Branch: `research-refresh-gb-gbc-gba`
Status: **OFFLINE CONTROL-FLOW / SOURCE AUDIT CLOSED; package next**

## Scope

Test125 is a deliberately bounded hardware proof of selective handheld
discovery. It is not the finished enrichment implementation. The branch's final
target remains the separately preserved `import/art/meta -> stock wrapper ->
catalog` architecture.

## Stage2 source audit

`tools/game_lists/build_test125_handheld_stage2.py` is a direct readable
reconstruction of the Test07/Test08 stable-merge mechanism at the already
proven Test106 Stage2 execution contract (`0x87180000`, exactly 7000 bytes).

Per-system descriptor values:

| row | directory | names table | count cache | accepted classifier family |
|---|---|---:|---:|---|
| GB | /GB | 0x80A3C374 | 0x80D28964 | wrapper 6 or native 23..25 |
| GBC | /GBC | 0x80A3C38C | 0x80D2896C | wrapper 6 or native 23..25 |
| GBA | /GBA | 0x80A3C3A4 | 0x80D28974 | wrapper 6 or native 20..22 |

The worker:
- reads and validates the selected synchronized triplet;
- scans only the selected physical directory;
- preserves the original filename before the stock extension classifier mutates
  extension text;
- compares exact physical filename against slot 0;
- collects up to 512 missing entries;
- preserves existing records/order;
- appends filename/basename fallbacks;
- constructs all three outputs before canonical writes;
- invalidates only the selected count cache;
- restores the classifier global;
- returns 1 changed, 0 unchanged, -1 failure.

No UI/status renderer and no firmware patching are present in Stage2.

Pinned Stage2 identities:
- GB   `705198908eccb8e828bf4f121d1843bceef0e92a65a5e9a5d988a91e0f40209b`
- GBC  `f31740039e53dbc051e37fa58347577762d1f9d6b27459c75cee5c0bbbb98246`
- GBA  `637c30ed10282e534704631e1261cc9fe9c25e051949271eaee15f9527137cbe`

## Stage1 contract

Each selected `catalog.xgc` remains exactly 2642 bytes, preserving the
boot-sensitive generic-runner size contract recovered from Test106. Stage1
loads its selected `catalog-saf.xgc` at `0x87180000`, performs the inherited
cache maintenance, calls it, and returns the Stage2 result through the ordinary
epilogue rather than the MD-specific marker finalizer.

Pinned Stage1 identities:
- GB   `d41df10bb3e561a18eee6f53ac34170244143b9ca670c8fac43933951916a207`
- GBC  `62de14865f8a14143c7980df0b242f33a5c76cbfe967ef16ff9db367a47ac13f`
- GBA  `dca88ac36235669a0e98a591d145e45b005b58d80221e09b9ae8b4b54a55e3a8`

## Firmware adapter contract

Exact parent is Test123 firmware:
`7becafa3372e7b511bd8f05d0f378ca6397d72c6cc5c075f2e0d650cba2a86b5`.

Test125 firmware output is pinned:
`4e5eb643ede9aa9883fa0ddf5590f92098af4baf369682bfa9ef3d4e185fd6c8`.

LCFG CRC-32/MPEG-2:
`0xB34148B3`.

Adapter routing:
- command 2 -> inherited MD body at `0x80A387AC`;
- command 3 -> `/GB/catalog.xgc`;
- command 4 -> `/GBC/catalog.xgc`;
- command 5 -> `/GBA/catalog.xgc`;
- each handheld helper uses generic runner `0x80A382E0`, size 2642;
- helper result <0 -> native Refresh Failed;
- helper result >=0 -> OR into accumulated change state -> inherited finish block
  `0x80A38808`;
- command 6 -> safe No New Games (Arcade remains intentionally inert);
- command 7 -> unwind, `s5=0`, CLASSIC continuation `0x80A38000`;
- unexpected command -> safe No New Games.

Path literal addresses in emitted firmware:
- GB  `0x80A3913C`
- GBC `0x80A39155`
- GBA `0x80A3916F`

Adapter allocation ends `0x80A39189`, below protected limit
`0x80A391F8`.

## Protected Test123 regions

The deterministic firmware composition asserts these inherited regions remain
byte-identical:
- CLASSIC bootstrap `0x80A38000..0x80A3823F`;
- stock FC/SFC/MD bodies `0x80A386F4..0x80A3883F`;
- selector/Test122 suppression region `0x80A389C0..0x80A3904B`.

## Hardware question

Only one new question is authorized:

> Can the Test08-proven discovery/stable-merge behavior be invoked selectively
> from the Test123 GB/GBC/GBA rows without regressing the cumulative firmware?

The pending raw GBC/GBA Mario ROMs remain untouched as blind evidence.

## After this proof

A PASS does not close the branch. It unlocks propagation of the already
HW-proven Test74/Test75 enrichment contract recorded in
`findings/handheld-stock-enrichment-propagation-contract.md` and
`tools/game_lists/handheld_enrichment_descriptors.py`.

The final handheld Refresh must consume `import/art/meta`, materialize
stock-shaped `.zgb` wrappers with artwork/friendly title, and stable-merge
those wrappers. Bare Test08-style entries are an intermediate diagnostic state.
