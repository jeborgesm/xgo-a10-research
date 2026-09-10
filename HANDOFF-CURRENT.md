# HANDOFF-CURRENT

## Current checkpoint — 2026-09-10 (supersedes historical sections below)

Active branch: `research-game-list-arcade-expansion`. Test47 generalized CLASSIC importer is hardware PASS. Its ZIP SHA-256 is `d40a811e2ef05788688fe516e520b3f11b2e5b08ca77d926e77bf1c224f5db53`. Do not redo Tests23–46 or change the working importer. Remaining gate: CLASSIC Save/Load.

Original Test48 CI run `34427821147` passed compilation, but its fixed scratch addresses did not establish ownership by the stock ROM arena. The corrected candidate reserves 12 MiB raw + 12.125 MiB compressed inside `gp_buf_64m`, below both the allocation end and core base. State v2 rejects wrong core/game identities and malformed sizes before restoration. Host boundary/roundtrip tests pass; hardware verification remains pending.

Deliver as a core-only overlay at `cores/fbalpha2012_cps1/core.xgc` on installed Test47. That inherited directory deliberately contains MAME2000. Do not reinstall catalog triplets: that would overwrite user imports. Keep original core available for rollback. No merge or golden promotion until hardware PASS.

See `findings/classic-test48-snapshot-audit.md`.

## Active branch

`research-game-list-scanning`

Created from merged `main` commit:

```text
2a12bd0fdf0999f2cbffbe9802dc9e25485b2a21
```

The previous `research-post-mapper-runtime` branch is closed and merged.

## Protected hardware baseline

Preserve the successful composed baseline:

```text
Mapper v19
+ native Snes9x2005 Core #2 Test02
+ hardware-confirmed sibling-derived CPS1 scheduler
```

Successful scheduler candidate firmware SHA-256:

```text
9136479687e921fc478ad89ccce3af94296366768a83600312b3bed5ee294607
```

Do not regress this baseline while instrumenting audio.

## Immediate scope: audio OSD experiments

Goal:

> expose useful stock audio state on-screen with the smallest possible runtime disturbance.

Research order:

1. Recover the stock volume/mute/mixer state variables and their update paths.
2. Identify the least invasive existing OSD/text/blit path available during gameplay.
3. Prove a tiny diagnostic overlay can be drawn without altering emulator cadence.
4. Start with read-only telemetry.
5. Only after that consider interactive audio controls or richer diagnostics.

Preferred first OSD values:

```text
volume level
mute state
active sample rate
audio batch/frame count if cheaply available
ring-buffer fill/occupancy if a stable stock value exists
```

Constraints:

- no new emulator core in this branch initially;
- do not touch the successful CPS1 scheduler unless instrumentation proves a conflict;
- preserve Mapper v19 and native SNES baseline;
- do not move timing-sensitive audio work into printf/log paths that could perturb pacing;
- prefer existing stock framebuffer/text routines over a new renderer.

## Priority roadmap after audio OSD

The user explicitly set the next research priorities:

```text
1. Audio OSD experiments                         <- current branch
2. On-device game-library scan/list regeneration <- next priority
3. Additional reliable emulator cores            <- after library work
```

### Next priority: on-device game-library regeneration

Research question:

> Can XGO itself scan ROM folders on command and regenerate/update the stock main game lists, eliminating the need for a Windows-side library-building application?

Earlier work considered an external Windows application as a practical way to add games to the stock lists. Re-open that only as a comparison/reference implementation. The preferred direction is now to determine whether the device can perform the same discovery/index-generation work itself.

Investigation should establish:

- exact stock list/index/database formats and all dependent assets;
- whether filenames, display names, ordering, thumbnails/previews, system IDs, favorites, mapper/config records, or offsets are precomputed;
- which stock code reads those structures and whether any dormant scanner/indexer already exists;
- whether sibling HC15xx/SF2000/GB300 firmware contains an on-device refresh/rebuild mechanism;
- minimum RAM/CPU/storage cost of scanning folders on XGO;
- safe trigger mechanism, preferably an explicit user command rather than scanning every boot;
- atomic/recoverable list regeneration so interruption cannot destroy the existing library;
- how custom ROMs coexist with stock entries and per-game mapper/save metadata.

Do not assume a new screen is required until the stock list architecture is understood. First determine whether regenerated entries can feed the existing stock game-list UI directly.

If new emulator/system support later requires game categories the stock UI cannot represent, treat **new screens/system browsers** as a separate UI architecture problem. That may be a substantially larger lift and should build on the library-format/scanner findings rather than precede them.

## Secondary/future research track: additional reliable cores

This is intentionally deferred until the audio OSD branch has a stable baseline.

Question:

> Which additional emulator cores can run reliably enough on XGO to be worth supporting?

Use a compatibility-first survey rather than "does it boot?"

Evaluate each candidate on:

```text
CPU cost / MIPS32 suitability
memory footprint
video format / resolution
audio sample rate and batching
stock frontend ABI compatibility
input/controller requirements
save-state behavior
representative-game performance
return-to-menu stability
```

Classify results as:

```text
A — reliable/playable
B — works with limitations
C — boots but impractical
D — incompatible
```

Prioritize lightweight 8/16-bit cores and HC15xx/SF2000-family ports before heavier systems.

Do not assume that generic libretro compatibility means practical XGO compatibility.

## Authoritative CPS1 conclusion carried forward

The successful CPS1 result remains:

```text
stock FBA
+ C68K
+ 22050-Hz / 367-sample audio
+ private render-only frameskip
+ sibling wall-time / bounded-catchup pacing
= hardware-confirmed removal of prolonged underwater slowdown
```

Do not resume A68K ROM bisection unless a new, specific research question requires it.


## Audio OSD branch progress

Static archaeology has now recovered the first audio-OSD anchors.

Confirmed runtime symbols:

```text
g_volume         0x80c33a54
set_audio_volume 0x801b3b40
```

The stock frontend alone imposes the four-step `0 -> 33 -> 66 -> 99 -> 0` policy. `set_audio_volume` masks the requested value to 8 bits and forwards it to the sound-device API; the next wrapper at `0x80279d20` again forwards the 8-bit value without four-step quantization.

Therefore intermediate volume values can reach the final stock sound driver, although actual perceptual granularity remains a hardware question.

Preferred first OSD experiment:

```text
volume-button event
  -> set transient expiry state

retro_video_refresh_cb
  -> while active, composite a tiny RGB565 bar into outgoing frame
  -> preserve the normal single run_screen_write call
```

This avoids touching the audio callback, sound task, CPS1 scheduler, display geometry, or adding a second OSD/DMA write per frame.

Primary result:

`findings/audio-osd-volume-state-and-render-strategy.md`

The exact protected scheduler-success firmware was not available in the current working-file set, so no hardware candidate has yet been composed. Do not fall back to pristine stock firmware; the next candidate must be applied to the protected baseline with SHA-256:

```text
9136479687e921fc478ad89ccce3af94296366768a83600312b3bed5ee294607
```


## Golden artifact preservation workflow

The project no longer treats the researcher's local Downloads folder as the canonical binary archive.

Public repository responsibilities:

```text
docs/artifact-preservation.md
artifacts/golden-artifacts.json
tools/artifacts/verify_golden_artifact.py
```

Private binary vault:

```text
jeborgesm/xgo-a10-artifacts
visibility: PRIVATE — VERIFIED 2026-09-05
```

The user populated the vault with the retained XGO research binaries. Canonical hardware-confirmed milestones are additionally copied into the private `golden/` folder while their original root copies remain untouched. `artifacts/golden-artifacts.json` records the canonical golden paths.

Current protected baseline artifact ID:

```text
cps1-scheduler-v1-on-snes-test02
```

Canonical filename:

```text
xgo-cps1-scheduler-v1-on-snes-test02.zip
```

Exact ZIP SHA-256:

```text
0c5a50f7d4b7f1b2b9a5f91a6b8856e3019a994ed43fc79a3f2579b38eaa9f8f
```

Firmware SHA-256:

```text
9136479687e921fc478ad89ccce3af94296366768a83600312b3bed5ee294607
```

Future branch closure rule:

A hardware-confirmed binary candidate is not considered fully preserved until its exact ZIP is recorded in `golden-artifacts.json` and copied to the private artifact vault. Handoffs should reference the artifact ID, not depend on local filenames.


## Audio OSD v1 candidate

Static patch-surface work is complete.

Protected input artifact:

```text
cps1-scheduler-v1-on-snes-test02
firmware SHA-256
9136479687e921fc478ad89ccce3af94296366768a83600312b3bed5ee294607
```

Verified free cave in that exact protected image:

```text
0x80002780..0x80002fff
2176 bytes
```

OSD v1:

```text
blob size      1548 bytes
blob SHA-256   2556cad397c66f5ac98a4f772b05d67eb86eb946bc785c781f1e426ec8954227
headroom       628 bytes
hook           run_screen_write tail jump @ 0x8035c458
output FW SHA  1fc85114909d6107ff80be6e199d54dd1d9b918454ceede61d5108246d6f50c1
candidate ZIP  bdf66f60b0ed105449582e7845a9c9d8d98e3e8e6ae0a695ec9c73dc28685f76
```

The hook preserves one stock OSD write per visible frame. It backs up the 64x8 source-frame area, overlays the bar, performs the normal synchronous stock region write, restores the source pixels, and returns.

No audio callback, GPIO volume path, hardware mute path, mapper, SNES loader, or CPS1 scheduler changes.

Hardware regression gate is pending. Do not promote this artifact to `golden/` until it passes.

Primary finding:

`findings/audio-osd-v1-exact-patch-surface-and-candidate.md`


## Audio OSD v1 archival promotion

Hardware test passed and the exact tested ZIP is now preserved in the private artifact vault at both:

```text
xgo-audio-osd-v1-on-cps1-scheduler.zip
golden/xgo-audio-osd-v1-on-cps1-scheduler.zip
```

Artifact ID:

```text
audio-osd-v1-on-cps1-scheduler
```

ZIP SHA-256:

```text
bdf66f60b0ed105449582e7845a9c9d8d98e3e8e6ae0a695ec9c73dc28685f76
```

Firmware SHA-256:

```text
1fc85114909d6107ff80be6e199d54dd1d9b918454ceede61d5108246d6f50c1
```

This is now the protected baseline for the next finer-volume-control experiment.


## Audio OSD v2 fine-volume hardware PASS

The fine-volume experiment is hardware-confirmed and is now the protected baseline.

Artifact ID:

```text
audio-osd-v2-fine-volume
```

Private golden artifact:

```text
golden/xgo-audio-osd-v2-fine-volume-test.zip
```

Exact tested ZIP SHA-256:

```text
086c60d7595843c778b04663aa5922ccd05ac966b1c4cb5ee736a78edbba428c
```

Firmware SHA-256:

```text
6b3261a9871c2b5678428ae1985176718c140178564ea924241bf6889ec714ac
```

Hardware confirms distinct intermediate audio levels and continuous OSD progression.

Current follow-up candidate:

```text
xgo-audio-osd-v3-menu-refresh-test.zip
ZIP SHA-256 15edc2b239cc9c7f9fed09ff0c3363ded2bc7fb10bd1345072abfc144bfad8bc
FW SHA-256  67e8474db2c0a85e230517adb2a699877b046b74fceddc0a2e2bb59fc9145dec
```

V3 changes only sparse 640x480 main-menu repaint timing. Do not promote V3 to golden until hardware passes.


## Audio OSD branch closure — final hardware PASS

Final hardware-confirmed artifact:

```text
xgo-audio-osd-v8-button-event-only-test.zip
ZIP SHA-256      ba3dad99471c6144fd8f6e9f5891bc88d44b955c5de8a21df905d0d396cdb83a
firmware SHA-256 4b8f7af994d16371a2664a3d46c983e52ffd1aefbebc5b5a4a9ae63dc6cbe954
```

Hardware result: PASS.

Final behavior:
- 11 audible nonzero volume levels plus mute: 0,9,18,...,99,0;
- transient 64x8 volume OSD;
- 1-pixel RGB565 0x8410 gray border;
- main-menu OSD appears only after a physical Volume-button event;
- repeated presses update it and restart the timeout;
- disappears after approximately one second of inactivity;
- no false OSD immediately after splash/boot;
- gameplay remains uninterrupted;
- in-game pause-menu OSD works;
- no loading/black/loading regression;
- physical button event, not arbitrary g_volume changes, is the semantic OSD trigger.

Archive status: promote exact v8 ZIP to `golden/` in the private artifact vault.

Branch `research-audio-osd` is complete and ready to merge to `main`.

Future UI idea, deliberately out of scope here: investigate replacing/customizing the device splash screen.


## Game-list scanning branch — initial archaeology

Branch created from merged Audio OSD main after PR #12.

Protected baseline remains:

```text
audio-osd-v8-button-event-only
ZIP SHA-256      ba3dad99471c6144fd8f6e9f5891bc88d44b955c5de8a21df905d0d396cdb83a
firmware SHA-256 4b8f7af994d16371a2664a3d46c983e52ffd1aefbebc5b5a4a9ae63dc6cbe954
```

Do not modify that artifact in place.

Initial native result:

- XGO contains an on-device directory scanner/list writer at stock runtime `0x80353ae0`;
- it enumerates files through the stock filesystem layer, rejects directories, normalizes/validates ROM extensions, alphabetically sorts accepted filenames, and writes the stock `count + offsets + strings` list format;
- list ID 0 maps `ROMS` to `tsmfk.tax` in all three resource slots;
- the scanner has a one-shot runtime flag, strongly matching the SF2000/GB300 behavior of rebuilding the User-ROM index during startup/initial frontend entry;
- built-in FC/SFC/MD/GB/GBC/GBA/curated-Arcade pages remain different: they use synchronized filename/title/search-key triplets, so blindly applying the User-ROM scanner to them would leave metadata misaligned.

Primary finding:

`findings/on-device-user-rom-list-scanner-and-writer.md`

Immediate next targets:

1. close the exact caller-state gate for the list-0 startup scan;
2. trace fixed-list loading and list ID 11 special handling;
3. recover the minimum metadata regeneration rules needed to safely expose added ROMs in stock built-in pages;
4. only then design an explicit on-device rebuild command.

