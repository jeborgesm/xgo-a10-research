# ALi HLD lineage closes XGO PCM descriptor identity and DMA depth command

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **SRC/UP + BIN CORRESPONDENCE**

## Exact public PCM descriptor match

Legacy ALi HLD source defines:

```c
struct pcm_output {
    UINT32 ch_num;          // +0x00
    UINT32 ch_mod;          // +0x04
    UINT32 samp_num;        // +0x08
    UINT32 sample_rata_id;  // +0x0C
    UINT32 inmode;          // +0x10
    UINT32 *ch_left;        // +0x14
    UINT32 *ch_right;       // +0x18
    ...
};
```

The XGO PCM submission callback `0x802FDF54` accesses the frontend descriptor at exactly those offsets:

```text
+0x00 mode/channel field
+0x08 sample/frame count
+0x14 left/source pointer
+0x18 right/source pointer
```

and its low-rate conversion doubles or quadruples `+0x08` while replacing +0x14/+0x18 with the scratch buffer.

This identifies the XGO structure as the same ALi `pcm_output` lineage, not an ad-hoc XGO descriptor.

## Cursor packing remains four stereo frames per unit

The ALi descriptor match initially raises a useful question because the lower ring advances in 16-byte cursor units.

Direct XGO code resolves it.

In the generic write path, one lower cursor position is filled by nested 2x2 loops that consume four 32-bit chunks from the two PCM channel pointers before incrementing private commit cursor +0x46 by one.

Each 32-bit channel word contains two 16-bit samples.

Therefore one 16-byte lower cursor unit represents:

```text
2 channels
* 2 packed 16-bit samples per 32-bit word
* 2 words per channel
= 4 stereo S16 time frames
```

This independently preserves the earlier unit closure:

> **1 lower cursor unit = 4 stereo S16 frames = 16 bytes.**

The public descriptor evidence does not invalidate that mapping.

## Commit callback identity

XGO object callback `+0x74 = 0x80304C50` performs:

```text
private +0x46
 -> snd low-level setter 0x8030A130
 -> SND +0x38
```

Thus private +0x46 is the software commit cursor whose packed 16-byte units are published to hardware.

## SND_CHK_PCM_BUF_DEPTH mapping

Public ALi command:

```text
SND_CHK_PCM_BUF_DEPTH = SND_IO + 18 = 0x21
```

is documented as:

> Get the PCM DMA buffer size in frame unit.

XGO command 0x21 dispatches to `0x803095B0`, which writes the GP global:

```text
0x80C2D02C
```

to the caller.

Its initialized value is:

```text
8
```

This is the same value already recovered as the lower-SND allocation depth factor `G=8`.

Therefore:

> **The lower allocation factor 8 is the legacy PCM DMA buffer depth.** [BIN+SRC]

This explains why it appears as a first-class sound-driver configuration value rather than an arbitrary allocator multiplier.

## SND_GET_SAMPLES_REMAIN diagnostic path

Public ALi command:

```text
SND_GET_SAMPLES_REMAIN = SND_IO + 34 = 0x31
```

matches an implemented XGO command-table case at 0x31.

The XGO handler calls `0x80309100` and writes its result to the caller-provided output pointer.

That helper combines lower queue-distance terms, including the already-proven commit/playback queued distance.

This provides a second stock diagnostic surface for measuring remaining PCM during gameplay.

Exact conversion of its returned legacy “samples remain” value into stereo time frames still needs one final unit cross-check, so it should not yet replace direct cursor arithmetic.

## Gameplay diagnostic value

We now have two stock legacy queries useful for a future instrumented CPS1 diagnostic:

```text
0x15  IS_PCM_EMPTY
0x31  SND_GET_SAMPLES_REMAIN
```

and one static capacity query:

```text
0x21  SND_CHK_PCM_BUF_DEPTH -> 8
```

This means real hardware tests can eventually measure lower-buffer behavior through the driver's own API instead of adding speculative register polling.

## Evidence boundary

- ALi HLD struct/command definitions: **SRC/UP**
- exact XGO descriptor offsets: **BIN**
- four-stereo-frame cursor packing: **BIN**
- command 0x21 returns 8: **BIN**
- 0x21 = PCM DMA depth: **SRC+BIN correspondence**
- command 0x31 implementation: **BIN**
- exact user-facing unit of XGO 0x31 result: **OPEN**

## Hardware gate

The minimal native-22050 proof remains ready; these diagnostics are optional follow-up instrumentation and are not required in the first A/B artifact.
