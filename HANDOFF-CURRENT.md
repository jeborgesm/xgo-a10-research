# HANDOFF-CURRENT

## Active branch

`research-audio-osd`

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

The user populated the vault with the retained XGO research binaries, including the golden mapper-v19, SNES Test02, and current CPS1 scheduler baseline. The current vault layout is repository-root filenames; `artifacts/golden-artifacts.json` records the canonical paths.

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