No firmware has been modified and no hardware-test ZIP has been generated on this branch yet.


### Deeper list-architecture results

The scanner caller gate is now closed:

- current-list state: `gp-0xdf4`;
- selected-list state: `gp-0xda4`;
- one-shot scan flag: `gp-0x5f64`;
- the scan flag has exactly one read and one write in the firmware and no reset path;
- all three globals are zero-initialized BSS, so first stable frontend state is list 0 / `ROMS` with scan flag clear;
- after `tsmfk.tax` generation the flag is latched and later built-in pages cannot invoke the scanner in that session.

The earlier label for `0x803536ec` has been corrected: that routine handles 16-bit-record persistence resources such as `Hisas.boa`, not the main 32-bit-offset game-string catalogs.

The real built-in browser random-accesses catalog strings by reading a 32-bit offset and then seeking to `4 + count*4 + offset`.

Language selection is now proven:

```text
English/Arabic/Hebrew/Spanish/Russian -> filename/English slot 0
Chinese                                -> display-title slot 1
slot 2                                 -> search-oriented path
```

List ID 11 remains `None / None / None`. No direct list-ID-11 special branch was found in the main browser; combined with the one-shot scanner already being consumed by ID 0, this now strongly favors an empty/dormant fifth Arcade placeholder over a dynamic raw-ZIP list.

Safe built-in regeneration strategy is now **stable merge**, not full alphabetical rebuild:

- keep every existing entry/index in place;
- append only newly discovered physical ROMs;
- append aligned fallback records to all three metadata catalogs;
- do not delete or reorder in the first implementation;
- this preserves existing Favorites/History indices automatically.

The browser's per-list count array begins at `0x80d2894c`. Built-in counts are lazy-loaded from catalog offset 0 when a cached count is zero. Therefore after a successful rebuild the runtime can invalidate just `count[list_id]` and let stock code reload the new count; a full frontend restart is not required.

New findings:

- `findings/game-list-loader-caller-gate-and-metadata-semantics.md`
- `findings/safe-built-in-library-regeneration-strategy.md`

### Search semantics and byte-exact append proof

Further archaeology closed the Search path and reduced the first built-in update to a minimal transform:

- normal display language-slot map is `0,1,0,0,0,0`: Chinese uses slot 1, the other five languages use slot 0;
- Search uses a separate map `0,2,0,0,0,0`: Chinese Search uses slot 2; other languages search slot 0;
- Chinese Search starts at list ID 1 and deliberately skips User Games/list 0;
- Search candidate matching normalizes characters and matches ASCII A-Z / 0-9 while ignoring punctuation/spacing;
- Search results are stored as `{ uint16 list_id, uint16 game_index }`, capacity 200;
- only English state 0 explicitly strips the filename extension in the observed display path;
- therefore a safe new-entry fallback is exact filename / basename / basename rather than manufacturing a separate compact search key.

Stable append byte audit:

- all 31 recovered XGO list resources end exactly at the final NUL; no padding/footer exists;
- existing offsets are relative to the string blob, so adding one entry does not require changing any old offset;
- exact append transform is: increment count, copy all old offsets unchanged, add one offset equal to old blob length, copy old blob byte-for-byte, append new UTF-8 string + NUL;
- this preserves every original OEM string byte and every existing game index.

Offline FC proof candidate:

`Bomber Man 2.zfc` is physically present but absent from the 744-entry FC catalog.

Prototype output:

`rdbui.tax` 744->745, SHA-256 `18e96c0543f98e513af4a2cf4e7679d922e1d26bad7d242d1eb59492890556ab`
`fhcfg.nec` 744->745, SHA-256 `c958891b891093ba1a3b23838798a89925f2419f10322e4059c5ad4f9b51e8de`
`nethn.bvs` 744->745, SHA-256 `4d76f100fd672ff7557517e9fd671238c0002e5fac955856d0f831a5b9d7e62e`

Assertions prove all 744 old offsets and all old string-blob bytes are unchanged.

Repository tool:

`tools/game_lists/prototype_append_existing_fc_rom.py`

Filesystem recovery result:

- `0x802abf50` is a live directory-removal operation;
- no stock `rename` string, mapped wrapper, or frontend atomic-replace use has been found;
- first on-device catalog update should therefore use backups plus a persistent transaction-phase marker and recovery on next boot, not depend on atomic rename.

New findings:

- `findings/search-semantics-browser-state-and-transaction-recovery.md`
- `findings/byte-exact-stable-append-proof.md`

No firmware or hardware-test ZIP has been generated.
### Special frontend state closure and Game-List Test01

Special frontend state map is now:

```text
0..11  normal game categories
12     Favorites
13     History
14     User Menu / Setup
15     Search
```

The User Menu has exactly three selectable rows with wrap range `0..2`:

```text
0 User Games
1 Language
2 TV System
```

Search is entered through a separate input path into state 15; it is not a fourth selectable row. Therefore a polished Refresh Games action cannot simply be appended as row 3 without modifying renderer/navigation bounds.

The earliest safe future transaction-recovery hook is immediately before the stock once-per-session `ROMS -> tsmfk.tax` scan at `0x80359404`, after SD/Resources are available and before normal built-in list browsing.

Static catalog semantics are now isolated from runtime mutation with Hardware Test01:

```text
xgo-game-list-test01-bomberman2-static-triplet.zip
ZIP SHA-256 45182596fd1f0598f356901b06ffc3cca94dcfcb445ac8e3b272702c6f9a3350
```

Private artifact vault status: archived at repository root, intentionally non-golden pending hardware.

Test01 changes only the synchronized FC catalog triplet from 744 to 745 entries and appends the already-present physical ROM `Bomber Man 2.zfc`. No firmware and no ROM payload are included. All 744 prior indices remain unchanged.

Primary finding:

`findings/hardware-test-game-list-test01-static-triplet-candidate.md`

Hardware PASS criteria: final FC entry appears, launches, Search remains valid, Chinese mode does not mis-index/crash, and existing Favorite/History references remain stable.

Do not begin the on-device writer/transaction implementation until this static catalog contract passes hardware.
### Game List Test01 hardware result and Test02 control

Test01 artifact:

`xgo-game-list-test01-bomberman2-static-triplet.zip`
`ZIP SHA-256 45182596fd1f0598f356901b06ffc3cca94dcfcb445ac8e3b272702c6f9a3350`

Hardware result:

- FC entry count increased to 745;
- entry 745 displayed as `Bomber Man 2`;
- selecting it reached the game runtime;
- screen flashed and then remained black;
- stock pause menu still worked and quit returned normally.

Interpretation: catalog append/display/index/dispatch PASS; `Bomber Man 2.zfc` gameplay FAIL/black screen. Do not treat the black screen as a catalog-format failure.

The user had no Favorite before Test01. A `Mega Man` Favorite has now been created specifically as an index-stability sentinel for later tests.

Test02 is a stricter control that appends a duplicate catalog reference to the already-stock-listed physical wrapper `FC/Mega Man 1.zfc` while preserving its original index.

Expected FC tail:

`745 Bomber Man 2`
`746 Mega Man 1`

Test02 artifact:

`xgo-game-list-test02-megaman1-known-good-duplicate.zip`
`ZIP SHA-256 40f6dce8380f61942f2f4f472b0c137fed8a6042cb00b0b3b669c99090d15a73`

Test02 outputs:

`rdbui.tax` SHA-256 `263926964e4c5aa5508c7f44490f1e6ff397947c83f52c2c3c28069be71c1335`
`fhcfg.nec` SHA-256 `b9af569cb185187f506d51a2622caf9d41a5f9d9914effbd56451a0a3d8d2153`
`nethn.bvs` SHA-256 `0d0001520b645d795128d915a665c7e8c251ee29a57abc2f425043d824ed7ef1`

Test02 hardware gate: launch entry 746 and verify normal Mega Man gameplay; then open the pre-existing Mega Man Favorite and verify it still resolves to the same original game.

Findings:

- `findings/hardware-test-game-list-test01-partial-pass.md`
- `findings/game-list-test02-known-good-duplicate-candidate.md`
### Hardware milestone — Test02 stable append PASS

`xgo-game-list-test02-megaman1-known-good-duplicate.zip`

ZIP SHA-256 `40f6dce8380f61942f2f4f472b0c137fed8a6042cb00b0b3b669c99090d15a73`

Hardware confirmed that appended FC entry 746 (`Mega Man 1.zfc`) displays at the end of the list and launches normally. The appended reference sees the existing Mega Man saves, supports normal button remapping, Audio OSD/volume changes, and normal gameplay.

This proves the stable-append built-in catalog contract independently of ROM compatibility. Test01 Bomber Man 2 black output is therefore isolated to that physical wrapper/payload compatibility rather than catalog indexing.

Important identity finding: save/remap/runtime state follows the physical ROM identity/path, not the catalog index. A duplicate catalog reference reaches the same existing saves and runtime configuration.

Next priority: promote the hardware-confirmed Test02 metadata milestone appropriately in the private artifact vault, then move from static catalog proof to the on-device stable-merge scanner/writer design. Preserve existing indices; use the Mega Man Favorite as an index-stability sentinel during future mutation tests.
### Exact wrapper/import archaeology

Captured `Resources/Test.zsf` fully closes the XGO ZXX wrapper format:

- file size 93,867 bytes;
- SHA-256 `8e661f5a9246091228dd2eedae65c109d2add7aa3c22cc0231c39dd67b3600f4`;
- first 59,904 bytes are the 144x208 little-endian RGB565 thumbnail;
- offset `0xEA00` begins a WQW-obfuscated standard ZIP;
- WQW transform = ZIP signatures changed to `WQW\x03` / `WQW\x02` / `WQW\x01` and local/central filename bytes XOR `0xE5`; compressed data unchanged;
- de-obfuscation opens as a normal DEFLATE ZIP containing `手柄测试.sfc`;
- de-obfuscating then re-obfuscating and concatenating the untouched thumbnail reproduces the original Test.zsf byte-for-byte with the exact same SHA-256.

The stock launcher computes preview size dynamically as `thumbnail_width * thumbnail_height * 2` before calling `run_game`, rather than hard-coding 59,904.

New finding: XGO also contains the exact Lucian Wischik XZip/XUnzip error-string family plus `deflate 1.2.5`, strongly proving ZIP-creation code is linked into the firmware. The corresponding open-source implementation exposes `CreateZip`, `ZipAdd`, and `CloseZip`; exact XGO addresses remain to be mapped.

The first 59,904 bytes of Test.zsf decode correctly as 144x208 little-endian RGB565 and visibly produce the expected Super Famicom controller-test image.

PNG/JPEG-related code exists (`image/png`, `image/jpeg`, JPEG decoder diagnostics), but a compact reusable still-image API is not yet proven.

Recommended staged feature path:

1. Refresh Games: scan existing `.zxx` wrappers and stable-append catalogs.
2. Import Prepared Game: raw ROM + preconverted 144x208 RGB565 cover -> stock ZIP creator -> WQW -> `.zxx` -> catalog append.
3. Import Game: PNG/JPEG artwork once a reusable stock decoder or small decoder port is proven.

New findings:

- `findings/exact-xgo-zxx-wrapper-and-wqw-contract.md`
- `findings/on-device-import-feasibility-stock-zip-and-image-stack.md`
### Test02 golden promotion and Test03 import candidate

Hardware-confirmed Test02 has been promoted in private `jeborgesm/xgo-a10-artifacts` by reusing the exact existing blob, no rebuild:

`golden/xgo-game-list-test02-megaman1-known-good-duplicate.zip`

Artifact-repo promotion commit:

`1818e81cbea17eee982899880ec1fea17247f4fb`

Git blob is identical to the root candidate: `fb09093f6e85771aad5facd3dd4a56bfb13378ba`.

Test03 candidate:

`xgo-game-list-test03-sfc-import-store-wrapper.zip`

ZIP SHA-256:

`bfef6f95adaf7cd986061154d20e500580135930426994b5ed3b44c822987320`

New wrapper:

`SFC/XGO Import Test.zsf`

wrapper size 191,112 bytes; SHA-256 `f600c45d37a77d9af80ecb1ad136e1dbcfbb7e22fd9afc91531f82cfd2fb03b1`.

It is generated from scratch using the XGO's own controller-test SNES ROM and thumbnail, but deliberately uses ZIP method 0 / STORE inside WQW rather than DEFLATE.

SFC triplet 929->930:

- `urefs.tax` `f2cbc51c08689229216fab1024d7acd7c62480d96812d97c2efe984f1fe63916`
- `adsnt.nec` `c010fca8f276bd73f34b7c01357979d94680961d4238fbb55521d589228ba2cb`
- `xvb6c.bvs` `ccc7339310b785dce8537014af408b7e0aa09e9025dc2584ebac49bd159c032b`

Expected new SFC tail entry: `930 XGO Import Test`.

If hardware accepts STORE, future on-device wrapper creation can avoid compression entirely: thumbnail + tiny ZIP/WQW writer + raw ROM bytes + stable catalog append.

Candidate documentation:

`findings/hardware-test-game-list-test03-import-store-wrapper-candidate.md`

Do not promote Test03 to golden until hardware passes.
### Wrapper/import packaging archaeology

XGO Zxx packaging is now directly recovered from captured hardware files.

- `Resources/Test.zsf` SHA-256 `8e661f5a9246091228dd2eedae65c109d2add7aa3c22cc0231c39dd67b3600f4`;
- exact wrapper boundary at `0xEA00` / 59,904 bytes;
- prefix is 144x208 RGB565 thumbnail data;
- payload begins `WQW\x03` and is a lightly obfuscated standard ZIP;
- WQW local/central/end signatures are `WQW\x03`, `WQW\x02`, `WQW\x01`;
- stored filenames are XORed with `0xE5`;
- restoring normal ZIP signatures and XOR-decoding filenames makes the captured XGO payload open and CRC-verify with a standard ZIP reader;
- captured package contains `手柄测试.sfc` using ordinary DEFLATE.

Preview size is not an unrelated magic constant. Both stock game-launch call sites compute:

`preview_size = thumbnail_width * thumbnail_height * 2`

before passing it to `run_game()`. Shipped `Foldername.ini` supplies 144x208, yielding 59,904 exactly.

New generic builder:

`tools/game_lists/build_wqw_store_wrapper.py`

