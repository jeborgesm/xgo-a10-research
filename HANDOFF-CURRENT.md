# HANDOFF-CURRENT

## Checkpoint — 2026-09-20 — Test106 closed

The stock-catalog-enrichment cycle has reached a safe closure point. **Test106 is the hardware-proven hardened Mega Drive Refresh baseline.** Preserve all earlier cumulative features and the complete positive/negative experiment record.

### Exact Test106 protected identities

```text
bios/bisrv.asd
SHA-256 b66dbcd86ad785875a6804bb7d07c6eb1195ceedb01c0bce8107f65eee2ab66e
UNCHANGED known-booting Test97/Test105 firmware

MD/catalog.xgc
size 2642
SHA-256 e4c21a94055a6aec817494d2f69450f12fbba3244a91c1b74e73de2a4e91b338

MD/catalog-safe.xgc
size 7000
SHA-256 45b3e2638b27e0d4a3ffa518e359413de619184ea9c93c4a5c83bbbc2e0ac65c

Test106 hardware candidate ZIP
SHA-256 07703312d5a331f2a35f6cc42d44d85d608f33f0cc07335679b9d03ccd46e4d7
```

### Test106 hardware closure

```text
Initial card:
  LIVE 839/839/839 healthy
  stale complete 788 recovery triplet
  no .xgo-cat-state

Install Test106
  -> boot PASS
  -> Refresh: Games Updated
  -> responsive
  -> newer MD game visible
  -> artwork present
  -> launch/gameplay PASS

Passive filesystem capture:
  .xgo-cat-state = exact ASCII "CLEAN!"
  LIVE = coherent known-good 839/839/839
  stale 788 recovery triplet remains physically present

Second Refresh, card otherwise unchanged:
  -> No new games
  -> responsive
```

This proves the logical state gate prevents stale complete backups from causing repeated rollback/rebuild.

### Transaction architecture

```text
              .xgo-cat-state
                    |
          +---------+---------+
          |                   |
       CLEAN!          absent/ACTIVE/
          |               invalid
          |                   |
 ignore stale .bak      recovery preflight
          |                   |
          +---------+---------+
                    |
             normal catalog work

Before destructive LIVE commit:
  validate OLD LIVE
       -> create + byte-verify recovery triplet
       -> write ACTIVE
       -> write LIVE TAX/NEC/BVS
       -> reopen + byte-verify NEW LIVE
       -> write CLEAN!
       -> return
```

Physical deletion of stale backup files is not part of correctness. Test105 proved the intended remove calls could leave the backup triplet present.

### Known healthy MD generations

```text
788:
TAX 22156 d04479d8214233d417ebf1791aa38b030a89b9ee55657c586c997257301bba01
NEC 15984 835be147cfb05da648385667da6ad5c81467a281ecfa8f71d60bf50d01d8197c
BVS  8160 60acca83cbcd3086a1f27c2f9c2f192474759d1711f0adf8c9b9e3419a3bf1a8

839:
TAX 23458 ca552d6c67eef499fa8d26dff532e75827947ae0230521db7d420d4237b451ee
NEC 17082 44371b1e48c225e4d871a253b4b5c459af42f6c3bf29e269e49c299e3ccdd955
BVS  9258 4617723c68984812d6ee116a2892ee2b845c3b202cfed0512ffb8c45938d62ac
```

### Important negative findings preserved

- Test103 direct native scanner substitution: **NO BOOT**.
- Test104 changed only helper-size immediate 2642 -> 7000: **NO BOOT**. Restoring exact Test97 firmware restored boot. Never casually patch this immediate.
- Test105 recovery works, but stale backup cleanup is unreliable; do not use backup-file absence as transaction state.
- Test106 first offline build had unaligned `CLEAN!` literal at `0x870004AA`; caught before hardware, corrected to aligned `0x870004B8`.
- `0x807D40A8` is remove/unlink-like, not a persistence finalizer.
- `0x80A38000` is **not** a standalone callable CLASSIC entry; Test92 hard-locked.
- Do not hook `0x807DBA6C`.
- Test90/91 guessed first-class REFRESH resource work was unsafe; Test91 demonstrated resource auto-discovery/corruption risk.
- Do not intentionally power-cut during SD writes to prove durability.

