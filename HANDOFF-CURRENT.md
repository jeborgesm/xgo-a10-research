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
