# HANDOFF-CURRENT

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
