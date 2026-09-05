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
