# GBC + GBA golden-architecture propagation candidate

Date: 2026-09-24
Branch: `research-refresh-gbc-gba-golden-propagation`
Status: **OFFLINE AUDIT PASS / HARDWARE CANDIDATE — NOT GOLDEN**

## Purpose

Wire GBC and GBA using the architecture closed and hardware-proven by the GB golden checkpoint. This candidate deliberately does not reuse the Test125/Test126 `catalog-saf.xgc` discovery experiment as the implementation.

Runtime contract:

```text
selected handheld command
  -> /<SYS>/refresh.xgc
  -> explicit /<SYS>/catalog.xgc
  -> common native Refresh status/epilogue
```

GB, FC, SFC, MD and CLASSIC are preserved from the validated 2026-09-24 physical SD baseline.

## Parent

Physical baseline firmware:
`b4b1ffa3e92c61d042b77345a21c16d67fcf586c8af6127dbc545997942f5542`

This is the hardware-proven final GB firmware.

## Materializer ancestry

GBC/GBA have three-character raw suffixes (`.gbc`, `.gba`). The implementation therefore uses the exact HW-proven Test75 FC materializer as the byte-level materializer ancestor for its already-proven three-character suffix/stem geometry, while preserving the final GB lifecycle architecture and `.zgb` output contract.

Exact FC ancestor:
`8b9607e51e4ad24cf19b92dc356f065d57081eaf93d722ccd9c65c00156fbd4e`

Mechanical specialization only:
- output wrapper suffix: `.zfc -> .zgb`;
- source suffix predicate: `.nes -> .gbc` or `.gba`;
- source/root/art/meta paths: `FC -> GBC` or `GBA`;
- longer system paths are relocated into the helper's proven zero tail beginning at `+0x1100`, and every code reference to the old path addresses is retargeted;
- JPEG/RGB565/WQW writer machinery is unchanged;
- three-character suffix geometry remains the Test75 value (`+0x009C = 0x05`, stem adjustment `+0x0DF8 = 0xFB`).

Result:
- GBC `refresh.xgc`: `ba6ec026370a4cc72d559061ac86b350554ae2427353e5ed44567868f2733a0d`
- GBA `refresh.xgc`: `b0ff7b7dfd0d5066d7cf310ea96a1e74eef4aa5052b2aa99fc3a57015f07e0fe`
- each is exactly 1,056,520 bytes.

## Explicit catalog merge

Both catalog helpers are mechanically specialized from the final HW-proven GB 2,642-byte explicit merge helper:
`66030c93bfde3e790140265b1123b0ca6cb684efc251a9f602bad480ac7cbbfb`.

The `.zgb` predicate is unchanged.

GBC:
- root `/GBC`
- triplet `pnpui.tax / wjere.nec / mgdel.bvs`
- count cache `0x80D2896C`
- SHA `b6dd0483764faad2feef2a5d7cdea45a94d99b402304c77ec6572bf6bd6a71f8`

GBA:
- root `/GBA`
- triplet `vfnet.tax / htuiw.nec / sppnp.bvs`
- count cache `0x80D28974`
- SHA `db7c1173f5b98adb3506b2676a035ba6e54b35a4391709cbbcd7ad92b983cbc6`

Baseline catalog coherence:
- GBC triplet: 958 / 958 / 958 records; sizes 30,504 / 22,618 / 10,779 bytes.
- GBA triplet: 632 / 632 / 632 records; sizes 22,935 / 18,379 / 8,319 bytes.
All are well below the 65,536-byte helper ceiling and have substantial append headroom.

## Dispatcher reachability audit

The final GB command-3 body at `0x80A39050` is byte-identical and untouched.

New GBC body:
- entry `0x80A390F8`
- materializer path `/mnt/sda1/GBC/refresh.xgc`
- materializer byte count `0x101F08`
- catalog path `/mnt/sda1/GBC/catalog.xgc`
- catalog byte count 2642
- both calls use generic runner `0x80A382E0`
- negative return -> existing failure path `0x80A3882C`
- each successful return is ORed into `s0`
- completion -> existing common status path `0x80A38808`.

