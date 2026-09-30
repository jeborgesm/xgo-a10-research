# GBC + GBA golden-architecture propagation candidate

Date: 2026-09-24
Branch: `research-refresh-gbc-gba-golden-propagation`
Status: **GOLDEN — GBC + GBA HARDWARE PASS / BRANCH CLOSED**

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

Initial sections preserve the pre-hardware audit boundary. Subsequent hardware records promote both paths to HW-proven golden status.


## GBC hardware result — PASS

Date: 2026-09-24
Status: **GBC HARDWARE PASS — COMPLETE**

The first GBC hardware test passed on the first candidate. User-confirmed observations:

- a new GBC game was added through the new Refresh path;
- supplied artwork appeared correctly;
- the generated game appeared in the normal GBC list;
- the game launched and was played successfully;
- controller mapping was changed successfully during play, providing an additional runtime/persistence-path regression check.

This hardware result proves the GBC materializer -> explicit catalog merge -> stock GBC launch path on the candidate firmware. It also confirms that the mechanically specialized three-character materializer contract is valid for GBC on XGO hardware.

Second unchanged GBC Refresh was then hardware-tested: the device reported `No New Games` and completed normally. This closes GBC idempotence/no-duplicate behavior on hardware.

GBA remains **OFFLINE AUDITED / NOT YET HW-PROVEN** until its separate test is completed.


## GBA hardware result — PARTIAL PASS / ARTWORK DEFECT ISOLATED

Date: 2026-09-24
Status: **GBA GAME PATH HW PASS; ARTWORK ENRICHMENT FAIL**

A four-game GBA batch was processed in one Refresh invocation. Hardware observations:
- all four games were materialized/listed;
- games launch and play normally through the stock GBA route;
- supplied artwork was not incorporated into the generated wrappers;
- processing four games takes long enough that the unchanged UI gives the appearance of a hang.

Uploaded post-test fixture archive inspection confirms all four generated top-level .zgb wrappers are present together with the original import/, meta/, and art/ inputs. The artwork basenames do **not** exactly match the ROM/meta stems: ROM/meta use scene-style names such as (U) [!], while artwork uses No-Intro-style region strings such as (USA, Europe) / (USA, Australia). This is a concrete candidate root cause for the missing artwork and must be tested against the helper's exact artwork lookup behavior before changing firmware.

Follow-up hardware test corrected the artwork/input naming. Four GBA entries were generated with artwork, listed, launched and played successfully. A second unchanged GBA Refresh returned `No New Games`. Therefore GBA enrichment and idempotence are **HW PASS — COMPLETE**. The earlier missing-artwork observation was test-fixture naming mismatch, not a firmware defect.

### UX follow-up

Refresh currently exposes only final status (Games Updated / No New Games). Batch materialization can therefore look frozen. Add a separate post-GBC/GBA stabilization task to investigate progress feedback using the existing native OSD/text/compositor machinery. Preferred minimum UX is a processing message with current filename or n/N; a progress bar is optional and should not be mixed into the current correctness fix.



## Post-test GBA catalog cleanup — FINAL

Final cleanup was rebuilt from the original uploaded 671-record synchronized GBA triplet. Removed original indices 626..631 (six confirmed leaked GB records) and 663..666 (obsolete first GBA test batch) from all three slots. Index 632, A Sound of Thunder.zgb, is valid GBA content and is preserved. Final output count: 661 synchronized records.

Final cleanup v3 hashes:
- VFNET.TAX: 284379c58bd787d1696b25ba3d1505b4356060b635f9428718b4b83720cc2df0
- HTUIW.NEC: 400f92601286ddd25a6e404c70618901f051ee0cf3f07309ad83fd0d4f17250c
- SPPNP.BVS: 39d8597e28a9da3f9cc8127ff791a43e7833caa4d805d7348e5ccea0424190e2
- cleanup ZIP: 260c6d6922d2b3a2891abe6b49822284dac053f14180c0e68f5c68f980f1e120

## Branch closure

GBC and GBA propagation are complete and HW-proven. The firmware/package identities above are promoted to the golden cumulative Refresh architecture. Normal Refresh remains append-only; standardized deletion/reconciliation remains future work. Batch-processing progress feedback remains a separate UX follow-up.


## 2026-09-29 regression correction — GB catalog pathname terminator overwritten by GBC body