It intentionally creates method-0/STORE WQW packages from a preconverted RGB565 thumbnail plus raw ROM, avoiding any need for an on-device DEFLATE compressor.

Recovered scratch hardware candidate Test03 has been re-audited cleanly:

`xgo-game-list-test03-sfc-import-store-wrapper.zip`

ZIP SHA-256 `bfef6f95adaf7cd986061154d20e500580135930426994b5ed3b44c822987320`

It creates `SFC/XGO Import Test.zsf`, SHA-256 `f600c45d37a77d9af80ecb1ad136e1dbcfbb7e22fd9afc91531f82cfd2fb03b1`, using the XGO's own 131,072-byte controller-test SNES ROM and thumbnail. SFC catalogs are stable-appended 929->930 with all prior offsets/blob bytes preserved.

Test03 exact ZIP bytes are preserved in private vault staging `staging/game-list-test03/part00.b64`..`part05.b64`, with a hash-verifying archive workflow and staging README. Not golden pending hardware.

Image-decoder note: stock firmware contains genuine JPEG/PNG-capable multimedia code and JPEG hardware diagnostics, but no proven frontend API has yet been found that imports arbitrary SD PNG/JPEG into the game's RGB565 cover format. First importer should therefore use preconverted RGB565 covers until that surface is mapped.

Primary finding:

`findings/xgo-zxx-wrapper-and-import-packaging-contract.md`
### Hardware milestone — Test03 generated WQW wrapper PASS

`xgo-game-list-test03-sfc-import-store-wrapper.zip`

ZIP SHA-256 `bfef6f95adaf7cd986061154d20e500580135930426994b5ed3b44c822987320`

Hardware confirmed the newly generated `SFC/XGO Import Test.zsf` appears as final SFC entry with its embedded SNES controller-test thumbnail, launches successfully, accepts Start/Select, opens the normal pause menu, and behaves as a normal SFC game.

This proves XGO accepts a newly generated method-0/STORE WQW wrapper outside the OEM Windows toolchain. Together with Test02, both halves of the static import contract are now hardware proven: stable catalog append and generated stock-style Zxx packaging.

Test03 has been promoted to `golden/xgo-game-list-test03-sfc-import-store-wrapper.zip` in the private artifact vault and added to `artifacts/golden-artifacts.json`.

Next engineering/research target: combine the proven primitives into an on-device scanner/importer while preserving existing indices. First implementation should scan for already-packaged unindexed Zxx files. A later import mode can package raw ROM + preconverted RGB565 cover using the proven STORE WQW writer. PNG/JPEG decode remains optional future work unless a cheap stock decoder entry point is recovered.

## External comparator preservation — DY19 direct extraction

The DY19 stock-image recovery target is complete.

A read-only HTTP-Range FAT32 extractor recovered `BIOS/BISRV.ASD` and selected `Resources/` directly from the 31GB Internet Archive image without downloading the ROM payload.

DY19 application identity:

```text
size    12,477,596
SHA256  135ddf837f37570cedbd204036e02bdede876338ad94a9c33cac0db5ac8fe9e4
```

Successful extraction artifact ZIP:

```text
SHA256  3d7ebfb44fd0c31a6b022b4d58018da9bb7518de1b4ed7493a0d0a6229dc19d6
```

Preservation locations:

- public reproducibility: `tools/dy19/`, workflow and `findings/dy19-direct-stock-image-comparison.md`;
- private binary vault: external/reference corpus documented under `external/`;
- local analysis archive: `XGoAnalisis/DY19/` contains the retained workflow artifact and unpacked extraction.

Do not treat DY19 bytes as an XGO golden baseline.

Direct comparison conclusion:

```text
XGO = DY19-family H1512 software/content fork
    + XGO-specific board adaptation
```

The next hardware-archaeology priority is authentic DY19 PCB/teardown imagery and component identification, especially controller, LCD, RF, power and UART/test-pad regions.


## New high-value external investigator: 炒鸡大帅比9961

Chinese Bilibili research has identified an active modder working on the same DY12/DY19-style power-bank handheld family.

Indexed videos include:

```text
2025-08  充电宝游戏机新系统包介绍
2026-04  DY-12变色翻转问题成功修复
2026-05  充电宝游戏机 自定义添加游戏工具
          充电宝游戏机可以玩PS1游戏？
```

This is now directly relevant to both current/future roadmap items:

- game-list scanning/regeneration;
- additional emulator/core support;
- model-specific LCD adaptation.

A separate `叶落听风者` DY19 SF2000-conversion series includes a 2026 follow-up specifically about importing localized games.

Next external-recovery priority:
1. recover the custom add-game tool;
2. recover the modified system pack;
3. inspect the DY12 display-orientation/color patch;
4. compare their list-generation behavior against XGO's native databases.

Primary finding:
`findings/dy19-dy12-chinese-modding-ecosystem.md`

## Refresh Games implementation branch

The completed game-list archaeology and 39-image evidence corpus were checkpointed into `main` by PR #13 at merge commit:

```text
8bdb175b2e73d35e8f336d0039b771b15a8a0ede
```

Fresh implementation branch:

```text
research-game-list-refresh-implementation
```

### Natural trigger

Stock User Menu row 0 (`User Games`) is now the preferred Refresh trigger.

Dispatcher anchor:

```text
0x80359e94  load selected User Menu row
0x80359e98  row 0 -> stock User Games destination 0x80357468
```

The implementation can interpose Refresh here and then continue to the exact stock destination. No fourth menu row and no uncertain raw-button chord are required.

Primary finding:

`findings/refresh-games-implementation-hook-and-staged-proof.md`

### Test04 staged runtime-writer design

Test04 isolates device-side canonical catalog mutation before implementing the full directory scanner.

Protected inputs:

```text
Audio OSD v8 golden ZIP
ba3dad99471c6144fd8f6e9f5891bc88d44b955c5de8a21df905d0d396cdb83a

Audio OSD v8 firmware
4b8f7af994d16371a2664a3d46c983e52ffd1aefbebc5b5a4a9ae63dc6cbe954

Test03 generated-wrapper golden ZIP
bfef6f95adaf7cd986061154d20e500580135930426994b5ed3b44c822987320
```

New safe runtime cave:

```text
0x807dab98..0x807dbb9f
4104 usable bytes
```

The referenced table beginning at approximately `0x807dbba0` is intentionally excluded.

Current deterministic writer blob:

```text
entry       0x807dab98
size        688 bytes
SHA-256     88bd4d39cbfe94ef8fbb47861d86c2d8eb3746533afa27a33f57724b0e417cd4
headroom    3416 bytes
```

Test04 install state intentionally restores the original 929-entry SFC triplet while placing `SFC/XGO Import Test.zsf` on disk and staging the known-good 930-entry triplet in `Resources/refresh.bin`.

Expected hardware sequence:

```text
boot -> SFC 929 / XGO Import Test absent
User Menu -> User Games
device rewrites SFC triplet
SFC cache invalidated
return to SFC -> 930 / XGO Import Test present
```

The routine uses stock `fopen/fread/fwrite/fclose` plus the stock filesystem sync wrapper.

**Test04 is deliberately non-transactional and disposable-clone-only.** It is a runtime-write proof, not the final Refresh Games implementation.

Public builder:

`tools/game_lists/build_test04_runtime_refresh.py`

Primary finding:

`findings/game-list-test04-runtime-writer-candidate.md`

Next action: compose Test04 inside the private artifact vault from the exact two golden inputs, archive the generated ZIP at vault root immediately, then hardware-test. Only a hardware pass is eligible for `golden/`.


### Test03 vault repair COMPLETE / Test04 candidate READY

The private-vault Test03 golden artifact had an archival corruption caused by an interrupted Base64 transfer. The authoritative hardware-tested Test03 ZIP remained intact locally and was used to repair the vault.

Repair gate passed:

```text
xgo-game-list-test03-sfc-import-store-wrapper.zip
size 76,285 bytes
SHA-256 bfef6f95adaf7cd986061154d20e500580135930426994b5ed3b44c822987320
unzip integrity PASS
```

The repaired golden Test03 then passed the Test04 CI input audit together with exact Audio OSD v8.

Exact Test04 candidate:

```text
xgo-game-list-test04-runtime-sfc-refresh.zip
size 4,740,864 bytes
SHA-256 342ce43bcdc7af6f847741385deb148fb93c3bea2e678b3eff6f5c6ec6e031af
```

Candidate firmware:

```text
SHA-256 ceda0e903a29e652d4c9c72394f798002a3de5b618399c4c5ed1c81690159486
LCFG CRC-32/MPEG-2 0xb266669f
```

Writer blob:

```text
688 bytes
SHA-256 88bd4d39cbfe94ef8fbb47861d86c2d8eb3746533afa27a33f57724b0e417cd4
```

The exact Test04 candidate is archived at the private artifact-vault root and is **not golden** pending hardware.

Hardware procedure:

1. disposable SD clone only;
2. install Test04;
3. before invoking User Games, SFC should show 929 games and XGO Import Test must be absent;
4. invoke `User Menu -> User Games` once;
5. return to SFC: expected 930 games, final entry XGO Import Test;
6. launch XGO Import Test and verify controller-test behavior;
7. reboot and verify 930 persists;
8. verify the existing Mega Man Favorite still resolves normally;
9. briefly verify Language and TV System rows still behave normally.

Test04 is intentionally non-transactional. Avoid power loss during the User Games trigger/write sequence.


### Hardware milestone — Test04 on-device runtime catalog rewrite PASS

Hardware result: **PASS** on 2026-09-07.

Exact hardware-tested artifact:

```text
xgo-game-list-test04-runtime-sfc-refresh.zip
size 4,740,864 bytes
SHA-256 342ce43bcdc7af6f847741385deb148fb93c3bea2e678b3eff6f5c6ec6e031af
firmware SHA-256 ceda0e903a29e652d4c9c72394f798002a3de5b618399c4c5ed1c81690159486
```

Every planned hardware gate passed:

- before the trigger, SFC remained at 929 entries and XGO Import Test was absent;
- `User Menu -> User Games` executed the injected device-side writer and continued through the normal stock path;
- afterward SFC reloaded as 930 entries with XGO Import Test as the final entry;
- XGO Import Test launched and retained the controller-test behavior proven in Test03;
- after reboot, the 930-entry catalog persisted;
- the pre-existing Mega Man Favorite/save behavior remained intact;
- User Menu Language and TV System behavior remained intact.

This closes the architectural question Test04 was designed to answer: **XGO can rewrite the synchronized built-in catalog triplet on-device, invalidate the cached count, and have the unmodified stock browser consume the rewritten persistent catalog.**

Test04 remains a staged/non-transactional proof, not the final Refresh Games implementation. The next implementation step is to replace `Resources/refresh.bin` with the general on-device scan + stable-merge engine and add backup/transaction-marker recovery before canonical catalog replacement.

Archive rule: promote this exact hardware-tested ZIP to private-vault `golden/`; do not rebuild it for promotion.


## Private-vault composition complete — exact hardware candidate ready

The Test05 private-vault composition completed successfully on 2026-09-07 from the exact protected Audio OSD v8 baseline plus a freshly reconstructed compact source bundle containing the seven hash-asserted stock setup resources.

Verified compact UI source bundle:

```text
setup-ui-stock-source-new.tar.xz
size 94,664 bytes
SHA-256 6a1264b9ebf49f4bb28f2185168ca400fbc883a9bacfde6874796baaf813701c
```

All seven source member hashes matched the deterministic builder's stock-resource assertions. The previously interrupted `staging/test05-ui-source-20260907/` transfer was not reused.

Exact Test05 hardware candidate:

```text
xgo-game-list-test05-explicit-refresh-menu.zip
size 4,908,988 bytes
SHA-256 766071faec548b04deffef4e97ba900c965aa09686a05195d6bbda997b7961a4
firmware SHA-256 30de1ecc9819f0e669a872cd642e23098506a6411f2ce0de74b4dedfc1a0ae21
stub SHA-256 23d57760e7b249802d2e1b97069a820d92a4494c6b87570160d3f45377b0fd2d
```

The private CI gate reproduced every expected modified bitmap hash, exact candidate size/hash, exact firmware hash, and passed `unzip -t`. The candidate is archived at the private-vault root (binary archive commit `ea4faae`) and exposed as a CI artifact for hardware retrieval. It is **not golden** pending hardware confirmation.

Next action: hardware Test05 only. Do not attach the Test04 writer yet. The gate is the explicit four-option UI, navigation, preservation of the original three menu actions, and harmless REFRESH stub behavior with no catalog mutation.


### Test05 hardware result — UI mechanics partial PASS; visual polish FAIL (2026-09-07)

Hardware candidate:
```text
xgo-game-list-test05-explicit-refresh-menu.zip
size 4,908,988 bytes
SHA-256 766071faec548b04deffef4e97ba900c965aa09686a05195d6bbda997b7961a4
firmware SHA-256 30de1ecc9819f0e669a872cd642e23098506a6411f2ce0de74b4dedfc1a0ae21
```

Observed on hardware:
- all four 2x2 options are visible;
- User Games, Language, and TV System still perform their stock functions;
- REFRESH selection is a harmless no-op as designed;
- visual defect: dynamic NTSC/PAL text remains at the stock top-right TV-system coordinate and must move down/left into the relocated TV tile;
- visual defect: blue selection border and A action badge appear on all four tiles after the new layout/navigation, rather than only representing the current selection as intended.

Classification: **Test05 is NOT golden.** The fourth-command mechanics are promising, but visual selection semantics must be corrected before binding Refresh to Test04. Do not attach catalog writes yet.

Next candidate: Test05b/05.1 UI-only correction. Preserve the no-write REFRESH stub while correcting TV mode coordinates and selection overlay behavior.


### Test05b hardware candidate — polished explicit Refresh UI (2026-09-07)

Built from protected Audio OSD V8 plus the verified stock setup-UI source bundle. No catalog-write path is attached; Refresh remains a no-op stub.

```text
xgo-game-list-test05b-polished-refresh-menu.zip
size 4,914,256 bytes
SHA-256 cae6acf4e5cd1016d1cb380df79355a2142aefd87653059f3baa119371e1d37f
firmware SHA-256 8638ba5aed222b60052020a9fe2caa12109e7656d5e3eebb29431887066589f1
stub SHA-256 23d57760e7b249802d2e1b97069a820d92a4494c6b87570160d3f45377b0fd2d
```

