# XGO embedded CPS timing constant and FBA audio segment reveal deliberate 60-Hz compromise

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **BIN + SRC FAMILY + ARITHMETIC**

## Exact embedded CPS timing constant [BIN]

The stock XGO firmware contains the double-precision constant:

```text
59.633333
```

at:

```text
0x809B42E0
```

Its immediate rodata neighborhood contains CPS-specific state labels including:

```text
CpsRam90
CpsRamFF
CpsReg
CpsRam708
CpsFrg
CpsRam660
CpsRom
CpsZRom
CpsZRamC0
```

This is strong exact-binary placement of the value in the embedded CPS engine data region.

## Matching older FBA engine source [SRC/UP]

The already-established engine ancestry is close to:

```text
dmitrysmagin/fba-a320
a324b2ddb92f82a48b90e2ee6af0cf69403219ab
```

Its CPS initialization performs:

```c
BurnSetRefreshRate(59.633333);
```

and then derives CPS CPU clock work from `nBurnFPS`.

This matches the exact double retained in XGO.

Therefore the CPS engine internally knows a nominal timing near 59.633333 Hz even though the XGO frontend scheduler is independently proven to execute its NTSC loop on an exact 60-FPS 17/17/16-ms cadence.

## XGO FBA audio constants [BIN]

The XGO libretro-facing FBA wrapper sets:

```text
source rate        = 22050
audio segment      = 367 source frames
```

The later-wrapper ancestry at `madcock/sf2000-fbalpha@621e371` uses the same architecture: a hard-coded audio segment, one batch callback after each `BurnDrvFrame()`, and a fixed declared sample rate. The upstream constants differ because the vendor XGO build changed the rate/segment policy.

## Two timing domains

For CPS1 on XGO there are therefore two distinct timing concepts:

### Engine nominal CPS timing

```text
~59.633333 Hz
```

### Frontend real execution cadence

```text
60.000000 Hz
```

The frontend runs CPS frames about:

```text
60 / 59.633333 - 1 ~= 0.6149%
```

faster in wall-clock cadence than the engine's nominal refresh value.

This is a scheduler behavior inherited by gameplay, not an audio-only defect.

## Why 367 makes sense as a vendor compromise

At the XGO's actual 60-Hz frontend cadence:

```text
22050 / 60 = 367.5 samples/frame
```

The vendor chose the integer:

```text
367
```

which is only half a sample/frame below the exact 60-Hz requirement.

At the CPS engine's nominal 59.633333 Hz, exact 22050-Hz audio would instead require approximately:

```text
22050 / 59.633333 ~= 369.76 samples/frame
```

Thus 367 aligns far more closely with the **frontend's 60-Hz execution cadence** than with nominal CPS timing.

This strongly suggests the vendor audio segment is a pragmatic integer approximation to the frontend's actual cadence.

## Gameplay-audio consequence

For the user's target — sound synchronized with the game as XGO actually plays it — changing the scheduler to 59.633333 is not a prerequisite.

A much smaller and safer correction is:

```text
keep protected 60-Hz gameplay scheduler
keep core producing its stock 367-frame batches
rate-convert actual 22020-frame/s delivery
to the exact hardware output clock
```

That removes the recurring PCM deficit without changing game speed.

## Separate accuracy question

A future “board-authentic CPS timing” project could investigate running CPS at its nominal refresh and adjusting audio accordingly.

That would change gameplay timing and belongs outside the current audio-quality scope.

It must not be smuggled into an audio-latency/fidelity candidate.

## Evidence boundary

- XGO 59.633333 CPS-region constant: **BIN**
- matching FBA-A320 CPS initialization: **SRC/UP**
- exact 60-Hz XGO frontend scheduler: **BIN**
- 22050/367 XGO FBA wrapper constants: **BIN**
- interpretation of 367 as a 60-Hz integer compromise: **INF strongly supported by arithmetic**

## Hardware gate

Not reached.