Full chronology: `findings/md-refresh-test76-test106-preservation-record.md`.
Source/reconstruction: `tools/game_lists/md/test106/README.md`.

### Source preservation rule

All future generated executable helpers must have a source/reconstruction record committed alongside findings. If a helper is produced by byte patching/hand assembly rather than a conventional compiler, preserve:
- annotated assembly/pseudocode;
- runtime addresses;
- patch offsets/call targets;
- exact input/output hashes;
- build/patch script when available;
- positive and negative hardware outcomes.

Binary-only ZIPs are not sufficient archival source.

### Stock-console regression status

SFC:
- Test74 is independently hardware-proven for multi-entry enrichment, artwork, launch and idempotent Refresh.
- Test106 MD changes do not constitute a new SFC hardware regression test.
- therefore SFC is proven, but a quick post-Test106 launch spot-check would close cumulative regression evidence.

FC:
- Test75 is hardware-proven with a five-game batch;
- all five generated entries launched and ran correctly;
- supported JPG artwork was hardware-proven after correcting an accidental PNG input mistake and regenerating wrappers;
- catalog records remained stable without duplication during the repair workflow;
- standardized deletion/removal remains future work because Test75 merge behavior is append-only.
- Test106 did not directly modify the protected FC helper files, but a fresh post-Test106 FC launch spot-check has not yet been recorded.

GB/GBC/GBA:
- retain generalized scanner history; enrichment propagation remains deferred until after CLASSIC resurface / explicit regression priorities.

### Next branch: CLASSIC Refresh resurface

Start from merged main after this closure.

Goal:
1. resurface CLASSIC as an independent Refresh module using its proven historical invocation contract;
2. preserve Test106 MD transaction hardening untouched;
3. preserve Mapper v19, CPS1 pacing, Audio OSD v8, stock consoles/Arcade, normalized MAME2000 core and CLASSIC Save/Load;
4. do not revive obsolete Pac-Man work;
5. do not use direct `0x80A38000` invocation;
6. after CLASSIC module is stable, proceed toward the proper first-class `REFRESH GAMES` selector:
   Famicom, Super Famicom, Mega Drive, Game Boy, Game Boy Color, Game Boy Advance, Arcade, Classic.
7. No Refresh All.
8. The old Settings-page selector was diagnostic only; do not polish it as final UX.

### OPEN

- actual power-loss/media durability and fsync/writeback semantics;
- hardware proof of interrupted ACTIVE transaction;
- rollback after deliberately induced partial LIVE write.

Leave these OPEN rather than risking SD corruption.



## Checkpoint — 2026-09-20 — CLASSIC Refresh resurface / selector archaeology

Active branch: `research-classic-refresh-resurface`.

### Closed invocation/lifecycle contract

- Native Refresh entry: `0x807DB5CC`; it creates a 0xB0 save frame and initializes scanner workspace before module dispatch.
- CLASSIC bootstrap `0x80A38000` is a continuation under that live native frame, **not a standalone function**.
- Correct CLASSIC-only route after workspace init: `s5=0; j 0x80A38000`.
- Test92 direct arbitrary UI -> `0x80A38000` HARD LOCK is causally explained by missing native Refresh frame.
- CLASSIC helper result maps back into native Games Updated / No New Games / Refresh Failed paths and common native epilogue.

Primary findings:
- `findings/classic-refresh-resurface-invocation-contract.md`
- `findings/native-refresh-lifecycle-classic-adapter-closure.md`

### Selector command ABI and UI architecture

Final command IDs are ephemeral:
```text
0 FC
1 SFC
2 MD
3 GB
4 GBC
5 GBA
6 Arcade
7 CLASSIC
```

Do not overload frontend state `0x80C33980`; 0..11 are catalog states, 12 Favorites, 13 History, 14 User Menu, 15 Search. Do not invent state 16.

Use state 14 as the valid host lifecycle with a transient selector overlay. The selector uses translated frontend events:
```text
UP   0x0010
DOWN 0x0040
A    0x2000
B    0x4000
```