Changes relative to Test05:
- label is title-case `Refresh`;
- all four tiles and labels are shifted upward 20 pixels to clear the footer controls;
- dynamic NTSC/PAL draw point is transplanted from the stock TV tile offset to the relocated TV tile;
- the setup redraw is expanded to a full 640x480 RGB565 copy before the active selector is drawn, intended to prevent stale selector border/A-badge accumulation;
- rows 0..2 remain stock destinations; row 3 remains a no-write stub.

Hardware gate: verify layout/label clearance, NTSC/PAL placement, exactly one active selector overlay while navigating repeatedly, unchanged stock functions, and no game-count/catalog mutation when Refresh is selected. Do not promote to golden until hardware-confirmed.


### Test05c hardware result — functional/geometry PASS; label-style refinement requested (2026-09-07)

Hardware-confirmed behavior:
- four-item 2x2 layout works;
- footer icons restored;
- selector behavior correct;
- NTSC/PAL positioning correct after the dual-path coordinate fix;
- rows 0..2 retain stock behavior;
- Refresh remains a no-op as designed.

Remaining issue is cosmetic only: the bold synthetic Refresh label does not visually match the OEM labels. Test05c is therefore not promoted to golden as the final explicit-menu milestone.

### Test05d hardware candidate — OEM-style regular Refresh label

Test05d freezes all Test05c runtime/geometry fixes and changes only the Refresh label raster. The new label is an antialiased regular sans raster, 84x17 pixels, baseline-aligned with the stock bottom labels. No catalog-write path is attached.

```text
xgo-game-list-test05d-oem-refresh-label.zip
size 4,918,184 bytes
SHA-256 c8ca3bf010f1d658e0c7ceb249473b05ca65541220fa81650adfe762084f9be6
firmware SHA-256 03d1e5278eb7a8a8b525776ffa8cf7cdc8c10c35e41166bf500cd0f410240845
stub SHA-256 23d57760e7b249802d2e1b97069a820d92a4494c6b87570160d3f45377b0fd2d
```

Hardware gate for Test05d: visual confirmation that Refresh now matches the regular OEM label style closely enough. No other behavior should differ from Test05c. Do not promote until hardware-confirmed.


### Test06 hardware candidate — explicit staged Refresh + stock-font status feedback (2026-09-07)

Test06 combines the two previously hardware-proven pieces: the Test05c/d explicit fourth User Menu command and the Test04 on-device staged SFC catalog writer. Refresh now performs the staged 929->930 rewrite directly from the visible menu item.

User feedback was added before hardware testing by reusing the stock setup-screen text renderer (the same firmware path used for dynamic NTSC/PAL text). A persistent in-RAM status value is rendered after all NTSC/PAL setup draw paths:

- `Games Updated` after a successful staged rewrite;
- `No New Games` when the canonical SFC catalog already reports 930 entries, in which case all writes are skipped;
- `Refresh Failed` for unexpected catalog count or read/open/write failures.

The Refresh label itself carries the slightly heavier Test05d raster requested for the next step. All known-good Test05c geometry/footer/selector/TV-text fixes remain frozen.

Exact candidate:

```text
xgo-game-list-test06-explicit-staged-refresh.zip
size 5,022,831 bytes
SHA-256 44e8632b2f71572d9d7e98a75c0dbea00cafa9dd6cfb98eadb149b7c83086fed
firmware SHA-256 c69627edbc5c8112a5b0ec890ea6ddde1180de952e36944d0da8a1070f0df907
writer/status blob bytes 1,238
writer/status blob SHA-256 85d1f32722d8dbf426c9d7c0ecde962b286505f25b6c02ae591a78226be11745
```

Private CI run 34169680118 passed protected-input verification, builder execution, ZIP integrity, artifact upload, and vault-root archival. This candidate is NOT golden pending hardware confirmation.

Hardware gate:
1. install on the disposable clone; initial SFC catalog must be 929 and XGO Import Test absent;
2. open User Menu and select Refresh;
3. expect return to User Menu plus stock-font `Games Updated` status;
4. SFC must become 930 with XGO Import Test last and launch normally;
5. select Refresh again; expect `No New Games` and no rewrite;
6. reboot and confirm 930 persists, Mega Man Favorite/save remains intact, and User Games/Language/TV System remain normal;
7. visually verify status text placement under both NTSC and PAL setup states.

The staged writer remains intentionally non-transactional. Do not treat Test06 as the final general Refresh Games scanner yet.


### Test06 hardware result — explicit Refresh functional PASS; status persistence polish issue (2026-09-07)

Hardware-confirmed:
- visible Refresh command performs the staged on-device catalog update successfully;
- SFC changes to the staged 930-entry catalog as expected;
- repeated Refresh correctly reports `No New Games`;
- stock menu behavior and explicit Refresh integration are working.

Observed polish issue: the status message remains resident on the User Menu indefinitely, including after leaving to a game list and returning. Test06 is therefore not the final polished milestone.

### Test06b candidate — timed stock-font Refresh status

Test06b preserves the Test06 writer/status behavior and adds a monotonic 3-second expiry using the stock `os_get_tick_count()` service recovered at runtime address `0x8030fec8`. Each result stores its creation tick; the stock-font status renderer clears the in-RAM status once unsigned elapsed time reaches 3000 ms. Therefore returning to User Menu after the expiry should not resurrect the old message.

```text
xgo-game-list-test06b-timed-status.zip
size 5,022,902 bytes
SHA-256 2d859b3ca3f0644a461c197fcfe0b58f2650c26bc6a7c8d28a189da196aa1042
firmware SHA-256 5d15cbe1cef380b3517cbd64727526e1b837df5160ba5275ccde6fec01324f4e
writer/status blob bytes 1,370
writer/status blob SHA-256 31590cfb05e4b02536ae288218108b066f9bf0b3d836117f2fb873d830b591bc
```

Private CI run 34170092288 passed protected inputs, build, ZIP integrity, artifact upload, and vault-root archival. Pending hardware confirmation; not golden.


### Test06b hardware result — FINAL EXPLICIT REFRESH UI MILESTONE PASS (2026-09-07)

Hardware confirmation completed successfully. The timed-status refinement works as intended and the user elected to keep the implementation exactly as-is for this milestone.

Confirmed on hardware:
- visible fourth User Menu item `Refresh` works;
- explicit Refresh integration remains stable;
- staged on-device SFC catalog refresh path remains successful;
- repeated refresh correctly reports `No New Games`;
- stock-font result feedback displays correctly;
- result feedback expires automatically after about three seconds and does not remain stuck after navigating away and returning;
- footer icons, active selector/A badge behavior, NTSC/PAL placement, and stock User Games/Language/TV System behavior remain correct.

Promote the exact tested Test06b artifact to golden:

```text
xgo-game-list-test06b-timed-status.zip
size 5,022,902 bytes
SHA-256 2d859b3ca3f0644a461c197fcfe0b58f2650c26bc6a7c8d28a189da196aa1042
firmware SHA-256 5d15cbe1cef380b3517cbd64727526e1b837df5160ba5275ccde6fec01324f4e
writer/status blob bytes 1,370
writer/status blob SHA-256 31590cfb05e4b02536ae288218108b066f9bf0b3d836117f2fb873d830b591bc
```

Important scope boundary: Test06b proves the explicit native-style Refresh command and the staged 929->930 writer/status lifecycle. It is intentionally NOT yet the final general filesystem scanner/stable-merge engine. Preserve this exact milestone before beginning that next stage.

Next-stage direction: start from this golden Test06b state and replace the staged `refresh.bin` proof mechanism with the real on-device discovery/stable-merge implementation while preserving the now-golden UI/feedback behavior. Do not reopen completed Test04/Test05/Test06 archaeology unless new hardware evidence requires it.


## Next-stage branch opened after Test06b milestone merge

The explicit Refresh Games milestone was merged to `main` by PR #39 at merge commit:

```text
5ac3036c16639d659c75bef554ab77b229c0d440
```

Fresh next-stage branch:

```text
research-game-list-general-scanner
```

Start the next chat by reading this file and `artifacts/golden-artifacts.json` from this branch. Repository evidence is authoritative.

Protected starting milestone is the exact hardware-confirmed private-vault golden artifact:

```text
xgo-game-list-test06b-timed-status.zip
size 5,022,902 bytes
SHA-256 2d859b3ca3f0644a461c197fcfe0b58f2650c26bc6a7c8d28a189da196aa1042
firmware SHA-256 5d15cbe1cef380b3517cbd64727526e1b837df5160ba5275ccde6fec01324f4e
```

Next engineering target: replace the staged `refresh.bin` 929->930 proof with the real on-device discovery + stable-merge scanner while preserving the now-golden explicit Refresh UI, status messages, three-second expiry, selector/footer behavior, PAL/NTSC placement, Favorites/save stability, and all prior golden emulator/audio behavior. Do not redo Test04-Test06b archaeology.


### Test07 candidate — real SFC discovery + stable merge (2026-09-07)

The first post-Test06b real scanner candidate is composed and offline-audited.

```text
xgo-game-list-test07-general-sfc-scanner.zip
size              4,995,560 bytes
ZIP SHA-256        0b07d1b4cd83b4a54b80740d646f85e72e3994598c19c089941b76ad56268719
firmware SHA-256   238331cf5cf56f9fb31891e197c12bfaa86a280a65dbeacc83e1b34d99c858c1
scanner/status     3,009 bytes
scanner SHA-256    9ef681888972c01bca94b50c0ea1a51df0f4246d9889ac007aa9907c3b1fe0c8
builder commit     d2ca23b21e3b909af48646c9bc7242f74f212b7c
```

Test07 starts directly from the exact golden Test06b ZIP and preserves the proven User Menu/UI/status resources. It replaces the staged writer with a real `/SFC` directory scan using the stock directory wrappers and stock extension classifier. It performs stable merge: existing entries/indices remain unchanged, only physical filenames absent from slot 0 are appended, with basename fallbacks appended to slots 1 and 2. All three outputs are constructed in RAM before canonical writes. The classifier global side effect is saved/restored.

Critical proof boundary: `Resources/refresh.bin` is absent from Test07. The expected 929->930 transition must therefore come from discovery of the physically present `SFC/XGO Import Test.zsf`.

Test07 is still deliberately non-transactional and is **NOT golden**. Hardware test only on the disposable clone; do not interrupt power during Refresh. First Refresh should report `Games Updated`, yield 930 entries, and expose/launch XGO Import Test. Second Refresh should report `No New Games`. Reboot/Favorite/save/Search/Chinese/UI/audio/SNES/CPS1 regressions remain part of the gate.

Primary finding:

`findings/game-list-test07-real-sfc-discovery-stable-merge-candidate.md`

The private-vault CI reproduction workflow is committed at `.github/workflows/xgo-game-list-test07-general-sfc-scanner.yml` in `jeborgesm/xgo-a10-artifacts`, but API-originated commits did not emit its configured push trigger in this session. Do not claim private-vault archival until an actual run or direct archive commit is confirmed.


### Test08 candidate — full FC/SFC/MD/GB/GBC/GBA scanner (2026-09-07)

**Test07 SFC-only is superseded before hardware testing. Do not test or promote Test07.**

Test08 is the active pending hardware candidate for the real built-in game-list scanner.

One Refresh pass now iterates all six ordinary built-in console directories:

```text
FC -> SFC -> MD -> GB -> GBC -> GBA
```

For each system the firmware resolves the synchronized triplet from stock table `0x80a3c32c`, scans the physical directory through the confirmed stock directory wrappers, filters by that system's wrapper/native extension classifier returns, stable-appends every filename absent from slot 0, appends basename fallbacks to slots 1/2, writes the complete synchronized triplet, fs-syncs, and invalidates only `count[list_id]` in the array at `0x80d2894c`.

No ROM filename, expected catalog count, or expected append count is hardcoded.

Candidate capacity is 512 additions per system. The preserved card inventory audit predicts 347 total discoveries on the captured stock state: FC 20, SFC 149, MD 45, GB 88, GBC 15, GBA 30. All projected final resource sizes stay well below the 64 KiB per-slot guard.

The install ZIP deliberately contains **no game-list catalogs and no test ROM payloads**. It contains only the patched firmware, the six protected Test06b User Menu UI resources, and the hardware-test README. Therefore installing Test08 does not itself reset/prepopulate any game list; mutations begin only when Refresh is invoked.

```text
xgo-game-list-test08-all-console-scanner.zip
size              4,921,057 bytes
ZIP SHA-256        9c66fd727a2f894ad692b4868ba8bcee3daf2ff81b4d7eced539f80f2fd2e61e
firmware SHA-256   45831b0ea3c9ae336d82b240e6afe27167e5e83b88037152af237ab758ca1444
scanner/status     3,601 bytes
scanner SHA-256    a3f965d0ccabc2238da240a4b05b5f8027c968e40ede1831b51c42cff374c01d
cave remaining     495 bytes
```

Exact reproducer:

`tools/game_lists/build_test08_all_console_scanner_candidate.py`

Primary finding:

`findings/game-list-test08-full-console-scanner-candidate.md`

Test08 is **NOT golden** pending hardware confirmation and remains deliberately non-transactional. Hardware test only on the disposable clone; do not interrupt power during Refresh.

Hardware gate:
- record FC/SFC/MD/GB/GBC/GBA counts before first Refresh;
- first Refresh should report `Games Updated` and append all accepted unindexed physical ROMs across all six systems;
- second Refresh should report `No New Games`;
- verify representative old Favorites/History/save references, Search, Chinese list/search alignment, and launches of newly discovered games from multiple console pages;
- confirm User Games/Language/TV System, timed status, Audio OSD, SNES and CPS1 protected behavior remain intact.

Arcade is intentionally out of Test08 scope because the shared `ARCADE` directory still requires safe per-wrapper family classification into CPS1/CPS2/NeoGeo/IGS curated pages.


### Test08 hardware PASS — real multi-system discovery confirmed (2026-09-07)

**Test08 passed hardware.**