A physical-card forensic snapshot taken after the user observed GB `Refresh Failed` exposed a deterministic regression in the supposedly cumulative GBC/GBA propagation.

Current physical identities:
- `GB/refresh.xgc` SHA-256 `34f4714ecbe5affc97b7a0b87726944c253286c3baa3531e437e982174bda238` — exact GB golden helper.
- `GB/catalog.xgc` SHA-256 `66030c93bfde3e790140265b1123b0ca6cb684efc251a9f602bad480ac7cbbfb` — exact GB golden helper.
- GB triplet remains synchronized at count 975.
- The current firmware's GB command body at `0x80A39050` retains the correct two-stage reachability, including `0x80A3907C -> 0x80A39084`.

The failure is in the firmware pathname storage.

GB catalog pathname begins at `0x80A390E0`:

`/mnt/sda1/GB/catalog.xgc`

That string is exactly **24 bytes**, so its required NUL terminator is at **0x80A390F8**.

The GBC/GBA propagation placed the new GBC command body at **0x80A390F8**. Consequently the first GBC instruction overwrote the GB pathname terminator. On the physical firmware the bytes are:

`... /mnt/sda1/GB/catalog.xgc A4 80 04 3C 60 91 84 24 10 00 ...`

The generic helper runner therefore receives a non-terminated/garbage-extended catalog pathname instead of `/mnt/sda1/GB/catalog.xgc\0`, fails to open the helper, returns negative, and the preserved GB dispatcher correctly reports **Refresh Failed**.

This is not an Arcade/Test17 mutation and not a GB-helper defect. It is a latent cumulative regression introduced when GBC code was allocated at the exact byte required by the protected GB catalog-path terminator. The GBC/GBA finding's earlier statement that GB was byte-identical/fully preserved was therefore incomplete: the GB *code body* was preserved, but an adjacent live GB string datum was not.

### Status correction

The GBC/GBA implementation remains HW-proven for GBC/GBA themselves, but the cumulative-baseline preservation claim is withdrawn until GB is repaired and regression-tested. The superseding physical baseline must not be treated as fully cumulative for GB Refresh.

### Repair gate

Do not change either golden GB external helper. Repair must preserve the existing GB two-stage architecture and current GBC/GBA behavior. Offline work must relocate either the GB catalog pathname or the colliding GBC body into proven-owned space, patch the single corresponding reference, and mechanically audit the current firmware before any hardware request.


## 2026-09-29 deterministic GB pathname repair candidate

The physical failing firmware from the user snapshot was used as the exact repair parent. No GB external helper or catalog resource is changed.

Repair:
- preserve colliding GBC body at `0x80A390F8`;
- relocate the complete NUL-terminated GB catalog pathname to verified zero space at `0x80A398E1`;
- change only the GB catalog-stage pathname low immediate at `0x80A39088`: `0x248490E0 -> 0x248498E1`;
- reseal LCFG CRC-32/MPEG-2.

The destination is the 55-byte zero run `0x80A398E1..0x80A39917`, immediately after the documented GBA body ending at `0x80A398E0`. Required string is 25 bytes and remains wholly inside that verified zero run.

Candidate:
- package `xgo-gb-refresh-path-terminator-repair.zip`
- firmware SHA-256 `3a3206279a1d18ffb6e29b3708383c56cdae11ba89227e078517335c810c3fd0`
- package SHA-256 `6775ed6e3801ca05576fc51a7a9ae6304157e4bf18654c0fff7f3154e76404d2`
- LCFG CRC-32/MPEG-2 `0x38F17EE5`

Hardware question is intentionally narrow: with no GB input/catalog changes, does selecting GB Refresh return `No New Games` rather than `Refresh Failed`? If yes, immediately spot-check GBC and GBA Refresh still return `No New Games`. Arcade is not part of this repair test.


## 2026-09-29 HW result — GB repair passes; GBA regression exposed

Hardware result for the surgical GB pathname repair:
- GB: `No New Games` — **PASS**, the GB `Refresh Failed` regression is repaired.
- GBC: `No New Games` — preserved.
- GBA: `Refresh Failed` — **regression exposed**.
- Arcade: `Refresh Failed` — pre-existing current Arcade state; remains out of this handheld repair scope.
- all other Refresh items tested by user: `No New Games`.

