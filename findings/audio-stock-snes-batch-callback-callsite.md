# XGO built-in SNES audio callback callsite — BIN closure

Date: 2026-10-01  
Branch: `research-audio-fidelity-latency`  
Status: **DIRECT STOCK BIN — CALLBACK SITE FOUND; PER-FRAME INCREMENT STILL OPEN**

## Provenance

Stock `bios/bisrv.asd`:

```text
SHA-256 869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf
runtime base 0x80000000
```

The image contains the built-in SNES core identity strings:

```text
v1.36
Snes9x 2005
smc|fig|sfc|gd3|gd7|dx2|bsx|swc
```

This pass located the corresponding libretro glue in the stock binary rather than inferring callback cadence solely from the maintained family source.

## Libretro callback slots [BIN]

A compact setter group at `0x8073F1BC..` stores frontend callbacks in GP-relative slots.

The audio-batch slot is:

```text
GP + 0xE900
```

and is loaded by the stock SNES audio upload path at:

```text
0x8073F8E8  lw s1,0xE900(gp)
0x8073F8EC  jalr s1
0x8073F8F0  move a0,s0
```

At the call:

```text
a0 = stock SNES mixed-audio buffer
a1 = [GP + 0xE904]
```

Therefore `[GP+0xE904]` is the frame count passed to the frontend's `retro_audio_sample_batch_t` callback. [BIN]

## Stock accumulation logic [BIN]

Immediately before the callback:

```text
0x8073F838  lw   t4,0xE904(gp)
0x8073F83C  lw   t5,0xE8F4(gp)
0x8073F840  addu v0,t4,t5
0x8073F844  slti t3,v0,0x81
0x8073F84C  sw   v0,0xE904(gp)
...
0x8073F8E4  lw   a1,0xE904(gp)
0x8073F8E8  lw   s1,0xE900(gp)
0x8073F8EC  jalr s1
...
0x8073F8F8  sw   zero,0xE904(gp)
```

The branch at `0x8073F848` sends control to the mix/callback block when the accumulated count reaches at least `0x81 = 129`.

Thus stock built-in SNES does **not** blindly call the frontend with 576 frames.

It maintains:

```text
pending += fixed/current increment at GP+0xE8F4

if pending < 129:
    no audio batch callback yet
else:
    mix pending stereo frames
    audio_batch_cb(buffer, pending)
    pending = 0
```

The mix helper receives `pending << 1`, consistent with a stereo sample count, while the libretro callback receives `pending` as stereo frames. [BIN]

## Important correction to the family model

The maintained family Snes9x2005 revision emits one audio batch per video frame with approximately 183/184 frames at 11025 Hz.

The XGO built-in binary now proves a related but **not source-identical** policy:

- it has an explicit pending-frame accumulator;
- it suppresses callback until pending reaches 129 frames;
- it submits the accumulated count and resets it.

Therefore the family 183/184 residence model must remain SRC/UP-model evidence until the value/source of `GP+0xE8F4` is closed.

If `E8F4` is approximately one frame's 183/184-frame production, the threshold is crossed every frame and the behavior converges on the family model. If it is smaller, XGO may aggregate multiple internal production slices before each callback.

We now have the exact BIN question needed to decide that.

## Initialization lead [BIN]

`GP+0xE8F4` has a single identified write in this core region:

```text
0x80740AC4  lw  a0,0x4C(s2)
0x80740AC8  jal 0x807C02F0
0x80740ACC  sw  v0,0xE8F4(gp)
```

So the callback increment is initialized from the return value of `0x807C02F0`, using an object/configuration field at `s2+0x4C`.

Closing that helper/field is now the shortest route to the exact stock callback size.

## What is now closed

[BIN]:

- built-in core is Snes9x 2005 lineage;
- exact stock audio-batch callback slot/callsite located;
- callback frame argument identified as `GP+0xE904`;
- stock pending-frame accumulator identified;
- callback threshold is 129 frames;
- pending count resets to zero after submission;
- 576 is definitively a downstream XGO frontend-consumer quantum, not the built-in SNES core's direct callback size.

## OPEN

- exact runtime value of `GP+0xE8F4`;
- semantics of helper `0x807C02F0`;
- whether stock built-in callback count is normally ~183/184, a smaller sub-frame increment accumulated to >=129, or another value;
- resulting exact stock-BIN frontend residence distribution.

## Next target

Reverse `0x807C02F0` sufficiently to identify the quantity returned for the stock SNES configuration, or locate the `s2+0x4C` field initialization upstream.

Once `E8F4` is known, recompute the residence distribution from stock BIN and either validate or retire the family-derived ~26-ms mean.

## Hardware gate

Not reached.
