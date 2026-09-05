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


## Exact XGO pacing-state map

Direct disassembly of the preserved XGO `run_emulator()` at `0x8035ed48`, using authoritative:

```text
XGO_STOCK_GP = 0x80c34774
```

now identifies the scheduler state precisely.

### Persistent/global timing inputs

```text
0x80c2d128  target_fps
             PAL  = 50
             NTSC = 60

0x80c2d118  active integer frame period in milliseconds
             PAL  = 20
             NTSC = 17/17/16 cadence

0x80c2e870  previous/current tick anchor used by pacing loop

0x80c33a74  residual overrun/debt carried into next frame

0x80c33a90  frameskip flag passed to gfn_frameskip()

0x80c33ae0  gfn_frameskip callback pointer

0x80c33ae4  active retro_run callback pointer
```

Two nearby setup words are diagnostic/configuration values rather than required scheduler state:

```text
0x80c2d12c  20000 / 16667 usec diagnostic period
0x80c2d114  3528 / 2940 diagnostic sound_len
```

The corrected audio analysis already established that these do not impose a hard PCM budget.

### Local register state

The two counters previously suspected to be firmware globals are actually local `run_emulator()` register state:

```text
s2 = 0 at 0x8035edfc
s3 = 0 at 0x8035ee0c
```

`s3` is the NTSC modulo-3 cadence counter. It increments at:

```asm
8035efe0  addiu s3,s3,1
8035efe4  li    a2,3
8035efe8  beq   s3,a2,0x8035f170
8035efec  li    v0,17
```

This implements the repeating integer cadence:

```text
17 ms
17 ms
16 ms
```

for exactly 60 frames per second over each 50-ms / 3-frame group.

`s2` is local transient late/catch-up bookkeeping, not persistent firmware state.

### Exact XGO incremental-debt loop

The central timing sequence is:

```asm
8035eee8  jal   os_get_tick_count
8035eef0  lw    v1,0x80c33a74       ; residual debt
8035eef4  lw    a0,0x80c2e870       ; prior tick
8035eef8  lw    a1,0x80c2d118       ; frame period
8035eefc  move  a2,v0               ; current tick
8035ef00  addu  v0,v0,v1
8035ef04  subu  v0,v0,a0            ; adjusted elapsed
8035ef08  sltu  t1,v0,a1
8035ef0c  bne   t1,zero,wait
8035ef10  subu  a0,v0,a1            ; overrun
8035ef14  sltu  t2,a1,a0            ; overrun > another frame period?
8035ef18  sw    a2,0x80c2e870       ; update tick anchor
8035ef20  sw    a0,0x80c33a74       ; carry debt
8035ef24  addiu a3,a1,10
8035ef28  sltu  t3,a3,a0            ; overrun > period + 10?
8035ef30  sw    zero,0x80c33a74     ; then discard debt
...
8035ef44  sw    1,0x80c33a90        ; assert frameskip
...
8035efd4  sw    zero,0x80c33a90     ; clear frameskip
```

If the frame is early, XGO takes:

```asm
8035f080  jal   dly_tsk
8035f084  li    a0,1
8035f088  branch back to pacing loop
```

Thus the previously reconstructed incremental-debt model is now tied to exact firmware storage.

## New-state requirement for sibling policy

A wall-time/ideal-frame implementation does not need to repurpose any of the XGO debt/cadence globals.

It requires three private state words unless an existing XGO saved register is deliberately repurposed:

```text
scheduler_start_tick
completed_frame_count
catchup_count
```

Everything else can reuse proven XGO state/services:

```text
target_fps     -> 0x80c2d128
tick source    -> os_get_tick_count()
frameskip flag -> 0x80c33a90
frameskip hook -> 0x80c33ae0
retro_run      -> existing XGO path
```

This is safer than overloading `0x80c33a74` or other stock state whose secondary consumers may not yet be fully named.

## Patch redirection boundary

The smallest useful behavioral interception is the timing decision region beginning around:

```text
0x8035eee8
```

and ending before the existing callback dispatch / general frame-processing path.

The patch should return with only the existing XGO frameskip flag changed.

The following must remain stock:

```text
0x8035f0d4  load frameskip argument
0x8035f0d8  call gfn_frameskip
...
existing retro_run dispatch
existing menu/state/input/audio logic
```

Therefore the desired helper contract is conceptually:

```c
void xgo_scheduler_policy(void)
{
    // read target_fps and wall clock
    // update private start_tick / completed_frame
    // bounded sibling-style catch-up
    // write only 0x80c33a90 (frameskip flag)
    // return to stock dispatch path
}
```