Stock text renderer: `0x803528A4`.
Stock User Menu redraw/re-entry: `0x80359ABC`.
Framebuffer/presentation evidence:
```text
0x80C33364 framebuffer
0x80C3395C width
0x80C33958 height
0x8035C398 run_screen_write
```

State-14 confirm seam: `0x80359E94`.
State-14 navigation terminal sites: `0x80359AA4`, `0x80359E60`.

### Why the Test106 selector is ugly

Exact Test106 firmware is byte-identical to Test85/Test97 and still contains the diagnostic selector.

Test106 globally expanded the stock User Menu from rows 0..2 to 0..3 and routes row dispatch through `0x80A385F0`. Row 3 sets a selector flag, resets selection, then redraws the **same User Menu**; active rows 0..2 become modules and row 3 exits. This is the hacky Settings/User Menu selector being retired.

Useful inheritance: normal User Menu row 3 is already a proven entry seam. Final behavior should be:
```text
stock User Menu -> REFRESH GAMES -> dedicated stock-font 8-row selector
```
Do not retain the diagnostic active presentation.

Finding: `findings/test85-test106-diagnostic-selector-mechanism-closure.md`.

### Exact Test106 cave audit

Exact protected firmware:
```text
size   12,768,452
SHA256 b66dbcd86ad785875a6804bb7d07c6eb1195ceedb01c0bce8107f65eee2ab66e
```

Stable all-zero cave:
```text
0x80A389B8 .. 0x80A391F8
length 0x840 / 2112 bytes
region SHA256 80b67b115f8e28f3b67fddcd4cd1daac24a054603d1dd0cb13793a299a5dadfc
```

The exact region is identically zero in stock, Test75, Test85, Test92, Test97 and Test106. Reserve it as one selector/adapter module. Builder must fail closed on baseline SHA mismatch, nonzero cave byte, patch-site mismatch, or module overflow.

Audit source:
`tools/refresh_selector/audit_test106_selector_cave.py`

Finding:
`findings/test106-selector-cave-byte-audit.md`

### Relevant commits on this branch

```text
a42af42  CLASSIC invocation contract
2fd8c73  native Refresh lifecycle / CLASSIC adapter closure
8a7cff1  Test85 state + new command ABI
53bed68  native menu grammar survey
973d68b  selector input-loop architecture
a9c6619  B/Back input identity closure
a0e3df4  state-14 hosted selector architecture
02cd28e  native text renderer contract
4effb35  Test92 selector state / native Refresh handoff
c92929a  state-14 confirm hook closure
a13c6d0  navigation and repaint closure
1c2db0f  exact Test106 cave byte audit
9dae763  fail-closed cave audit utility
98ea4eb  Test85/Test106 diagnostic selector mechanism closure
```

### Next exact task

Construct the source-preserved replacement selector/adapter module in the verified `0x80A389B8..0x80A391F8` cave.

Requirements:
1. keep normal state-14 behavior untouched while selector inactive;
2. normal User Menu row 3 enters REFRESH GAMES;
3. dedicated stock-font eight-row selector, no custom raster/resource triplet;
4. private `selector_active` + `selected_row`;
5. UP/DOWN wrap 0..7;
6. B cancels to stock User Menu with no Refresh mutation;
7. A hands module ID to native Refresh entry `0x807DB5CC`;
8. post-workspace dispatcher sends CLASSIC via `s5=0; j 0x80A38000`;
9. preserve Test106 MD helper architecture and protected status/logging/Volume OSD;
10. produce source/reconstruction + exact byte-diff manifest before any hardware candidate.

Do not authorize GB/GBC/GBA propagation merely because their selector rows exist; module adapters remain evidence-gated.


## Process correction — 2026-09-21 — source-first gate restored

Test113 is the last positive Refresh-selector hardware checkpoint. Tests114–117 are rejected negative experiments and MUST NOT be used as development bases.

Test113 HW:
- Setup opens;
- clean REFRESH GAMES presentation;
- all eight rows navigate;
- B exits Setup but selector state persists and resurfaces when Setup is reopened;
- selecting a Refresh option closes the selector, demonstrating that a valid close/redraw mechanism already exists in the active selector/confirm lifecycle.