New decoder continuation at `0x80A397E0` handles commands 4, 5, 7 and default:
- 4 -> GBC body;
- 5 -> GBA body;
- 7 -> exact CLASSIC unwind + `s5=0` + `0x80A38000`;
- command 6/default -> existing native No New Games path.

New GBA body:
- entry `0x80A39840`
- materializer path `/mnt/sda1/GBA/refresh.xgc`
- catalog path `/mnt/sda1/GBA/catalog.xgc`
- same runner/failure/result/status contract as GB/GBC.

The old command extension changes only at `0x80A38858..0x80A3885F`, replacing the old command-7/default tail with a jump to the new continuation. Commands 0/1/2/3 therefore retain their existing dispatch.

## Mechanical preservation audit

Compared against the exact GB golden firmware, every changed firmware byte is confined to:
- LCFG CRC field;
- `0x80A38858..0x80A3885F` command-extension continuation;
- previously zero `0x80A390F8..0x80A391F7` GBC cave;
- previously zero `0x80A397E0..0x80A39917` GBC/GBA decoder/body cave.

Audit result:
`287 changed bytes; 0 bytes outside the allow-list`.

Therefore the existing FC, SFC, MD, GB bodies, CLASSIC bootstrap, selector UI, native workspace initialization and protected status/epilogue are byte-identical.

## Candidate identities

Firmware:
`ea442b74bdc07cd5e05ec2de8da5c997848a76ed3125681c1955fbcb29b66152`

LCFG CRC-32/MPEG-2:
`0x0DAD49E7`

Candidate ZIP:
`xgo-gbc-gba-golden-propagation-candidate.zip`

ZIP SHA-256:
`3c8c7829d2aab4fc6050d896f00335adfe40f4115db1fcfe546586404b10dbb1`

ZIP integrity: PASS.

## Hardware gate

Although both routes are wired in one mechanically isolated candidate, validate them sequentially.

### GBC first

Use one previously unindexed GBC fixture:

```text
/GBC/import/<stem>.gbc
/GBC/art/<stem>.jpg       optional but recommended for proof
/GBC/meta/<stem>.txt      optional friendly title
```

First GBC Refresh:
- Games Updated;
- top-level `.zgb` generated;
- friendly title/artwork if supplied;
- entry appears only in GBC;
- launches through stock GBC route.

Second unchanged GBC Refresh:
- No New Games;
- device remains responsive;
- no duplicate.

If GBC fails, stop and do not use GBA as a debugger.

### GBA second, only after GBC passes

Use the equivalent `/GBA/import/<stem>.gba` fixture and repeat the same first-pass/second-pass/launch checks.

After both, spot-check GB and CLASSIC unchanged behavior.

## Evidence boundary

This document is BIN/SRC/offline evidence until hardware results are recorded. Neither GBC nor GBA is golden yet.


## GBC hardware result — PASS

Date: 2026-09-24
Status: **GBC HARDWARE PASS**

The first GBC hardware test passed on the first candidate. User-confirmed observations:

- a new GBC game was added through the new Refresh path;
- supplied artwork appeared correctly;
- the generated game appeared in the normal GBC list;
- the game launched and was played successfully;
- controller mapping was changed successfully during play, providing an additional runtime/persistence-path regression check.

This hardware result proves the GBC materializer -> explicit catalog merge -> stock GBC launch path on the candidate firmware. It also confirms that the mechanically specialized three-character materializer contract is valid for GBC on XGO hardware.

The second unchanged-refresh/idempotence observation has not yet been recorded in this finding and must not be silently inferred.

GBA remains **OFFLINE AUDITED / NOT YET HW-PROVEN** until its separate test is completed.