## Exact sibling wall-time scheduler reconstruction

The SF2000 08/03 pacing core is now reconstructed directly from the preserved binary rather than summarized from behavior.

Relevant state:

```text
s2            start_tick captured once for the run_emulator session
s0            consecutive catch-up/render-skip count
gp-3364       completed_frame_count
gp-3336       frameskip flag
gp-30296      target_fps
```

With SF2000 stock GP `0x80c114f4`:

```text
completed_frame_count = 0x80c107d0
frameskip flag        = 0x80c107ec
target_fps            = 0x80c09e9c
```

The critical sequence begins at `0x80358afc`:

```asm
80358afc  jal   os_get_tick_count
80358b04  lw    a2,target_fps
80358b08  subu  a3,v0,s2             ; elapsed_ms = now - start_tick
80358b0c  li    ra,1000
80358b10  mult  a3,a2
80358b14  lw    v0,completed_frame
80358b18  addiu a1,v0,1              ; next_frame = completed + 1
...
80358b28  divu  a0,ra
80358b30  mflo  a0                   ; ideal_frame = elapsed*fps/1000
80358b34  sltu  t9,a0,a1
80358b38  bnez  t9,early_path        ; ideal_frame < next_frame
80358b3c  sw    a1,completed_frame
80358b40  slti  v1,s0,3              ; catchup_count < 3
80358b44  sltu  t1,a1,a0             ; next_frame < ideal_frame
80358b48  and   a2,t1,v1
80358b4c  bnez  a2,catchup
80358b50  addiu s0,s0,1              ; delay slot: increment catchup
80358b54  move  s0,zero              ; otherwise stop catch-up burst
80358b58  sw    a0,completed_frame    ; snap logical frame to wall-time ideal
80358b5c  lw    v0,gfn_frameskip
80358b60  slt   a0,zero,s0
80358b64  bnez  v0,call_frameskip
80358b68  sw    a0,frameskip_flag
```

This produces the exact bounded catch-up rule:

```c
elapsed_ms = now - start_tick;
ideal_frame = (elapsed_ms * target_fps) / 1000;
next_frame = completed_frame + 1;

if (ideal_frame < next_frame) {
    // early: sleep to absolute frame deadline
} else {
    completed_frame = next_frame;

    if (next_frame < ideal_frame && catchup_count < 3) {
        catchup_count++;
    } else {
        catchup_count = 0;
        completed_frame = ideal_frame;
    }

    frameskip = (catchup_count > 0);
}
```

### Exact early/deadline path

The sibling early path at `0x80358df0` computes the absolute deadline without accumulating per-frame debt:

```asm
80358df0  sll   t2,a1,5              ; 32 * next_frame
80358df4  subu  t7,t2,a1             ; 31 * next_frame
80358df8  sll   t6,t7,2              ; 124 * next_frame
80358dfc  addu  t0,t6,a1             ; 125 * next_frame
80358e00  sll   t5,t0,3              ; 1000 * next_frame
80358e04  addiu t4,t5,-1000          ; 1000 * (next_frame - 1)
80358e08  div   t4,target_fps
80358e10  mflo  t3                   ; deadline_ms
80358e14  subu  a0,t3,elapsed_ms     ; sleep_ms
80358e18  blez  a0,no_sleep
80358e20  jal   dly_tsk               ; sleep exact positive delta
```

Equivalent:

```c
deadline_ms = ((next_frame - 1) * 1000) / target_fps;
sleep_ms = deadline_ms - elapsed_ms;

if (sleep_ms > 0)
    dly_tsk(sleep_ms);
```

This confirms the key behavioral distinction from XGO: sibling pacing is continuously re-anchored to absolute elapsed wall time.

## Private-state requirement correction

The cleanest helper implementation requires:

```text
scheduler_start_tick
completed_frame_count
catchup_count
```

The earlier two-word estimate omitted the fact that the sibling catch-up counter is held in saved register `s0` across frame-loop iterations.

A custom hand-written helper could potentially reuse XGO's existing `s2` register as the catch-up counter, but that should be treated as a separate optimization only after proving every XGO `s2` consumer in `run_emulator()`.

For the first scheduler-only candidate, three private words are safer and clearer.

## Code-cave constraint

The historically verified low firmware cave:

```text
0x80001500..0x8000217f
```

is already part of protected native-NES/external-core infrastructure, and mapper work also uses the neighboring low injection area.

It must **not** be reused casually for this scheduler experiment.

A separate non-conflicting executable cave or an explicitly coordinated shared injection layout must be proven before generating a hardware candidate.

This keeps the protected mapper-v19 and external-NES baselines intact.

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
