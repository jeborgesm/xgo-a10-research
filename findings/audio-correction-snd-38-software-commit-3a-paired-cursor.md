# Correction — XGO SND +0x38 is software-committed; +0x3A is the paired hardware-maintained cursor

Date: 2026-10-01  
Branch: `research-audio-fidelity-latency`  
Status: **BIN CORRECTION / SUPERSEDING CURSOR INTERPRETATION**

## Why this correction exists

Earlier findings correctly established that the lower circular transport uses SND offsets `+0x38/+0x3A`, but described both too broadly as hardware-facing/hardware-progress cursors.

Deeper tracing of the post-transfer callback closes an asymmetry between them.

## Post-transfer commit callback [BIN]

The device callback at:

```text
object +0x74 = 0x80304C50
```

executes:

```text
load lower private state
load SND object/base
load private halfword +0x46
call 0x8030A130
```

The low-level helper `0x8030A130` is exact:

```text
a1 &= 0xffff
[a0 + 0x38] = a1
return
```

Therefore after the lower PCM submission/copy path advances private `+0x46`, the `+0x74` callback **commits that software cursor value into SND +0x38**.

This proves:

```text
private +0x46 -> software lower-ring cursor
SND +0x38     -> software-programmed/committed SND cursor or boundary
```

The exact vendor name of `+0x38` remains OPEN.

## Paired +0x3A cursor [BIN]

The readiness/distance helper reads:

```text
0x8030A174 -> lhu [SND +0x38]
0x8030A198 -> lhu [SND +0x3A]
```

The `+0x38` value is now proven to be software writable/committed.

No corresponding write from the post-transfer commit path to `+0x3A` has been found.

Therefore the safe current distinction is:

```text
+0x38 = software-committed cursor/boundary
+0x3A = paired SND-maintained cursor observed by the software
```

It is now reasonable to investigate `+0x3A` as the actual hardware-progress/playback cursor, but that exact name is not promoted until its update mechanism is closed.

## Distance arithmetic [BIN]

The lower helper samples both cursors and computes a modular distance using `+0x48 = 8208`.

What remains unsafe is assigning that distance the semantic name "free space" or "queued data" before the operating mode and pointer convention are fully closed.

The same arithmetic can represent either quantity depending on which boundary the hardware register means.

Therefore earlier prose describing the 482-unit comparison as definitively "writable/admission capacity" is superseded by:

> **482 is the threshold applied to the modular distance between the software-committed SND +0x38 cursor and paired SND +0x3A cursor.**

The operational fact that the upper helper waits on this predicate remains BIN-proven.

## Initialization [BIN]

XGO setup also calls the `+0x38` setter with zero, so the software-committed cursor begins at zero.

This further supports its ownership by the software submission side.

## Relationship to HC15xx SDK [UP/INF]

The later HC15xx sound ABI exposes:

- `get_avail()`
- `SND_IOCTL_AVAIL_MIN`
- transfer gating on available frames;
- `SND_IOCTL_DELAY` for queued-frame/backlog reporting.

The XGO cursor-distance predicate is structurally compatible with an availability-style calculation, but exact old-driver mapping is still OPEN.

This correction makes finding XGO's equivalent of `get_avail` versus `delay` the immediate priority.

## Superseded wording

The following earlier phrases should no longer be used without this correction:

- "two hardware cursors at +0x38/+0x3A"
- "hardware progress is sampled from both cursors"
- any claim that neither cursor is software-updated

Retain the geometry and threshold numbers from those findings; only cursor ownership/semantic naming changes.

## New proven lower submission sequence [BIN]

```text
PCM copied into lower circular storage
        |
        v
private +0x46 advances
        |
        v
object +0x74 callback
        |
        v
0x8030A130
        |
        v
SND +0x38 = private +0x46
```

This is the first exact closure of how software tells the lower SND engine that the circular submission boundary has moved.

## Next target

1. Find every writer to SND `+0x3A` and determine whether only hardware changes it.
2. Trace the `+0x38/+0x3A` distance helper under the active playback mode.
3. Identify whether that helper corresponds to available space, queued delay, or a start threshold.
4. Then revisit the 482-unit latency interpretation.

## Hardware gate

Not reached.