Rejected:
- Test114: assumed B exit seam; no behavioral change.
- Test115: assumed selector-exit helper; no behavioral change.
- Test116: state clear grafted into stock/global B continuation; wrong lifecycle.
- Test117: global interception at 0x80356C68; Setup hard-lock. This violated the documented no-custom/global-B-hook architecture.

Mandatory protocol:
- `docs/MODIFICATION-CONTINUITY-PROTOCOL.md`
- `docs/FAMILY-SOURCE-PROVENANCE.md`

No Test118 is authorized until:
1. the selector-specific B-cancel seam is closed offline from Test106 BIN + repository reconstruction + applicable family source;
2. `selector_module_v0.S` is instruction-pinned rather than leaving the relevant continuation OPEN;
3. `build_selector_candidate.py` becomes the deterministic emitter rather than audit-only;
4. every emitted patch site is fail-closed and documented;
5. a complete byte-diff manifest is reviewed;
6. LCFG reseal is independently verified.

Do not rediscover behavior by mutating Test113. Test ZIPs are evidence artifacts, not source.



## HW Test118 PASS — 2026-09-21

Candidate: `xgo-test118-refresh-B-proven-close-safe-cave-MINIMAL-HARDWARE-CANDIDATE.zip`

Test118 was built from HW-positive Test113, with the selector-aware B helper moved to verified free space beginning at `0x80A38FD0`; Test113's renderer epilogue through `0x80A38FC8` remained byte-identical.

HW result:
- Setup opens.
- Refresh Games opens.
- Pressing B closes Refresh Games and reveals normal Setup.
- Device remains responsive.

Therefore the following is now **HW-proven**:
- selector-active B can invoke the inherited selector-close/redraw transition safely;
- the corrected post-renderer cave allocation is viable;
- the Test116/117 regression was caused by their bad placement/corruption, not by the close semantic itself.

User additionally exercised CLASSIC beyond the intended Test118 scope:
- selecting Classic closed Refresh Games;
- `No New Games` appeared;
- message disappeared after about one second;
- afterward, selecting Refresh Games did not reopen the Refresh list.

Classify that final observation as a new **HW finding**, not a Test118 failure. It indicates selector state/lifecycle after native Refresh completion is still incomplete. Do not patch it by guess. Trace the post-refresh return/redraw/state transition from the native Refresh path before another candidate.

Test118 is now the last HW-positive checkpoint for B-cancel behavior. The next source work must also repair the already-identified Test113 command-dispatch defect where row 3/Game Boy still aliases the inherited diagnostic Back operation.


## HW Test119 PASS — 2026-09-21 — command/re-entry lifecycle closed

Candidate: `xgo-test119-refresh-command-reentry-MINIMAL-HARDWARE-CANDIDATE.zip`

Firmware:
```text
SHA-256 d357a86a79175d7c07877026ccfaa94c352fd571ba7d54b08d1e9acf1cdf4c15
LCFG CRC-32/MPEG-2 0x39A338DE
```

HW result reported by user: **successful test**.

Test119 changes the active A dispatcher so every selector row 0..7 is an individual Refresh command, removes the inherited Test85/Test106 row-3 Back special case, and normalizes the caller's ordinary state-14 selection to row 3 before entering native Refresh.

This closes the Test118 re-entry defect:
- CLASSIC may execute and return through native Refresh status/epilogue;
- the ordinary User Menu caller is left with a valid selection;
- Refresh Games can be entered again;
- Game Boy/row 3 is no longer the old diagnostic Back command.

The B-active close path remains the HW-proven Test118 implementation.

Authoritative source/evidence:
- `tools/refresh_selector/build_test119_from_test106.py`
- `tools/refresh_selector/selector_module_v0.S`
- `findings/refresh-post-operation-reentry-selection-closure.md`
- `findings/refresh-selector-command-and-reentry-closure.md`
- `findings/refresh-selector-b-cancel-and-test117-root-cause.md`

Important correction to older handoff text: the earlier “no Test118 authorized” gate is historical and is superseded by HW PASS Test118 and HW PASS Test119. Likewise, the older blanket prohibition on a custom/global B hook is superseded by the scoped selector-active Test118 hook whose inactive path reproduces stock behavior.

### Current protected selector checkpoint

**Test119 is now the protected HW-positive Refresh selector checkpoint.**