The disposable-card test confirmed that one Refresh operation discovered and exposed previously unindexed games in multiple built-in console systems. This is the hardware proof of the real FC/SFC/MD/GB/GBC/GBA filesystem-discovery + stable-merge architecture.

Observed FC additions included `Bomberman 2` and `Home Alone`. Home Alone launches/plays correctly. Bomberman 2 remains non-working after being successfully indexed, so that title remains an emulator/game compatibility issue rather than a scanner failure.

The strongest accidental blind proof came from `/GB`: ordinary raw `.gb` files manually copied to the card long before this scanner work, and previously invisible to the stock main list, were rediscovered by Test08. `Super Mario Land (W) (V1.1) [!].gb` appeared in the normal GB list, launched successfully, played normally, and accepted the existing button-remapping mechanism. This validates native-extension discovery and stock launching without a scanner-specific test filename.

Newly discovered raw games currently have no automatic box art. Treat artwork association as a separate follow-up; it does not invalidate discovery/catalog/launch success.

Hardware result:
`findings/game-list-test08-hardware-pass.md`

Exact tested candidate remains:

```text
xgo-game-list-test08-all-console-scanner.zip
size              4,921,057 bytes
ZIP SHA-256        9c66fd727a2f894ad692b4868ba8bcee3daf2ff81b4d7eced539f80f2fd2e61e
firmware SHA-256   45831b0ea3c9ae336d82b240e6afe27167e5e83b88037152af237ab758ca1444
scanner SHA-256    a3f965d0ccabc2238da240a4b05b5f8027c968e40ede1831b51c42cff374c01d
```

Next engineering priorities after preservation/golden promotion:
1. transaction marker + backup/recovery for interruption-safe triplet updates;
2. box-art association for newly discovered games;
3. Arcade wrapper-family classification and safe shared-`ARCADE` scanning.


### Test08 GOLDEN promotion and branch closeout (2026-09-07)

Test08 full console scanner is now promoted to golden after hardware PASS.

Private vault:
- repository: `jeborgesm/xgo-a10-artifacts`
- golden path: `golden/xgo-game-list-test08-all-console-scanner.zip`
- vault promotion commit: `68600639c93c9c33acbae6afcd9c67c5f8410053`

Exact golden artifact:

```text
xgo-game-list-test08-all-console-scanner.zip
size              4,921,057 bytes
ZIP SHA-256        9c66fd727a2f894ad692b4868ba8bcee3daf2ff81b4d7eced539f80f2fd2e61e
firmware SHA-256   45831b0ea3c9ae336d82b240e6afe27167e5e83b88037152af237ab758ca1444
scanner SHA-256    a3f965d0ccabc2238da240a4b05b5f8027c968e40ede1831b51c42cff374c01d
```

Golden registry ID:
`game-list-test08-full-console-scanner`

The `research-game-list-general-scanner` branch is ready to merge into `main`.

Next branch objective:
`research-game-list-arcade-expansion`

Priority for that branch is arcade discovery and expansion, ahead of box-art work:
1. safely classify and refresh the existing CPS1/CPS2/NeoGeo/IGS curated pages from the shared `ARCADE` directory;
2. investigate adding arcade families not currently represented in the stock four curated groups;
3. target user-requested classics as concrete compatibility goals: Asteroids, Pac-Man, Ms. Pac-Man, Donkey Kong, Mario Bros., Frogger, and Galaga;
4. determine whether an existing stock arcade core can run any of those families or whether a new lightweight external arcade core/frontend is required;
5. preserve the golden Test08 six-console Refresh behavior while extending arcade support.

Box-art association remains deferred behind arcade expansion.


### Active branch — Arcade expansion (2026-09-07)

Current branch:

`research-game-list-arcade-expansion`

Branch base:

`a1bf54e96fc28b721a38d6920f0d4557dbd99730` — merged golden Test08 full console scanner.

The prior `research-game-list-general-scanner` milestone is closed, merged, archived, and golden. Do not reopen Test04-Test08 console scanner archaeology unless a regression is discovered.

Immediate priority is Arcade expansion, ahead of box-art work.

Existing curated pages to preserve/classify:
- list 7 CPS1
- list 8 CPS2
- list 9 NeoGeo
- list 10 IGS

Primary new compatibility targets:
- Asteroids
- Pac-Man
- Ms. Pac-Man
- Donkey Kong
- Mario Bros.
- Frogger
- Galaga

Research must first recover exact shared-`ARCADE` wrapper/family classification so existing CPS1/CPS2/NeoGeo/IGS additions can be refreshed safely. Then determine whether the stock arcade emulator already contains drivers for the requested classic families. If not, evaluate a lightweight external arcade core.

Prefer investigating inherited fifth `ARCADE` / list-ID-11 behavior as a possible native presentation surface for general/classic arcade games before inventing an entirely new screen.

Scope document:
`findings/arcade-expansion-scope-and-priority-targets.md`


### Arcade Test09 candidate — dormant list-ID 11 Pac-Man probe (2026-09-07)

Direct stock-binary inspection found a compiled Pac-Man/Ms. Pac-Man driver family in XGO's shipped FBA payload, including `pacman`, `mspacman`, `pacplus`, `puckman`, and associated ROM descriptors such as `pacman.6e`, `pacman.6f`, `pacman.6h`, `pacman.6j`, and `mspacatk.*`.

Canonical identifiers for Galaga, Frogger, Donkey Kong, Mario Bros., and Asteroids were not found in the same XGO binary scan. Do not assume upstream FBA 0.2.97.42 coverage means those modules were compiled into this device.

The fifth repeated ARCADE entry remains list ID 11 with `None / None / None` as its resource triplet. Test09 probes whether supplying a valid `Resources/None` activates that native page without any firmware patch.

Exact Test09 package:

```text
xgo-arcade-test09-id11-pacman-probe.zip
size       4,922,444 bytes
SHA-256    f2b6b2c127effc554f882190648f84ab7cba4a1f026a74a1ccbaf042d0768ba6
```

Golden Test08 firmware is unchanged.

Added:
- `Resources/None`: one-entry stock catalog containing `Pac-Man.zfb`;
- `ARCADE/Pac-Man.zfb`: blank-thumbnail XGO arcade reference record pointing to `pacman.zip`;
- hardware-test README.

No ROM image is included. Hardware testing requires the user to place their own compatible `ARCADE/bin/pacman.zip`.

Builder:
`tools/game_lists/build_arcade_test09_id11_pacman_probe.py`

Finding:
`findings/arcade-test09-id11-pacman-probe.md`

Interpretation:
- fifth page + successful launch => native general/classic Arcade page and stock Pac-Man path proven;
- fifth page + launch failure => page path proven, isolate ROM-set/driver launch;
- fifth page absent => additional ID-11 gate exists and frontend patching is required.


### Correction — only four visible Arcade pages (2026-09-07)

Direct hardware observation confirms the XGO frontend exposes only four Arcade pages.

The fifth inherited `ARCADE` definition in `Foldername.ini` and list ID 11 = `None / None / None` do **not** correspond to a currently visible fifth Arcade page. Treat ID 11 as a dormant inherited placeholder unless/until frontend navigation is explicitly extended.

Therefore Arcade Test09 (`Resources/None` + Pac-Man probe) is **superseded before hardware test** and should not be used as-is.

Next research target:
- trace the visible Arcade page navigation/selector;
- identify the exact four-page bound and associated resource/list-ID mapping;
- deliberately extend it to a real fifth Classic Arcade page backed by list ID 11 or another safe slot;
- then use Pac-Man/Ms. Pac-Man as the first stock-driver launch proof.

Do not overload CPS1/CPS2/NeoGeo/IGS long-term merely to avoid creating the proper Classic Arcade page.


### Arcade Test10 hardware PASS — fifth Arcade and stock Pac-Man execution (2026-09-07)

Test10 passed hardware.

Changing `Foldername.ini` active-section count `11 7 0 -> 12 7 0` exposes a real fifth Arcade section. The fifth page is therefore an inherited but disabled native category, not a hypothetical frontend slot.

Observed presentation:
- fifth category is visible but inherits CPS2 artwork;
- `Resources/None` loads successfully as list ID 11 and shows Pac-Man;
- Pac-Man has no thumbnail because Test10 intentionally supplied a blank `.zfb` thumbnail;
- lower system/banner artwork is scrambled/invalid, confirming list ID 11 lacks a complete valid presentation-resource mapping.

Observed execution:
- Pac-Man launches from `ARCADE/bin/pacman.zip`;
- gameplay and controls work;
- pause menu works normally;
- **audio is silent**.

This proves the stock XGO FBA Pac-Man driver is executable. Silent audio is now a focused classic-driver/audio-path problem, separate from category/list/wrapper/launch correctness.

Hardware finding:
`findings/arcade-test10-hardware-pass.md`

Next priorities:
1. fix fifth-category Classic Arcade presentation resources;
2. trace/fix Pac-Man audio;
3. inventory all non-CPS/NeoGeo/IGS drivers compiled into stock XGO;
4. test Ms. Pac-Man next because it belongs to the now-proven compiled Pac-Man family;
5. continue Galaga/Frogger/Donkey Kong/Mario Bros./Asteroids coverage analysis; use external/lifted core only where stock driver modules are genuinely absent.


### Arcade Test11 candidate — Pac-Man audio A/B by list ID (2026-09-07)

Test10 proves Pac-Man gameplay works from list ID 11 but is silent.

Static comparison shows Pac-Man's frame routine reaches the shared stock FBA sound-output helper, so Test11 isolates frontend/list setup from driver-level sound.

Test11 keeps the Test10 fifth Arcade Pac-Man entry and temporarily appends the exact same `Pac-Man.zfb` to list ID 7 / CPS1.

Both entries resolve to the same `ARCADE/bin/pacman.zip`.

```text
xgo-arcade-test11-pacman-audio-ab.zip
size       4,923,915 bytes
SHA-256    a1a77ae81427b4623023419d0d55b74a08ff13224528ba736a02a23d6de42976
```

Hardware interpretation:
- sound on list 7 but not list 11 => dormant fifth page lacks/gets wrong audio initialization;
- silent on both => compiled Pac-Man/Namco sound path itself is incomplete/broken in stock XGO;
- list-7 launch failure => active Arcade subtype affects deeper runtime setup.

Finding:
`findings/arcade-test11-pacman-audio-ab.md`

The temporary CPS1 Pac-Man entry is diagnostic only, not the intended final organization.

Stock-binary inventory also confirms compiled classic-era driver data beyond the four exposed stock families, including Pac-Man/Ms. Pac-Man, Phoenix, 1942/1943, Arkanoid, Pooyan, Route 16 and Mr. Do! families. Continue inventory after the audio A/B result.


### Arcade Test11 hardware PASS — silence follows Pac-Man driver, not list ID (2026-09-07)

Test11 A/B is complete.

The exact same Pac-Man content was launched from:
- fifth Arcade / list ID 11;
- first Arcade / CPS1 list ID 7.

Both paths produce normal playable Pac-Man with working controls and pause menu, but **no audio**.

A second Pac-Man ROM-set variant (~27.7 KB vs ~13.8 KB original) also produces the same playable-but-silent behavior.

Therefore list ID 11 is ruled out as the primary audio cause. The leading defect is inside the compiled Pac-Man/Namco sound path or its interaction with the XGO vendor FBA wrapper.

Hardware finding:
`findings/arcade-test11-hardware-audio-ab-pass.md`

Next test should compare other dormant classic drivers using different sound hardware to determine whether silence is Namco-specific or general to hidden drivers.


### Arcade Test14 — Ms. Pac-Man stock FBA FAIL; pivot fifth Arcade to MAME2000 (2026-09-07)

Hardware result:
- Pac-Man remains playable/video-correct but silent under stock XGO FBA.
- Ms. Pac-Man launches but has severely corrupted/glitched video and no audio.
- User supplied photographic evidence of the corrupted Ms. Pac-Man runtime.

Conclusion: stranded classic drivers inside stock XGO FBA are useful archaeology but are not reliable enough to build the requested Classic Arcade library.

Architectural pivot:
- keep stock FBA untouched for CPS1/CPS2/NeoGeo/IGS;
- keep the proven fifth Arcade/list-ID-11 frontend as the Classic Arcade category;
- route list ID 11 to a dedicated external MAME2000 core.

Important prior-context correction: MAME2000 was previously rejected as a **CPS1/SFII performance replacement**, not as a general classic-arcade core. The XGO external MAME2000 integration already reached playable SFII with repaired input and frontend integration, but portable CPS1 emulation was too slow. That does not predict performance for much lighter Pac-Man/Galaga/Frogger/Donkey Kong/Asteroids-era hardware.

Next engineering target: reuse the proven XGO MAME2000 external-core infrastructure, gate it on list ID 11 only, and build a Pac-Man/Ms. Pac-Man 0.37b5 proof while preserving stock arcade lists 7-10.

Finding:
`findings/arcade-test14-mspacman-fail-mame2000-pivot.md`


### Arcade Test15 candidate — list-ID 11 external MAME2000 (2026-09-08)

Test15 is the first Classic Arcade candidate that stops relying on the broken stranded Pac-Man-family stock FBA drivers.

Architecture:
- list IDs 7-10 remain untouched stock XGO FBA;
- list ID 11 / fifth Arcade routes to external MAME2000 only;
- golden Test08 console Refresh remains the firmware baseline.

The loader is injected into the currently verified zero cave `0x80001900..0x8000217f` and intercepts the real stock arcade runtime call at `0x80360df8`.

```text
loader size       1,325 bytes
loader SHA-256    74046302713cd575a3b3db8abebb00e656c9dd7fb7c33a6bc1b66094c71ebd0e
MAME2000 core     9,127,952 bytes
core SHA-256      abf8e4ec6eb7c6d4c2162076e8faa868954a3663b8210c820e1267857b345461
candidate ZIP     7,400,598 bytes
candidate SHA-256 20cba65613463f68fb6d9ee7bf4ef2b7dc1ac2f86423dda4a50620e339fd0097
firmware SHA-256  7ade9be3609ce74add4ffd217e4f48ff077e3ce50420670854315941dc7bff50
```

The external core is the already hardware-proven MAME2000 Test12 XGOC, with repaired XGO input filtering and isolated MAME state namespace.

