# XGO stock SNES callback increment — sample-rate / refresh-rate closure

Date: 2026-10-01  
Branch: `research-audio-fidelity-latency`  
Status: **BIN CLOSED FOR FORMULA; FAMILY SOURCE CORROBORATION**

## Corrected call chain

After accounting for the MIPS delay slot, the stock SNES initialization sequence is:

```text
g_sample_rate (GP+0x8C94 / runtime 0x80C2D408)
 -> integer-to-double helper 0x801B25D8

refresh-rate double
 -> selected from the stock SNES AV-info constants

double division helper 0x801B15CC
 -> sample_rate / refresh_rate

double-to-integer helper 0x801B2460
 -> truncates the quotient

delay-slot store at 0x80740ACC
 -> GP+0xE8F4
```

Thus the stock producer increment is:

```text
GP+0xE8F4 = trunc(sample_rate / video_refresh_rate)
```

[BIN]

## Why the refresh-rate operand is closed

The same stock core's AV-info construction at `0x8073F990` selects one of two double constants according to its PAL/NTSC state and places that value into the timing structure.

At `0x80740A7C`, the SNES initialization loads the same selected refresh-rate double and combines it with the current sample-rate global.

The current sample-rate global is the already-closed XGO family-0x08 value:

```text
0x80C2D408 = 11025
```

for the stock SNES path.

## NTSC callback size

The Snes9x2005 lineage refresh rate is ~60.1 Hz.

Therefore:

```text
11025 / ~60.1 = ~183.45
truncation -> 183
```

The stock pending-audio threshold is 129 frames.

Since:

```text
183 >= 129
```

the stock NTSC built-in core crosses the callback threshold on every normal frame invocation.

Its normal callback frame count is therefore:

```text
183 stereo frames per emulated NTSC frame
```

[BIN formula + source-lineage refresh constant]

Unlike the maintained newer family source, this stock path does not retain a fractional 0.45-frame accumulator at this layer. It uses the truncated per-frame integer.

## PAL

The binary selects a separate PAL refresh-rate double.

The exact numeric PAL constant has not yet been recovered from its runtime-initialized storage, so the PAL integer callback size is not promoted here from inference alone.

The important architecture is nevertheless BIN-closed: it is the same `trunc(11025 / selected_refresh_rate)` formula.

## Frontend residence consequence — NTSC

Producer packet:

```text
P = 183 source frames/frame
```

XGO frontend consumer:

```text
C = 576 source frames/transfer
```

Therefore stock built-in SNES is now an integer `183/576` FIFO phase problem, not the earlier family-model `183/184` fractional sequence.

Because:

```text
gcd(183,576) = 3
```

the residual phase repeats after:

```text
576 / 3 = 192 producer callbacks
```

This permits an exact deterministic stock-BIN residence model.

## Relationship to maintained family Snes9x2005

The maintained pinned family revision computes a floating `samples_per_frame` and carries fractional remainder, yielding principally 183/184-frame callbacks.

The older XGO built-in binary computes the per-frame quantity once and truncates it to 183 for NTSC.

This is a small but real lineage/runtime difference.

The family model's ~26-ms mean was directionally useful, but the stock NTSC model can now be recomputed from the exact 183/576 geometry.

## Fidelity consequence [BIN/INF]

At 183 frames per ~60.1-Hz video frame, the callback supplies:

```text
183 * refresh_rate ~= 10998 samples/s
```

rather than the nominal 11025 exactly.

Whether the underlying mixer compensates elsewhere, or whether this creates a small stock pitch/time discrepancy, requires a separate trace before making a fidelity claim.

Do not yet classify this as an audible pitch error.

## Next work

1. Compute exact 183/576 stock NTSC frontend residence distribution.
2. Recover the PAL refresh constant/value and corresponding integer callback size.
3. Determine whether any other stock SNES path periodically compensates the truncated per-frame remainder.
4. Then combine the stock frontend distribution with the lower 576-unit/482-unit SND sawtooth.

## Hardware gate

Not reached.
