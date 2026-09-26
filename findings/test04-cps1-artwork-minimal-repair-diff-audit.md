# Test04 CPS1 artwork repair — exact binary differential audit

Date: 2026-09-26
Branch: `research-arcade-refresh-four-family`
Status: **OFFLINE BINARY REPAIR AUDITED; NOT A HARDWARE CANDIDATE**

## Parent

Exact physical Test04 CPS1 materializer:
- size `0x101F08` / 1,056,520 bytes
- SHA-256 `301df6494c89928cf615a918b76f81d4c0774d864cd45c77cacc2e145fed3f28`

## Minimal repair

Only the two decoder scratch literals are shortened in place:

```
/mnt/sda1/ARCADE/CPS1/art/.xgo.jpg
 -> /mnt/sda1/ARCADE/.xgo.jpg

/mnt/sda1/ARCADE/CPS1/art/.xgo.rgb565
 -> /mnt/sda1/ARCADE/.xgo.rgb565
```

The source-art paths such as `/ARCADE/CPS1/art/%s.jpg` remain unchanged.

Because the replacement paths are shorter, they fit entirely inside the existing Test04 literal slots; unused suffix bytes are zero-filled. No executable instruction or reference needs to move.

## Offline emitted result

Deterministic patch of the exact Test04 parent produced:
- size: 1,056,520 bytes, unchanged
- SHA-256: `2d6503ae20937bd9d525d68a18ee845d942667b582e71e2371450a83d8d29ad2`
- changed bytes: **37**
- changed runs only:
  - `0x1245..0x1255` — 17 bytes
  - `0x1269..0x127C` — 20 bytes

The earlier bytes in each literal remain identical because both old and new paths share the `/mnt/sda1/ARCADE/` prefix.

## Protected binary invariants

Verified after patch:
- total helper size unchanged;
- JPEG tail `+0x100000..+0x101F07` SHA remains
  `9ca2599d45d5c7cadb4f89064d959f5959fc1de258c4384545353bc796fec136`;
- decoder invocation words at `+0x0730/+0x0734/+0x0738` remain
  `3C198710 / 0320F809 / 00000000`;
- Arcade finalizer splice begins unchanged at `+0x09B4` (first word `8FC40044`);
- no byte outside the two existing scratch-literal slots changes.

## Reproducibility

Source:
`tools/arcade_refresh/repair_test04_cps1_art_scratch.py`

The tool fails closed unless the input size/hash exactly match the physical Test04 CPS1 helper and the golden JPEG tail hash matches before patching.

## Provenance note

The private artifacts repository contains the golden package
`golden/xgo-stock-test75-fc-enrichment-proof.zip`, but the exact Test75 binary is not currently materialized in the local analysis workspace. Therefore this audit deliberately uses the exact physical Test04 helper as its immediate binary parent rather than pretending to perform a fresh Test75 rebuild.

A later full four-family rebuild must still start from the pinned Test75 parent and reproduce the same safe scratch-path rule.

## Gate

This closes the CPS1 artwork repair mechanically. It does **not** authorize Test05 yet.

Independent remaining branch gates include:
- Arcade live-list/frontend lifecycle after catalog mutation;
- integration of the compatibility validator before publication;
- four-family deterministic rebuild/audit from the pinned materializer ancestor.