Fifth-page entries:
- `Pac-Man.zfb -> ARCADE/bin/pacman.zip`
- `Ms Pac-Man.zfb -> ARCADE/bin/mspacman.zip`

No ROMs are included. Prefer MAME2000 / MAME 0.37b5-compatible sets.

Private CI run `34188223200` passed all build/audit/ZIP checks and archived the candidate; workflow artifact ID `10041265802`.

Finding:
`findings/arcade-test15-mame2000-classic-candidate.md`

Hardware priorities:
1. verify lists 7-10 still run stock;
2. test Pac-Man and Ms. Pac-Man in fifth Arcade for speed/video/audio/controls/pause/quit;
3. if successful, expand Classic Arcade to Galaga/Frogger/Donkey Kong/Mario Bros./Asteroids.


### Arcade Test15 hardware FAIL; Test16 runtime-list diagnostic ready (2026-09-08)

Test15 hardware result:
- Pac-Man -> black screen, device unresponsive;
- Ms. Pac-Man -> black screen, device unresponsive;
- no usable pause/quit recovery.

This is classified as external-core integration/runtime failure, not evidence that MAME2000 cannot emulate the games.

Repository evidence re-confirms the stock Arcade path globals are already resolved before the runtime hook, so the leading Test15 mismatch is now the active frontend list identity. Old proven MAME2000 Test12 ran as list ID 7; new Classic Arcade runs as dormant list ID 11.

Test16 changes only the loader runtime identity:
- frontend remains fifth Arcade/list 11;
- loader gates on list 11;
- immediately before external MAME entry, ACTIVE_LIST_ID is temporarily set to 7;
- after core return it is restored to 11;
- lists 7-10 remain stock FBA.

Exact Test16 candidate:

```text
xgo-arcade-test16-mame2000-classic.zip
size              7,400,685 bytes
ZIP SHA-256        2c7ee9ad37c916d01d7b2425c99140c31f35b37ec3affea2cfca71acd9418ce7
loader SHA-256     be020660480cc22da4a29ae820577721d47596aa1c5f566b5d2260078f57a37d
MAME2000 SHA-256   abf8e4ec6eb7c6d4c2162076e8faa868954a3663b8210c820e1267857b345461
firmware SHA-256   09eb51ed55a620439bd42e1f701a4bb9a1e4e77778a14c2d623c1570cf082e1d
```

Private CI run `34238269652` passed and archived the candidate; artifact ID `10060835366`.

Findings:
- `findings/arcade-test15-hardware-fail-black-screen.md`
- `findings/arcade-test16-mame2000-runtime-list-spoof-candidate.md`


### Arcade Test16 FAIL; Test17 persistent core trace ready (2026-09-08)

Test16 hardware result is identical to Test15 for both Pac-Man and Ms. Pac-Man:

```text
select game -> Loading..... -> black screen -> frozen device
```

No pause menu, no volume OSD, no recovery path. Runtime list-ID spoofing is therefore ruled out.

Test17 stops changing emulator behavior and instruments the external MAME2000 core with persistent SD-card checkpoints.

The loader remains the proven-size Test16 loader because loader-side file tracing exceeded the verified firmware cave. The traced core creates fs-synced files at SD root:

```text
MAME17-11.txt  entered core C entry
MAME17-12.txt  C/newlib runtime init complete
MAME17-13.txt  ROM path constructed
MAME17-14.txt  before retro_init
MAME17-15.txt  retro_init returned
MAME17-16.txt  immediately before stock run_emulator
MAME17-17.txt  stock run_emulator returned
```

No `MAME17-11.txt` after the freeze means the failure occurs before core C entry and the next work belongs at the loader/control-transfer/cache boundary.

Exact diagnostic:

```text
xgo-arcade-test17-mame2000-stage-trace.zip
size              7,400,929 bytes
ZIP SHA-256        6e15e251c10193ca0a09aba278d467ed00f191d5b7f322bb27e7185e894c3e24
firmware SHA-256   9e9268226ed7315acf838180d68c9de138fce9dd4f80233cb65a55a2bb4585be
loader SHA-256     3e4207b31d608275f5fad0592c73e4072f9f8431967864e623a980f3fce05179
traced core SHA-256 20519be70fe6ca8a35a58e7eb0ade2195fd1fdc04095cc641bd06ab249be100f
```

Private CI run `34242919132` passed and archived the candidate; workflow artifact ID `10062878283`.

Finding:
`findings/arcade-test17-mame2000-persistent-stage-trace.md`

Hardware procedure: test Pac-Man only, hard-power after freeze, inspect SD root, and report the highest numbered `MAME17-xx.txt` file present. If none exists, explicitly report that no MAME17 checkpoint file was created.


### Arcade Test17 hardware FAIL — pre-core-entry; Test18 loader-only trace queued (2026-09-08)

Hardware result:
- Pac-Man and Ms. Pac-Man freeze on the stock `Loading.....` screen under Test17;
- no `MAME17-11.txt` through `MAME17-17.txt` core-entry checkpoint files are created.

Conclusion: the external MAME2000 C frontend is never reached. The active failure domain is now the pre-entry loader/handoff sequence, not ROM driver execution, retro_init, or the stock run_emulator loop.

Test18 removes core-side tracing entirely and restores the exact original hardware-proven Test12 MAME2000 core. Only the list-ID-11 loader is instrumented.

The loader writes a single byte to:
`/mnt/sda1/MAME17-L.txt`

Stage byte meanings:
- A = loader entered
- B = XGOC header read
- C = immediately before stock sound-task shutdown
- D = sound-task shutdown returned
- E = RAMSIZE ceiling moved
- F = core payload copied
- G = payload CRC passed
- H = IRQ-GP repair completed
- I = cache flush completed
- J = immediately before external core entry jump

This single-byte trace is intentionally much less invasive than Test17's core-side filesystem checkpoints.

Private artifact workflow:
`.github/workflows/xgo-classic-arcade-mame2000-test18-loadertrace.yml`

Workflow run:
`34247530169`

As of this handoff update the Test18 workflow is queued; do not invent or claim a candidate hash until the run completes.


### Exact Test12-vs-Test08 MAME differential; Test20 ready (2026-09-08)

A private-vault byte comparison between the hardware-working MAME2000 Test12 firmware and golden Test08 closed several hypotheses.

Byte-identical stock-service windows:
- fopen/fread/fclose;
- dly_tsk;
- retro video/audio/input/environment callbacks;
- run_fba @ 0x80360848;
- arcade cleanup @ 0x80360e00;
- osd_region_write.

Low-memory map:
- mapper 0x800014a0..0x800018ff identical;
- 0x80001900..0x8000217f zero in both images;
- SNES loader 0x80002230..0x8000277f identical.

Therefore the relocated Classic Arcade loader cave is not overlapping protected mapper/SNES code.

Critical divergence:
- `run_emulator @ 0x8035ed48` differs between Test12 and golden Test08.
- first changed instruction is `0x8035ed6c`: Test12 original setup instruction vs golden Audio-OSD game-enter hook.
- golden firmware also includes the later hardware-confirmed sibling wall-time scheduler transplant inside run_emulator.
- MAME2000 Test12 was never validated under those later runner changes.

Primary finding:
`findings/arcade-mame-test12-vs-test08-runtime-differential.md`

Test20 is a narrow diagnostic:
- base = exact golden Test08;
- fifth Arcade/list 11 retained;
- clean list-11 loader retained;
- exact hardware-proven Test12 MAME2000 core retained;
- only `run_emulator 0x8035ed48..0x8035f2b3` is restored byte-for-byte from working Test12.

```text
xgo-arcade-test20-mame2000-test12-runner.zip
size              7,400,664 bytes
ZIP SHA-256        65de1d19d5aa2781515d4022930c722fc2265a7d42fb1fb1ed462afa7e6c1476
firmware SHA-256   9464c50fc3f3af4ea21072c85af6958d3b77dfb1d4390ef66401742dcd4f53b4
loader SHA-256     74046302713cd575a3b3db8abebb00e656c9dd7fb7c33a6bc1b66094c71ebd0e
MAME2000 SHA-256   abf8e4ec6eb7c6d4c2162076e8faa868954a3663b8210c820e1267857b345461
restored runner    1,388 bytes
runner SHA-256     a7c398141c1b7c706f653a847fab09480917ef84c469160a50560fb825b54078
```

No trace writes and no visual tracing.

Hardware procedure:
- test Pac-Man first;
- do not press Volume while the game is running because Test20 temporarily removes the newer Audio-OSD game-session hooks from run_emulator;
- if Pac-Man reaches gameplay, later run_emulator changes are confirmed as the regression surface;
- if black-screen/freeze remains, the runner differential is ruled out and focus returns to loader/core transfer.


### Test20 hardware FAIL; Test21 loader round-trip probe ready (2026-09-08)

Test20 restored the exact hardware-working Test12 `run_emulator()` body while keeping golden Test08, list 11, the clean Classic Arcade loader, and the exact Test12 MAME2000 core.

Hardware result:
```text
Pac-Man
 -> Loading.....
 -> black screen
 -> frozen/unresponsive device
```

Therefore the later Audio OSD/session hooks and sibling scheduler transplant inside `run_emulator()` are ruled out as the Classic Arcade MAME regression source.

A source-level differential between the hardware-working Test12 CPS1 loader and the current Classic Arcade loader shows the pre-entry machinery is otherwise effectively identical:
- XGOC validation;
- sound-task shutdown;
- RAMSIZE ceiling move;
- payload copy;
- payload CRC;
- BSS zero;
- IRQ-GP repair;
- cache flush;
- entry call.

Meaningful differences are only list gate, core pathname, and the old continuity-return handshake.

Test21 therefore removes MAME entirely and reuses the hardware-proven 16-byte XGO1 continuity payload:

```asm
lui v0,0x5847
ori v0,v0,0x4f31
jr ra
nop
```

The Test21 loader is derived directly from the proven CPS1 loader, gates list ID 11, reads `/cores/mame2000/core.xgc`, and restores the old handshake:

```text
loader -> 0x87000000 probe -> returns XGO1
 -> restore RAMSIZE
 -> launch same Pac-Man through stock run_fba
```

Hardware PASS shape:
`Loading -> ordinary stock Pac-Man` (mute is acceptable/expected from prior hidden-stock-Pac-Man tests).

Hardware FAIL shape:
freeze before stock Pac-Man appears.

Exact candidate:
```text
xgo-arcade-test21-loader-roundtrip-probe.zip
size              4,922,310 bytes
ZIP SHA-256        19dcb2d562e7e087bb6a2f61d6a7819464bc435c6f48d4fa94c4284d144a6a67
firmware SHA-256   f10c0258fac38bd0e05514934b3c863275971c5cea34ce612b7f467e1b5c9b54
loader SHA-256     3b54123155b22e8e739a0a85a8ecf88e689eed50e29956501641afd138236eae
probe XGOC SHA-256 aac9310c13d6330270e17b8fd417cfbfaefebfbdc197a2a46a7567c384ac7802
```

Private CI run `34260753277` passed; artifact ID `10069783018`.


### Major pivot — lift family-proven SF2000/GB300 MAME2000 path (2026-09-08)

Family research confirms a working MAME2000 implementation already exists on closely related HC15xx devices.

Sources:
- madcock/sf2000_multicore
- madcock/sf2000_multicore_cores
- tzubertowski/gb300_multicore

SF2000 Multicore ships MAME2000 as `m2k`; GB300 Multicore also ships `m2k` and inherits the same architecture. Family documentation uses MAME 0.37b5 sets and reports broad classic-arcade coverage, though performance is worse than stock FBA for larger games.

Critical architecture difference from our current XGO bridge:

Family proven path:
```text
loader
 -> raw core_87000000 loaded directly at 0x87000000
 -> core entry clears BSS + initializes libc/ctors
 -> returns struct retro_core_t API table
 -> loader installs stock callbacks
 -> retro_init
 -> populate stock game-info/globals
 -> stock run_emulator
```

The family does NOT use our XGOC + custom MAME frontend model.

Most important runtime difference:
SF2000 Multicore patches the IRQ path with a live `restore_stock_gp` JAL so every interrupt re-establishes the firmware GP. Our current XGO bridge only copies the stock GP-init instructions into the IRQ path once. The tiny Test21 XGO1 probe can succeed without stressing this, while a full MAME runtime can freeze under interrupt activity.

New primary direction:
- stop the custom MAME staged-return ladder;
- port the family multicore loader/core_api contract to XGO list ID 11;
- use raw family-format `m2k/core_87000000`;
- adapt stock firmware addresses to known XGO equivalents;
- implement family-style IRQ GP restoration;
- keep lists 7-10 stock FBA;
- test Pac-Man/Ms. Pac-Man with MAME 0.37b5 sets.

Finding:
`findings/family-proven-mame2000-sf2000-gb300-lift-target.md`


### Test23 family-style MAME2000 candidate ready (2026-09-08)

The family/API-table port now builds and packages cleanly.

Architecture:
- golden Test08 remains baseline;
- lists 7-10 remain stock XGO FBA;
- list 11 routes to external MAME2000;
- external image exposes family-style `retro_core_t` API ownership;
- golden XGO callbacks and `gfn_retro_*` slots are installed;
- golden `run_emulator()` owns the runtime loop.

Preserved golden functionality:
- Volume OSD v8;
- gray border and timeout behavior;
- CPS1 sibling scheduler;
- mapper v19;
- native SNES;
- Refresh Games / multi-system scanner;
- stock pause/menu behavior.

The candidate retains the XGO MAME admin/service-key patch and Test12 isolated-state patch.

Exact candidate:
```text
xgo-arcade-test23-family-api-mame2000.zip
size              7,378,684 bytes
ZIP SHA-256        99c591ac0f9c61096997503adb328b3634ca080e79124d338b4ff3aeeb114b8a
firmware SHA-256   98f044cc661ebd63f2b332638c72109bcc4a04a527d8ca4cc3ee3b71c2bb59ed
core SHA-256       62114aeb11035a72111e67fa86c58f47937d4d7e78af220989097d00a914495d
```

Private CI run `34271682744` passed; artifact ID `10074162355`; archive commit `7130e05`.

Finding:
`findings/arcade-test23-family-api-mame2000-candidate.md`

