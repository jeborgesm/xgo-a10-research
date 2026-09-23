# Test127 — GB enrichment from proven ancestors

Date: 2026-09-23
Status: **OFFLINE AUDIT PASS / HARDWARE CANDIDATE**

Test127 is the first GB candidate on this branch that implements the requested
finished architecture rather than raw-ROM discovery.

## Proven ancestry

- firmware/UI/lifecycle parent: exact HW-pass Test123;
- materializer parent: exact HW-pass Test97 MD `refresh.xgc`;
- catalog parent: exact HW-pass Test75 FC / Test74 SFC explicit catalog merge;
- CLASSIC path remains Test123;
- GBC/GBA/Arcade remain inert.

## GB materializer

Input:
`/GB/import/<stem>.gb`

Optional:
`/GB/art/<stem>.jpg|jpeg`
`/GB/meta/<stem>.txt`

Output:
`/GB/<friendly-or-basename>.zgb`

SHA-256:
`00addd59c2b3305e936021bb6cb7c66e03cac334816cd2a61e5c216315e19810`

Only 18 bytes differ from exact Test97 MD materializer. Test97 short-extension
NOP at helper offset `0x027C` is preserved. JPEG/RGB565/WQW machinery is unchanged.

## GB catalog helper

Derived mechanically from exact Test75 FC helper.

Contract:
- filter `.zgb`;
- root `/GB`;
- triplet `vdsdc.tax / umboa.nec / qdvd6.bvs`;
- GB count cache `0x80D28964`;
- stable append, synchronized triplet, no deletion/resort.

SHA-256:
`66030c93bfde3e790140265b1123b0ca6cb684efc251a9f602bad480ac7cbbfb`

## Firmware adapter

Command 3 now executes, under the already-valid native Refresh frame/workspace:

```
GB/refresh.xgc
  -> generic runner 0x80A382E0
  -> if failure: native Refresh Failed
  -> accumulate changed
GB/catalog.xgc
  -> same runner
  -> if failure: native Refresh Failed
  -> accumulate changed
  -> existing common Games Updated / No New Games status tail
```

The GB body is placed at `0x80A39050`, after the protected Test122 suppression
helper ending at `0x80A39047`. Its path strings are at `0x80A390C0` and
`0x80A390E0`. The exact Test123 input region `0x80A39048..0x80A391F7`
was verified zero before use.

Command policy remains:
- 0 FC existing proven body
- 1 SFC existing proven body
- 2 MD existing proven body
- 3 GB **new Test127 body**
- 4 GBC inert / No New Games
- 5 GBA inert / No New Games
- 6 Arcade inert / No New Games
- 7 CLASSIC exact Test123 continuation

## Exact identities

Firmware:
- SHA-256 `490939aaacd210d78b667057a604414e840fdb5981d6cf5ba1305612131a917f`
- LCFG CRC-32/MPEG-2 `0x1E8CE898`

Candidate ZIP produced in the working session:
- `xgo-test127-gb-enrichment-proven-ancestry-HARDWARE-CANDIDATE.zip`
- SHA-256 `30a772b6f32e1460f88d5fd78c7ebb56f23338a86005593d528e2c09c8d770e5`
- ZIP integrity: PASS

Deterministic source:
`tools/game_lists/build_test127_gb_enrichment.py`

## Hardware test

Use one new GB fixture that is not already cataloged:

```
/GB/import/<stem>.gb
/GB/art/<stem>.jpg
/GB/meta/<stem>.txt
```

First Refresh Games -> Game Boy:
- expected Games Updated;
- generated top-level `.zgb`;
- friendly title visible;
- artwork visible;
- launch/play through stock GB route.

Second unchanged Game Boy Refresh:
- expected No New Games;
- responsive;
- no duplicate entry.

Also spot-check CLASSIC after GB to ensure Test123 routing remains intact.

Do not test GBC/GBA with this candidate; those commands are intentionally inert.
