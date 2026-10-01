# XGO stock FBA callback cadence versus 576-frame frontend consumer quantum

Date: 2026-10-01  
Branch: `research-audio-fidelity-latency`  
Status: **BIN + SRC/UP CROSSWALK — FBA BATCHING MODEL CORRECTED**

## Important correction

Earlier bounded-latency notes described the frontend's 576-source-frame consumer quantum as an "upper batch" and used its full duration as a possible per-sample batching wait.

For stock FBA that wording is too coarse.

The stock-family FBA core contract is already recovered in this repository:

```text
AUDIO_SAMPLERATE     = 22050
AUDIO_SEGMENT_LENGTH = 367 samples/frame
```

The upstream FBA2012 libretro structure shows the relevant cadence:

```text
ForceFrameStep()
...
video_cb(...)
audio_batch_cb(g_audio_buf, nBurnSoundLen)
```

and `nBurnSoundLen` is the per-frame segment length.

Therefore stock-family FBA delivers approximately **367 source frames once per emulated video frame**, not 576 frames in one normal callback. [SRC/UP + family reconstruction]

The XGO stock callback then writes those frames into its 0x4800-byte frontend ring [BIN].

## Consequence: 576 is a consumer threshold, not the core callback size

For FBA:

```text
core callback A: +367 frames
frontend occupancy: 367 < 576 -> consumer waits

core callback B: +367 frames
frontend occupancy: 734 >= 576 -> consumer removes 576

remainder: 158 frames
```

The consumer therefore accumulates across frame callbacks.

This distinction materially changes the sample-age model.

## Exact deterministic occupancy sequence ignoring task race

With producer increment `P=367` and consumer quantum `C=576`, and assuming one 576-frame consume whenever occupancy reaches/exceeds 576, the residual evolves:

```text
r[n+1] = (r[n] + 367) mod 576
```

because 367 < 576 and occupancy cannot require more than one 576-frame removal per FBA callback.

The residual phase walks through the 576-frame space rather than staying at one fixed value.

Because:

```text
gcd(367,576) = 1
```

the idealized residual sequence visits every integer phase over a 576-callback cycle.

Thus the frontend ring is a genuine asynchronous batching reservoir for FBA; it is not a simple one-callback/one-consume pipeline.

## Time scales

One stock FBA callback contains:

```text
367 / 22050 = 16.644 ms of source PCM
```

The lower consumer quantum represents:

```text
576 / 22050 = 26.122 ms
```

Therefore a 576-frame transfer normally spans PCM generated across two or occasionally more callback phases depending on residual occupancy.

## Correct sample-wait interpretation

A newly produced sample does **not** necessarily wait a full 26.122 ms in the frontend ring.

Its wait depends on current residual occupancy and its position inside the 367-frame callback.

At one extreme, a sample arriving just before the threshold-crossing portion can be consumed almost immediately.

At the other extreme, a sample left in the post-consume residual can remain until enough later FBA frame callbacks arrive to complete a future 576-frame block.

The full 576-frame source duration remains a useful absolute batching scale, but it is not a fixed additive delay.

## Frame-phase relationship

Upstream FBA2012 structure performs the emulated frame step before invoking the audio callback for that frame.

The maintained HC15xx frontend wrapper calls the core's `retro_run()` directly after hotkey/input frontend work.

Therefore the family source architecture is:

```text
frontend per-frame call
 -> core retro_run
    -> emulate frame
    -> video callback
    -> one audio callback for nBurnSoundLen
```

This supports treating FBA audio production as frame-paced.

Exact instruction ordering of the XGO stock core should still be classified from its binary/reconstructed core rather than assumed solely from upstream.

## Lower-SND interaction

FBA lower submission quantum after XGO's 2x repetition remains:

```text
576 source frames
 -> 1152 output frames
 -> 288 lower units
 -> 26.122 ms represented audio
```

The lower queue admits this block only when existing queued audio is below 482 units.

Therefore FBA has two independent phase systems:

```text
core -> frontend ring:
  +367 source frames per emulated frame
  -576 source frames per consumer transfer

lower SND:
  +288 units per converted transfer
  continuous hardware playback
  admit next transfer below 482 queued units
```

The relative phase of these two sawtooths determines actual instantaneous latency.

## Correction to previous conservative envelope

The previous `<=95.873 ms` FBA number was constructed by adding:

```text
full 576-frame frontend quantum 26.122 ms
+
maximum arithmetic lower post-submit queue 69.751 ms
```

It remains a deliberately conservative arithmetic envelope, but it should **not** be read as a likely or typical FBA latency.

Now that the producer cadence is known, typical frontend sample age must be modeled from the 367/576 residual sequence rather than assigning every sample a full 576-frame wait.

## Next work

1. Compute the idealized FBA frontend residence-time distribution from the 367/576 phase sequence.
2. Reconcile that with lower 288-unit/482-unit queue phase.
3. Recover equivalent producer callback sizes for the stock SNES 11025 path.
4. Keep scheduler/task jitter separate from deterministic PCM batching.

## Hardware gate

Not reached.