Hardware test order:
1. verify Volume OSD in menu;
2. verify one stock Arcade game from lists 7-10, including audio/pause/OSD;
3. test Pac-Man on list 11;
4. if Pac-Man works, test Ms. Pac-Man.


### Test23 hardware bounce-back explained; Test25 true family candidate ready (2026-09-08)

Test23 hardware:
- Cadillac & Dinosaurs remains normal on stock Arcade path.
- Pac-Man and Ms. Pac-Man on fifth Arcade show `Loading.....` then cleanly return to list 11.
- no black-screen freeze.

Postmortem:
Test23's family frontend was dead-stripped by linker GC. The upper-RAM entry returned a `retro_core_t *` API table, but the low loader still used the old `entry(filename,load_state)` ABI and ignored the return value. Therefore the clean bounce-back is explained by an incomplete family transplant, not MAME rejecting the ROM.

Test24 rebuilt the same dead architecture and should not be hardware-tested.

Test25 implements the actual family contract:
- low list-11 loader captures `retro_core_t *`;
- builds stock-resolved `<system>/bin/<archive>` using 0x810a0eb0 + 0x8109fce8;
- installs XGO stock callbacks through the API table;
- calls `retro_init`;
- populates golden `g_retro_game_info` / `gfn_retro_*`;
- golden `run_emulator()` owns runtime;
- deinit + full callback/global restoration afterward;
- lists 7-10 remain stock FBA.

Upper MAME wrapper retains:
- XGO admin/service-key patch;
- Test12 isolated-state patch;
- joypad-only filtering;
- family L+R fold-down into internal first channel while retaining second channel.

Golden Test08 remains the base; Volume OSD, scheduler, mapper, SNES, scanner, pause/menu are not reverted.

Exact candidate:
```text
xgo-arcade-test25-true-family-mame2000.zip
size              7,400,397 bytes
ZIP SHA-256        927d6a33a42d8ddc239e64575ab19e07341d99a101051e3ddb202e9d0b5c5e8a
firmware SHA-256   9faddef2648868b856a2be084376cb7e3204505ae113fcefe1f884ae8957f316
loader size        2,009 bytes
loader SHA-256     bac994cd65c8da55fdc49b5cc92ad0aff7a4b2abf98086fab51f5b7d5e3277c1
core size          9,124,304 bytes
core SHA-256       14a5303decb74df31d9c05c1c6336f57447d7f0cc6bb29e4501d621fe4e3eb5c
```

CI run `34276092808` passed; artifact ID `10075859223`; artifact archive commit `13f0869`.

Finding:
`findings/arcade-test23-postmortem-test25-true-family-candidate.md`


### Test25 hardware FAIL; Test26 recovered-Test12 compatibility candidate ready (2026-09-08)

Test25 true-family MAME2000 hardware result:

```text
Pac-Man -> Loading..... -> black screen
```

The recent family API-table direction is closed for the immediate Classic Arcade implementation.

Repository archaeology re-established the older authoritative XGO result: MAME2000 Test12 was a physical-hardware PLAYABILITY PASS. SFII and Cadillacs reached real MAME gameplay; input was repaired; Test12 isolated poisoned MAME state. The remaining Test12 defect was CPS1-wide slow-motion/choppy-audio performance, not failure to boot.

Test26 therefore stops reimplementing MAME ownership and wraps the exact historical Test12 path:

- base = exact golden Test08;
- exact archived Test12 MAME2000 core, SHA-256 `abf8e4ec6eb7c6d4c2162076e8faa868954a3663b8210c820e1267857b345461`;
- historical Test12-era CPS1 loader source from commit `3470f0e320f47fb7deef5f64f7c0346b21adb4e8`;
- original core path retained: `/mnt/sda1/cores/fbalpha2012_cps1/core.xgc`;
- list 11 enters through an 88-byte compatibility shim at `0x80001900`;
- shim temporarily changes ACTIVE_LIST_ID 11 -> 7 and calls the relocated historical loader at `0x80001980`;
- after MAME returns, shim restores list 11 and returns into untouched stock arcade cleanup;
- lists 7-10 tail-jump directly to untouched stock `run_fba`;
- no family `retro_core_t` API-table frontend and no new MAME core build.

Exact Test26:

```text
xgo-arcade-test26-test12-compat-shim.zip
size              7,400,813 bytes
ZIP SHA-256        15bb71a267181fa2260a6be03de3252d09ef9211d4bdf151f18d8740ca569a24
firmware SHA-256   3cd4b957fe558475a5a5519281b4bbcc96a7e5c06ac8fc607b2ee0e871b55934
shim SHA-256       99eb1a504a09c995c97d6cb4c7f080ab8857aea224cd18a12d21dfb89b7cbc67
loader SHA-256     0231bd3f132bc79a885bd5090592f54984393dc08ca5b57cb4f7d38e5ecb0921
core SHA-256       abf8e4ec6eb7c6d4c2162076e8faa868954a3663b8210c820e1267857b345461
```

Private CI run `34283009246` passed; artifact ID `10078376651`; candidate archived in the private vault.

Finding:
`findings/arcade-test25-fail-test26-test12-compatibility.md`

Hardware order: verify golden stock behavior, then Pac-Man on fifth Arcade. If Pac-Man reaches gameplay, test audio/controls/pause/quit/OSD/speed and then Ms. Pac-Man. Do not create another speculative loader ladder if Test26 fails; first close any relocation-specific difference against the exact historical Test12 loader binary.


### Test27 — first-class CLASSIC list11 candidate ready (2026-09-08)

After Test26 repeated the same `Loading..... -> black` failure even with a different ROM renamed to Pac-Man, list11 itself became the primary suspect.

Repository archaeology confirmed list11 was a dormant placeholder: its fixed metadata triplet was literally `None / None / None`, unlike real lists 7-10.

Test27 converts list11 into a genuine stock-style category:

- fifth visible page renamed from repeated `ARCADE` to `CLASSIC`;
- dedicated directory tree:
  - `CLASSIC/Pac-Man.zfb`
  - `CLASSIC/Ms Pac-Man.zfb`
  - `CLASSIC/bin/pacman.zip`
  - `CLASSIC/bin/mspacman.zip`
- firmware list11 metadata pointers rewired to three real synchronized resource names:
  - `clm.tax`
  - `clm.nec`
  - `clm.bvs`
- list11 launch aliases to list7 **before stock `run_game()`**, so the full proven CPS1 preprocessing/state lifecycle executes;
- a private launch flag makes the final arcade runtime dispatcher route only the aliased list11 session to the historical Test12 MAME loader/core;
- true list7 stays golden stock CPS1/FBA;
- lists 8-10 stay golden stock;
- exact archived Test12 MAME2000 core is reused.

Exact candidate:

```text
xgo-arcade-test27-first-class-classic.zip
size              7,401,357 bytes
ZIP SHA-256        36e34502d9c3e038ca949630334864775ab7f605cad2a18c319a8efc147e1a2c
firmware SHA-256   2319f1f1bce604da3ee8d25eef40a629af49932fb8f9499f518d5d2eec6cbec8
core SHA-256       abf8e4ec6eb7c6d4c2162076e8faa868954a3663b8210c820e1267857b345461
```

Private CI run `34298562078` passed; artifact ID `10084069779`.

Important install difference from Tests15-26:

```text
ROMs must be placed in /CLASSIC/bin/
not /ARCADE/bin/
```

Finding:
`findings/arcade-first-class-list11-classic-design.md`

Hardware gate:
1. verify fifth page now visibly says CLASSIC;
2. verify Pac-Man and Ms Pac-Man rows appear;
3. verify golden Cadillacs/CPS1 still launches normally from stock Arcade;
4. place pacman.zip in CLASSIC/bin and launch Pac-Man;
5. if gameplay starts, test controls/audio/pause/quit/OSD and then Ms Pac-Man.


### Test28 — native first-class CLASSIC system ready (2026-09-08)

Test28 abandons all CLASSIC->Arcade/list7 compatibility plumbing.

CLASSIC is list ID 11 only because the frontend already has that menu slot. It now owns:

- fixed triplet `clm.tax / clm.nec / clm.bvs`;
- `/CLASSIC/` wrapper directory;
- `/CLASSIC/bin/` ROM directory;
- dedicated native launcher;
- exact archived Test12 MAME2000 core.

Generic browser launch calls route through the native launcher. If `ACTIVE_LIST_ID != 11`, it immediately calls untouched stock `run_game @ 0x80360b88`.

For list11, it bypasses stock Arcade entirely: opens the selected CLASSIC `.zfb`, reads the embedded ZIP basename at offset 59908, writes `/mnt/sda1/CLASSIC` and the ZIP name into the two globals expected by the proven Test12 MAME frontend, loads the exact Test12 core, performs the proven external-core memory/IRQ/cache handoff, and enters Test12. No stock Arcade preprocessing, no list7 alias, no Arcade runtime hook.

Test27's disappearing-page regression was caused by changing the menu control line. Test28 restores the last-known-visible values exactly (`12 7 0 / 472 144 144 208 / 40 24`) and changes only the fifth label from ARCADE to CLASSIC.

Exact candidate:

```text
xgo-classic-test28-native-system.zip
size              7,401,889 bytes
ZIP SHA-256        c60f8b4760db48a33db14f90d9211051be2915bb39c8474cddfb4d3bb0fd82d3
firmware SHA-256   ca799f4fc727bb04368b2171075e799f2262d2475cd19df3ffa87cbe64337367
launcher SHA-256   1a2c98bbd0ab126efaae8e6cfc1280183b545ef2013b22b4864fe7ba77d2df61
core SHA-256       abf8e4ec6eb7c6d4c2162076e8faa868954a3663b8210c820e1267857b345461
```

CI run `34299726436` passed; artifact ID `10084477699`.

ROM placement:
`/CLASSIC/bin/pacman.zip`
`/CLASSIC/bin/mspacman.zip`

Finding:
`findings/classic-test28-native-first-class-system.md`


### Test29 — CLASSIC path dispatch + dedicated artwork (2026-09-08)

Test28 hardware:
- CLASSIC page visible;
- Pac-Man / Ms Pac-Man visible;
- selecting either: Loading.... -> return to game list;
- CLASSIC still showed CPS2 artwork.

Static analysis found the stock platform-art pointer table at 0x80a3c428. List11 lands on a CPS2 fallback pointer at firmware offset 0x00a3c454. Test29 repoints only list11 to a new resource, Resources/clssic.r56. Real CPS2/list8 remains untouched.

The custom resource is a native 640x480 RGB565 conversion of the user-selected CLASSIC/Pac-Man crop, aspect-preserved at 397x480 and centered with black sidebars.

Test28 launch gating on ACTIVE_LIST_ID was also removed. Test29 uses the full wrapper path already passed by the browser:
- path contains /CLASSIC/ -> native CLASSIC launcher;
- otherwise -> untouched stock run_game.

Exact candidate:

```text
xgo-classic-test29-path-launch-custom-art.zip
size              7,477,721 bytes
ZIP SHA-256        d96b4d7d06f46d56c6b7e06c45adcf32d09ae0b9681bfc17ce7b0910d66e7241
firmware SHA-256   48a9bf4e5a3efdd2317028a1c5bbc4332d9b7dc006a0860f1c8b26848bf5f5f8
launcher SHA-256   850fa1f1303d990bd141c8144bcd149d6764d808834c3372d803d57fb36fcac4
art SHA-256        00ecf4913ee58b46f642f05ea150ffa1d67cd5a36d6674f44aedc5dedffd6cd0
core SHA-256       abf8e4ec6eb7c6d4c2162076e8faa868954a3663b8210c820e1267857b345461
```

Finding:
`findings/classic-test29-path-dispatch-custom-art.md`

Hardware gate: confirm custom CLASSIC art, confirm stock CPS2 art unchanged, confirm stock CPS1/Cadillacs golden, then launch Pac-Man from CLASSIC.


### Test30 — Cadillac baseline + launch trace + artwork fit (2026-09-08)

Test29 hardware kept CLASSIC visible and dedicated artwork working, but Pac-Man still failed to launch.

Test30 adds the hardware-proven MAME2000 baseline Cadillacs and Dinosaurs:
- wrapper: `CLASSIC/Cadillacs and Dinosaurs.zfb`
- archive basename: `dino.zip`
- user must place `/CLASSIC/bin/dino.zip`

CLASSIC catalog now has Pac-Man, Ms Pac-Man, and Cadillacs and Dinosaurs.

Test30 also writes `/CLASSIC/launch.stg` as a one-byte launch-stage marker:
- A = CLASSIC launcher entered
- B = wrapper parsed / ZIP basename extracted
- E = core loaded + CRC verified + IRQ/cache handoff complete, immediately before Test12 entry
- F = Test12 core returned

This turns a failed hardware launch into actionable evidence instead of another blind result.

Artwork is also revised: the user-selected 385x465 Pac-Man crop is vertically cropped to 385x360, scaled to about 513x480, and centered in the native 640x480 RGB565 canvas. This reduces top/bottom content and makes the artwork visibly wider. Only CLASSIC artwork changes.

Exact local candidate:

```text
xgo-classic-test30-cadillac-trace-art.zip
size              7,547,515 bytes
ZIP SHA-256        25ee41ac0ced58496fa1746e11473e0ff86b8903bc4d399ca26a2c6d2030b13e
firmware SHA-256   f4168fc129b18b454fb3fda3391e3423a3106bbee2e100e424a94b73839f6d66
launcher SHA-256   af9d984fa9827fd9840d4715359ce268702e72b49ad2ebcf6bfa773cdeda6ddc
trace SHA-256      e65fe8eef6fafe8f99ef3f2e5cf28dcb629cb990105342f10e808f61ba31050b
art SHA-256        62c7636d8f2285aba1c2a05803e43b39c5483b9739ed85fdca56cee27adf501a
```

Finding:
`findings/classic-test30-cadillac-baseline-launch-trace.md`

Hardware order:
1. copy `dino.zip` to `/CLASSIC/bin/`;
2. launch Cadillac from CLASSIC first;
3. if it fails, inspect `/CLASSIC/launch.stg` and report the one-byte stage;
4. if Cadillac runs, retry Pac-Man/Ms Pac-Man.


### Test31 hardware FAIL; Test32 Test12-derived path fix ready (2026-09-08)