Do not rebuild future work from Tests114–117. Future candidates must be deterministic derivatives of exact Test106 via the source-preserved builder/reconstruction path and must retain:
- Test118 B behavior;
- Test119 unified A row0..7 command semantics;
- caller state-14 selection normalization before native Refresh;
- renderer epilogue through `0x80A38FC8`;
- LCFG reseal validation.

### Refresh All requirement

There is no implicit Refresh All behavior. Each of the eight current rows refreshes only its own system. User approved a future explicit ninth `Refresh All` row after the eight individual paths are stable/closed.


## Current checkpoint — 2026-09-21 — Test122 + CLASSIC rescue priority

Test122 is the current HW-positive selector/UI checkpoint.

Test122 HW result:
- REFRESH GAMES remains responsive;
- all eight rows navigate;
- B closes the selector;
- producer-side suppression removes the underlying stock Setup blue selector border;
- residual OPEN issue: after B, a stale `No New Games` status can remain on ordinary Setup until another option is selected.

Test122 firmware SHA-256:
`6378e4a9cbf560afa53c38836826c294c9b2316310d65eb9860894c221cb2f0d`
LCFG CRC: `0x0EFF6110`
ZIP SHA-256: `21c3b9e6c871e67d85e334154b7157e12597f918911a76acc5932faa0647c78d`

Rejected presentation experiments:
- Test120 HW FAIL: full-screen memset/footer approach;
- Test121 HW FAIL: expansion of inherited repaint loop to 640x480.
Do not reuse these approaches. Test122 instead suppresses the native state-14 172x172 selector compositor while Refresh Games is active.

### Exact command-wiring correction

The current Test122 UI captures commands 0..7, but the inherited Test85/Test97 execution dispatcher is only three-way:
- 0 -> FC;
- 1 -> SFC;
- every other value -> MD.

Therefore only FC/SFC/MD labels currently match execution. GB/GBC/GBA/Arcade/Classic currently alias MD. Earlier interpretation of Test118 Classic -> `No New Games` as proof of CLASSIC execution is retracted; command 7 fell through to MD.

### Priority now

1. Rescue CLASSIC first.
2. Then wire GB/GBC/GBA.
3. Treat Arcade separately because stock UI/catalogs are CPS1/CPS2/NeoGeo/IGS (lists 7..10) sharing /ARCADE; the single Arcade row must eventually orchestrate/classify across those pages.
4. Explicit ninth `Refresh All` remains a later requirement after all eight individual operations are stable.

CLASSIC is a restoration, not a new scanner. Protected mature lineage: Test47 generalized importer, Test60 external helper, Test64 JPEG conversion, Test72 50-game batch and unchanged second Refresh -> No New Games. Safe invocation remains native Refresh frame/workspace first, then `s5=0; j 0x80A38000`. Never call `0x80A38000` standalone.

Current CLASSIC rescue gate: resolve the documented Test72 `CLASSIC/refresh.xgc` hash discrepancy against the actual artifact before packaging Test123. See:
- `findings/test122-individual-refresh-command-wiring-audit.md`
- `findings/refresh-wiring-priority-classic-first.md`
- `findings/classic-rescue-pre-test123-closure.md`
- `findings/test122-hw-pass-and-stale-status.md`


## Branch closure — Test123 HW PASS / merge-ready

The CLASSIC resurface objective is complete. Test123 is HW PASS and is the protected functional Refresh checkpoint.

Authoritative deterministic source: `tools/refresh_selector/build_test123_from_test122.py`.

Next work must start from merged `main`, not from an experimental ZIP:
1. branch for GB/GBC/GBA individual Refresh wiring;
2. preserve Test123 exactly while implementing commands 3/4/5;
3. leave command 6 Arcade inert until a dedicated Arcade branch;
4. dedicated Arcade branch must handle CPS1/CPS2/NeoGeo/IGS classification/orchestration;
5. explicit ninth Refresh All only after all eight individual operations are stable.

GitHub repository source/reconstruction, findings, manifests/hashes and hardware records are authoritative. Produced or modified source code must be committed before the work is considered preserved; proprietary hardware binaries belong in the companion artifact vault with repository hash/index records.