Interpretation boundary: the GB repair itself changed only the GB catalog-path reference plus a relocated pathname and LCFG seal; it did not intentionally modify the GBA command/helper/catalog. Therefore GBA failure must be investigated against the current physical firmware/data before another hardware candidate. Do not reopen Arcade or validator work. Freeze further hardware changes until the GBA path, pathname storage, helper identities, and live-data ownership are mechanically audited for the same class of cumulative cave/string collision.


## 2026-09-29 correction — first GB repair collided with GBA pathname terminator

The first GB pathname repair fixed GB on hardware but caused GBA `Refresh Failed`. Offline comparison of the exact tested repair against the pre-repair physical firmware closes the cause:

- GBA catalog pathname starts at `0x80A398C8`: `/mnt/sda1/GBA/catalog.xgc\0`.
- Its required NUL terminator is exactly `0x80A398E1`.
- The first GB repair selected the apparent zero run beginning at **0x80A398E1** for the relocated GB pathname.
- That repeated the same ownership error: a zero byte was misclassified as free space without accounting for its role as the terminator of the preceding live string.
- Hardware result is therefore fully explained: GB passed after relocation; GBA failed because its catalog pathname became garbage-extended.

This is a repair-construction defect, not a latent GBA baseline defect. Withdraw the earlier interpretation that GBA failure was merely newly exposed. The next repair must restore `0x80A398E1..` padding exactly and place the GB pathname only in a range whose ownership is established independently, not merely because it contains zero bytes.

New invariant: **NUL terminators and alignment/padding adjacent to live path strings are owned data. A zero run is not a code/data cave until predecessor-string ownership and references are audited.**


## Repair v2 — offline closure and hardware gate

The first repair's GBA regression is mechanically closed and corrected without changing any GB/GBC/GBA helper or catalog.

Exact correction from the hardware-tested first repair:
- restore `0x80A398E1..` to its original zeros, restoring the GBA catalog pathname terminator and following padding;
- relocate the complete GB catalog pathname to `0x80A381D8`;
- patch only the GB catalog-path `addiu a0,a0,low` at `0x80A39088` from low immediate `0x98E1` to `0x81D8`;
- reseal LCFG.

Ownership audit for `0x80A381D8..0x80A381FF`:
- the preceding live mode string is `rb\0`, whose terminator at `0x80A381D4` is preserved;
- `0x80A381D8..0x80A381FF` is padding before the generic helper runner beginning at aligned `0x80A38200`;
- the range is zero in both stock firmware and the current tested lineage before repair;
- scan of MIPS absolute jump/JAL and PC-relative branch targets found no target in `0x80A381D4..0x80A38200`;
- the 25-byte GB pathname fits wholly inside the audited padding and cannot touch the runner.

Candidate:
- ZIP `xgo-gb-gba-refresh-path-repair-v2.zip`
- ZIP SHA-256 `0f66812520558d5f4d4597c24418e1db786264e5b57fe9361d1d32e5673400e0`
- firmware SHA-256 `b5f1651b146b52070f2e89d51cc2694852af565150568f78d06404e9f9f461ab`
- LCFG CRC-32/MPEG-2 `0x4AB4C686`.

Hardware gate is bounded to cumulative handheld restoration: GB, GBC, and GBA unchanged Refresh should each return `No New Games`. Arcade remains frozen and is not part of this gate.


## 2026-09-29 HW closure — cumulative handheld Refresh restored

Second repair hardware result:
- GB: `No New Games` — PASS.
- GBC: `No New Games` — PASS.
- GBA: `No New Games` — PASS.
- all other non-Arcade Refresh selectors tested by user: `No New Games` — PASS.
- Arcade: `Refresh Failed` — expected current Arcade/IGS investigation state and explicitly outside this repair.

The v2 repair therefore restores the cumulative non-Arcade Refresh baseline on hardware. The first repair is rejected evidence and must never be promoted.

HW-proven v2 identities:
- package `xgo-gb-gba-refresh-path-repair-v2.zip`
- ZIP SHA-256 `0f66812520558d5f4d4597c24418e1db786264e5b57fe9361d1d32e5673400e0`
- firmware SHA-256 `b5f1651b146b52070f2e89d51cc2694852af565150568f78d06404e9f9f461ab`
- LCFG CRC-32/MPEG-2 `0x4AB4C686`

Promote this exact package/firmware as the new cumulative handheld Refresh golden checkpoint. Arcade remains an independent OPEN subsystem and must resume from the protected Test15 IGS publication/runtime boundary, with validator/preflight redesign still deferred until four-family functionality is established.