Test31 hardware:
- device boots;
- CLASSIC page visible;
- Pac-Man, Ms Pac-Man and Cadillacs and Dinosaurs visible;
- all three show Loading and immediately return to the list;
- known-good `dino.zip` also fails from CLASSIC.

Therefore the problem is CLASSIC -> MAME plumbing, not Pac-Man compatibility.

Concrete flaw found in Test29/31: the launcher required `/CLASSIC/` inside the browser-supplied wrapper path. That misses the valid relative stock-browser form `CLASSIC/<game>.zfb`, causing an immediate fallthrough into untouched stock `run_game()`.

Test32 accepts both `CLASSIC/...` and `/.../CLASSIC/...`.

For CLASSIC it uses the Test12-derived external-core load sequence and sets:
- `0x810a0eb0 = /mnt/sda1/CLASSIC`;
- `0x8109fce8 = embedded ZIP basename`.

No stock Arcade preprocessing, no list7 alias, no new memory region.

Artwork is intentionally stretched to 600x330 and centered at y=75 so the full title and bottom border remain inside the stock UI overlays.

Exact local candidate:

```text
xgo-classic-test32-test12-loader-pathfix-artfit.zip
size              7,535,429 bytes
ZIP SHA-256        3e8d7b1dfafd029120556ea5d65e06130bb3e0e7dd9b69759b712b533c42b08a
firmware SHA-256   235636d86ca86c915b2a78905392e9f2606a04392c51fc0114126154cbf65448
loader SHA-256     5aa159b1dc6bd05fcb18c8f3310818acd6c25d82d783bcd84cd0bc1b6cc15fc3
art SHA-256        f6ee3f75eafcdee6d5f61a64a7a8f709107eb8b1d93fefe694619e319937dd20
```

Finding:
`findings/classic-test32-test12-loader-pathfix.md`

Hardware order: boot -> CLASSIC art -> Cadillac first -> Pac-Man/Ms Pac-Man only if Cadillac reaches MAME.


### Test31 regression root-caused; Test32 golden-safe recovery ready (2026-09-08)

Test31 hardware exposed a protected-golden regression:
- CLASSIC games all bounced immediately;
- Contra pause menu showed movable Mapper yellow squares over Resume/Quit/Load/Save;
- ordinary pause-menu options became unselectable.

Root cause is now proven: Test28-31 injected CLASSIC code at `0x80001900..`, but Mapper v19 owns active bytes throughout `0x80001500..0x8000217f`. CLASSIC overwrote Mapper.

This invalidates Tests28-31 as regression-safe MAME evidence.

Test32 starts again from exact golden Test08 and uses no Mapper-era low-memory space.

Architecture:
- 352-byte bootstrap at `0x807db9b0`, inside the verified unused tail of the Test08 scanner cave;
- non-CLASSIC -> untouched stock `run_game`;
- CLASSIC -> bootstrap loads `/cores/classic/loader.bin` to RAM `0x86ff0000`;
- 1,947-byte RAM second stage parses the CLASSIC wrapper and loads the exact Test12 MAME core at `0x87000000`;
- list11 metadata/art resource-name strings also live only in the remaining verified scanner-cave tail;
- Mapper v19, SNES loader and Audio OSD ranges are byte-asserted unchanged.

Exact final hardware package:

```text
xgo-classic-test32-recovered-golden-safe.zip
size              7,551,351 bytes
ZIP SHA-256        4b4df70835ab90fbbb3e363ddb14cbf73f73379b1e926ab1879c7cb538d96d11
firmware SHA-256   55dca4ec9b35cd7d8afd66087c04ea5a6893aebad91c96af48c2a8e672a49bb8
bootstrap SHA      40fc040c26d3dcdb261f4f4050565c674174271deee6499047fa486bdf6e42bc
second-stage SHA   1b413ad9048e166010bbf7f4bce9d406cb29b3c5d57900cc6763d13aa571b040
Test12 core SHA    abf8e4ec6eb7c6d4c2162076e8faa868954a3663b8210c820e1267857b345461
```

Private CI run `34309041289`; artifact `10087703544`.

Hardware order:
1. boot;
2. test Contra pause menu first;
3. verify Mapper/pause behavior fully restored;
4. verify stock Arcade Cadillac;
5. test Cadillac from CLASSIC;
6. then Pac-Man/Ms Pac-Man.

Finding:
`findings/classic-test32-golden-safe-recovery.md`


### Deep Test12 contract audit complete; Test33 exact-machine-loader candidate ready (2026-09-09)

Test32 hardware established a clean boundary:
- boot PASS;
- Contra PASS;
- pause Resume/Quit/Load/Save PASS;
- Mapper regression fixed;
- stock Arcade Cadillacs PASS;
- every CLASSIC game still FAILS by immediate return.

Deep binary audit findings:

1. Correction to earlier Mapper diagnosis:
   - exact golden Test08 has a zero run `0x800018fe..0x8000217f`;
   - the launcher at `0x80001900` was not itself overwriting Mapper;
   - the unsafe CLASSIC metadata/art strings had been placed at `0x800018d0`, before the proven-zero boundary;
   - Test32 moving those strings out explains the physical Mapper recovery.

2. Browser call contract:
   - both normal browser launch sites pass the fully constructed selected wrapper path in `a0` to untouched `run_game @ 0x80360b88`.

3. Exact Test08 and hardware-working Test12 are byte-identical through the entire stock `run_game()` pre-loader path and helpers.
   Test12 therefore relied on stock preparation before the MAME loader.

4. The exact Test12 core is linked with `xgo_preloaded_rom_sbrk.c`, whose private heap starts at:
   `gp_buf_64m + align64(g_run_file_size)`.
   Those globals are populated by stock `run_game()`.
   Test32 bypassed this memory/preload contract.

5. Full Test12 vs Test08 firmware diff:
   - 4114 changed bytes in 837 runs;
   - all differences are accounted for by CRC, Test12 loader, later golden run_emulator/OSD, final Arcade hook, later Refresh/scanner/menu geometry and Audio OSD hooks;
   - no hidden MAME-support patch remains elsewhere.

6. Major exactness correction:
   recompiling the pinned historical loader source at its original Test12 address does NOT reproduce the hardware Test12 loader:
   `1373 bytes; 918 bytes differ`.
   Earlier wording that Test26 used the "exact historical loader" was therefore incorrect.

7. The ACTUAL hardware-working Test12 loader machine image was extracted directly:
```text
0x80002780..0x80002d03
size 1412
SHA-256 42f7638f9d0d9d89272eb06e880c777c65ce183900a8eee037cc561dccea4cb1
```

Test33 mechanically relocates those actual machine bytes to:
```text
0x80001900..0x80001e83
```
inside the exact-golden zero region.

Only relocation-required changes are made:
- eight internal J/JAL targets;
- two internal data-string address references;
- historical list gate immediate 7 -> CLASSIC list 11.

Relocated loader SHA:
`e38af97eabb454dbcc8dd8b1823b6f82b8878d7993c0eb7a120d26c6da767d4e`.

Test33 is the first candidate to combine:
- real first-class CLASSIC list11 metadata/folder/art;
- untouched stock browser calls;
- complete untouched stock `run_game()` preload and package preparation;
- actual relocated Test12 loader machine code;
- exact archived Test12 MAME2000 core;
- golden Test08 run_emulator/OSD/Mapper/SNES/scanner.

No Test32 RAM second-stage is used.

CI:
`34312130930`, artifact `10088750278`.

Firmware:
`80c851925990a04c35c9f7cc568f410f93c82d671f50b471ebd4f2c85f3c9a55`.

Final package:
```text
xgo-classic-test33-exact-test12-preload.zip
size 7,528,733
SHA-256 092c7af7f31efe5c408cf16f674ac106c3483d55f3540cecdaa79dda1289061e
```

The CLASSIC artwork is a content-only squashed version (590x300 inside the 640x480 resource) so title and bottom border remain above the UI icon row.

Hardware gate:
1. confirm Contra pause/Mapper remains golden;
2. confirm stock Arcade Cadillac remains golden;
3. test CLASSIC Cadillacs and Dinosaurs using `/CLASSIC/bin/dino.zip` FIRST;
4. only if Cadillac reaches gameplay test Pac-Man/Ms Pac-Man.

Finding:
`findings/classic-deep-test12-contract-audit-test33.md`.


### Deep Test12 contract recovery -> Test33 exact machine-loader candidate (2026-09-09)

After Test32 restored golden behavior but CLASSIC still launched no games, a bit-level comparison was performed against the actual hardware-working MAME2000 Test12 path.

Major findings:

1. Test32 intercepted at the browser call to `run_game()`, so it bypassed the stock wrapper-preload path.
2. The exact Test12 MAME core links `xgo_preloaded_rom_sbrk.c`, which depends on stock `gp_buf_64m` and `g_run_file_size` already being initialized.
3. Exact `run_game()` machine code confirms it opens/sizes/preloads the selected wrapper into `gp_buf_64m`, sets `g_run_file_size`, then dispatches by family.
4. Test12 entered MAME only at the final FBA seam:
   `0x80360df8`, with original wrapper path in `a0` and `a1=0`.
5. Recompiling the historical loader source did not reproduce the actual Test12 loader: 918 bytes differed. The hardware-tested machine bytes are authoritative.
6. Corrected collision diagnosis: Mapper v19 ends at `0x800018fd`; `0x800018fe..0x8000217f` is genuinely zero/free in golden Test08. Earlier Mapper corruption came from CLASSIC strings/flag placed at `0x800018d0..0x800018f0`, not from code at `0x80001900`.

The exact Test12 loader was extracted from:

```text
0x80002780..0x80002d03
size 1412
source SHA-256 42f7638f9d0d9d89272eb06e880c777c65ce183900a8eee037cc561dccea4cb1
```

and relocated into the verified golden free region:

```text
0x80001900..0x80001e83
relocated SHA-256 e38af97eabb454dbcc8dd8b1823b6f82b8878d7993c0eb7a120d26c6da767d4e
```

Only:
- list gate 7 -> 11;
- 8 internal J/JAL targets;
- 2 internal data-pointer low halves

were changed.

Test33 architecture:

```text
CLASSIC browser
 -> untouched stock run_game()
 -> stock preload / gp_buf_64m / g_run_file_size
 -> final FBA seam 0x80360df8
 -> relocated actual Test12 machine loader
 -> exact Test12 MAME2000 core
 -> golden run_emulator()
```

Real Arcade remains stock because loader gate is list 11 only.

Exact full hardware package:

```text
xgo-classic-test33-exact-test12-loader-full.zip
size              7,549,340 bytes
ZIP SHA-256        94d269201d59e42554dd80f547faa89262103b84c9fe80332666d258733867c4
firmware SHA-256   80c851925990a04c35c9f7cc568f410f93c82d671f50b471ebd4f2c85f3c9a55
core SHA-256       abf8e4ec6eb7c6d4c2162076e8faa868954a3663b8210c820e1267857b345461
```

Finding:
`findings/classic-deep-test12-contract-test33.md`

Remaining uncertainty: golden `run_emulator()` differs from historical Test12 by 150 bytes (later Audio OSD/scheduler). Do not change that until the corrected preload/loader contract is hardware-tested.

Hardware order:
1. Boot.
2. Contra pause/Mapper.
3. stock Arcade Cadillac.
4. CLASSIC Cadillac (`dino.zip`) first.
5. only if CLASSIC Cadillac reaches gameplay, test Pac-Man/Ms Pac-Man.


### Test33/33A hardware breakthrough + Test34 closeout candidate (2026-09-09)

Hardware result from Test33/33A:
- CLASSIC Cadillacs and Dinosaurs using `/CLASSIC/bin/dino.zip` launches and runs;
- known MAME2000 lag remains;
- CLASSIC Pac-Man freezes;
- CLASSIC Ms. Pac-Man freezes;
- stock Arcade Cadillac remains functional;
- Test33A stretched CLASSIC artwork accepted as much better.

This proves the first-class CLASSIC launch plumbing is now working. Pac-Man/Ms. Pac-Man are no longer treated as a CLASSIC launch problem.

Test34 adds only branch-closeout UI/Refresh work on top of hardware-working Test33A:

1. bottom list label:
   - stock draw seam `0x80359838 -> 0x803528a4`;
   - list11-only wrapper substitutes `CLASSIC` at the existing stock text-pointer stack slot;
   - all other lists tail-call stock unchanged.

2. Refresh:
   - existing scanner loop extended from indices `0..5` to `0,1,2,3,4,5,10`;
   - scanner index 10 maps to list ID 11;
   - index10 folder is `/CLASSIC`;
   - index10 classifier rule accepts ZFB (ID 7) only;
   - existing stable merge rewrites `clm.tax/clm.nec/clm.bvs` and invalidates list11 cached count;
   - `/CLASSIC/bin` is skipped by existing directory handling;
   - stock Arcade lists 7-10 remain outside Refresh.

Exact Test34 candidate:

```text
xgo-classic-test34-label-refresh.zip
size        7,537,711 bytes
SHA-256     cbacb517f5dfbb092963750b88d4caf7da499a0ee508e394709013990ee3b352
firmware    4e8faa2531b958988bac4497bf2e7e04f95349b3ba8debef77b95c5a943dca0f
loader      e38af97eabb454dbcc8dd8b1823b6f82b8878d7993c0eb7a120d26c6da767d4e
core        abf8e4ec6eb7c6d4c2162076e8faa868954a3663b8210c820e1267857b345461
art         4ff7b3e0bd88acb96e3a915264fdbaee14209175a5331e8a422764664e07a843
```

Finding:
`findings/classic-test34-label-refresh.md`

Hardware closeout gate before merge:
- Contra pause/Mapper;
- stock Arcade Cadillac;
- CLASSIC Cadillac;
- bottom label reads CLASSIC with garble gone;
- Refresh behaves normally;
- reboot and verify three CLASSIC entries persist.

On PASS:
- merge `research-game-list-arcade-expansion` to `main`;
- promote Test34 checkpoint;
- open `research-mame2000-pacman-compatibility`.

Pac-Man branch baseline:
- MAME2000 requires MAME 0.37b5 ROM definitions;
- begin with full non-merged 0.37b5 `pacman.zip` and `mspacman.zip`;
- compare exact filenames/CRCs/parent closure before changing runtime code.
