# XGO stock scheduler transplant patch surface

Date: 2026-09-05
Branch: `research-post-mapper-runtime`

## Purpose

This note converts the family-wide stock-FBA scheduler archaeology into the smallest plausible XGO-only optimization surface.

It deliberately does **not** propose:

- another external CPS1 emulator;
- another A68K ROM-loading experiment;
- replacing XGO's full `run_emulator()`;
- changing FBA, C68K, audio, input, video, or menu/state code.

The working target is a scheduler-only behavioral transplant.

## Proven family contract to preserve

All compared stock arcade builds share the same important FBA-side contract:

```text
ordinary CPS1 68000 -> C68K
FBA audio          -> 22050 Hz / 367 samples
frontend pacing    -> invokes private gfn_frameskip(flag)
frameskip(1)       -> active FBA draw buffer = NULL
frameskip(0)       -> alternate between two draw buffers
retro_run()        -> still executes on skipped-render frames
audio              -> still executes on skipped-render frames
```

The private FBA render-skip mechanism is therefore **not** the part to replace.

## Proven scheduler divergence

Sibling stock firmware:

```text
SF2000 08/03
SF2000 1.71
GB300 v2
```

uses a wall-time / ideal-frame-count model.

XGO uses an incremental frame-period / residual-debt model.

### Sibling model

Conceptually:

```c
elapsed_ms = now_ms - start_tick;
ideal_frame = (elapsed_ms * target_fps) / 1000;
next_frame = completed_frame + 1;

if (next_frame <= ideal_frame) {
    // We are behind wall time.
    catchup_count++;

    // Family code limits catch-up bursts rather than running unbounded.
    if (catchup_count <= 3)
        frameskip = (catchup_count > 0);
    else
        recover_to_normal_path();
}
else {
    catchup_count = 0;
    frameskip = 0;

    deadline_ms = ((next_frame - 1) * 1000) / target_fps;
    if (elapsed_ms < deadline_ms)
        sleep(deadline_ms - elapsed_ms);
}

if (gfn_frameskip)
    gfn_frameskip(frameskip);

retro_run();
completed_frame++;
```

The important property is the **absolute wall-time anchor**. A slow frame does not permanently shift all future frame deadlines.

### XGO model

Conceptually:

```c
period_ms = next_period();   // PAL 20; NTSC 17,17,16
adjusted_elapsed = now_ms + residual_debt - previous_tick;

if (adjusted_elapsed < period_ms) {
    dly_tsk(1);
    retry;
}

overrun = adjusted_elapsed - period_ms;
residual_debt = overrun;

if (overrun > period_ms) {
    frameskip = 1;

    if (overrun > period_ms + 10)
        residual_debt = 0;
}
else {
    frameskip = 0;
}

if (gfn_frameskip)
    gfn_frameskip(frameskip);

retro_run();
previous_tick = now_ms;
```

The important difference is that XGO carries **incremental timing debt** from one frame to the next instead of continually recomputing where emulation ought to be relative to the original wall-clock anchor.

## XGO timing state already isolated in run_emulator()

The XGO adaptive timing path is concentrated around the frame-pacing region of:

```text
run_emulator = 0x8035ed48
```

Key observed locations from the current reconstruction include:

```text
0x8035ef08  compare elapsed against target period
0x8035ef10  calculate lateness / overrun
0x8035ef14  test whether lateness exceeds another frame period
0x8035ef44  assert frameskip flag
0x8035efd4  clear frameskip flag
0x8035f0d4  load frameskip argument
0x8035f0d8  call private gfn_frameskip
```

With authoritative XGO GP:

```text
XGO_STOCK_GP = 0x80c34774
```

the confirmed private callback slot is:

```text
gfn_frameskip = 0x80c33ae0
```

and the observed frameskip-flag GP slot is:

```text
0x80c33a90
```

The remaining timing globals around this region must be named precisely before any binary patch is emitted, but the performance-critical decision block is already localized.

## Minimal transplant strategy

The first hardware candidate should **not** copy raw SF2000 instructions into XGO.

The sibling code uses different:

- GP-relative globals;
- register allocation;
- surrounding control flow;
- frontend/menu state layout;
- helper addresses.

Instead, reproduce the sibling **policy** in XGO's existing timing state.

Preferred patch shape:

```text
XGO run_emulator
    |
    +-- leave initialization unchanged
    +-- leave AV/sample-rate setup unchanged
    +-- leave sound task unchanged
    +-- leave input/menu/state handling unchanged
    |
    +-- replace only frame-deadline / catch-up decision
            |
            +-- maintain start_tick
            +-- maintain completed_frame
            +-- compute ideal_frame from total elapsed wall time
            +-- permit bounded catch-up (max 3)
            +-- set existing XGO frameskip flag
            |
            +-- fall back into existing XGO:
                    gfn_frameskip(flag)
                    retro_run()
                    video/audio callback path
```

## Why this is lower risk than a full scheduler transplant

A raw function transplant would also import sibling assumptions about:

- system-family dispatch;
- save/load state;
- pause menu;
- key mapping;
- UI lifecycle;
- buffer ownership;
- sound-task state;
- firmware globals.

Those areas have already diverged between SF2000, GB300 v2 and XGO.

A policy-only patch keeps XGO's existing device/application integration intact and changes only the timing decision that determines when the already-working stock FBA draw-skip mechanism is used.

## Required static proof before hardware

Before building a candidate:

1. Name the exact XGO timing globals used by:
   - previous/current tick;
   - residual debt;
   - frame-period/cadence state;
   - completed-frame counter;
   - frameskip flag.
2. Identify one safe code-cave or branch-redirection site for a small helper.
3. Prove the helper can return to the existing XGO `gfn_frameskip` / `retro_run` path without changing callback state.
4. Determine whether a new wall-time `start_tick` and `completed_frame` can reuse existing scratch globals or require two private words in unused RAM.
5. Preserve the original XGO timing block so rollback is one patch reversal.

## Candidate behavioral oracle

If the scheduler hypothesis is correct, a scheduler-only hardware patch should show:

```text
same game compatibility
same controls
same audio character
same save/menu behavior
same baseline stock speed

but:

fewer / shorter episodes of prolonged slow-motion after transient load
more aggressive short render-drop bursts when the device falls behind
faster recovery to normal cadence
```

A result that changes ROM loading, game compatibility, or core initialization would mean the patch surface was too broad.

## Current decision

The family archaeology has now produced a concrete mechanism suitable for a controlled experiment:

> **Keep XGO's stock FBA and private draw-skip implementation, but evaluate replacing only XGO's incremental drift/debt pacing policy with the sibling wall-time bounded-catch-up policy.**

No hardware package should be built until the exact XGO state/global map and branch patch surface are completed.
