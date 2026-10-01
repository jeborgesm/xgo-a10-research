# Audio lower-SND ring capacity and cursor-unit closure

Date: 2026-10-01  
Branch: `research-audio-fidelity-latency`  
Status: **STATIC BIN ARCHAEOLOGY — NO HARDWARE CANDIDATE**

## Scope

This pass closes two items left OPEN by `audio-lower-snd-admission-cursor-geometry.md`:

- runtime value of private `+0x48`, the lower circular wrap modulus;
- the byte size represented by one lower cursor step.

Direct evidence is from the preserved stock XGO `bisrv.asd`, SHA-256 `869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf`.

## Global geometry constant [BIN]

The lower-SND initialization path uses GP global `+0x9C08`.

There is exactly one store to this GP slot in the relevant firmware image:

```text
0x8030A040  li    v0, 8
0x8030A044  sw    v0, 0x9C08(gp)
```

The lower-buffer setup at `0x80307360...` subsequently reads this value.

Therefore the active stock geometry constant is:

```text
G = 8
```

## Lower ring allocation [BIN]

The allocation size is constructed as:

```text
((G << 9) + G) << 5
= G * 513 * 32
```

With `G=8`:

```text
allocation = 131,328 bytes
```

The allocated base is retained by the lower audio private state.

## Wrap modulus [BIN]

The same setup computes private halfword `+0x48` as:

```text
((G << 9) + G) << 1
= G * 513 * 2
```

With `G=8`:

```text
+0x48 wrap modulus = 8,208 cursor units
```

If the result were odd the code clears its low bit; 8,208 is already even.

It then initializes:

```text
+0x46 = 0   software submission cursor
+0x44 = 0   retained hardware cursor
```

## One cursor unit is exactly 16 bytes [BIN]

The post-resampler submission callback `0x802FDF54` uses the lower software cursor as a destination index.

At the final lower-ring copy boundary it forms:

```text
destination = lower_ring_base + (cursor << 4)
copy_bytes  = cursor_count << 4
```

and calls the stock memcpy routine. It then advances `+0x46` by the corresponding cursor count and wraps against `+0x48`.

Therefore:

```text
1 lower cursor unit = 16 bytes
```

This is independently consistent with the allocation:

```text
8,208 units * 16 bytes = 131,328 bytes
```

The lower circular storage geometry is therefore closed exactly.

## PCM-domain interpretation [BIN]

The established normal transport entering this lower path is stereo signed 16-bit PCM:

```text
4 bytes per stereo frame
```

Thus one 16-byte lower cursor unit contains:

```text
4 stereo S16 PCM frames
```

and the complete lower circular allocation can represent:

```text
131,328 / 4 = 32,832 stereo frames
```

At the normalized 44.1-kHz hardware rate this storage capacity corresponds to:

```text
32,832 / 44,100 = 744.49 ms
```

This is **storage capacity, not normal queued latency**. The firmware flow-control logic does not prove that the ring normally fills to capacity.

## Admission threshold in bytes/frames [BIN]

The previously closed readiness threshold is:

```text
+0xFA = (sample_num >> 1) + 2
sample_num = 960
threshold = 482 cursor units
```

Now that the cursor unit is closed:

```text
482 * 16 = 7,712 bytes
7,712 / 4 = 1,928 stereo S16 frames
1,928 / 44,100 = 43.72 ms
```

Operationally, the readiness callback waits until its modular hardware-cursor distance reaches at least 482 lower-ring units before admitting another submission.

The 43.72-ms figure is therefore the **PCM duration represented by one admission-distance threshold at 44.1 kHz**, not a claim that 43.72 ms is always queued or added as latency.

## Low-rate block sizes in lower cursor units [BIN]

After the proven integer repetition stage:

```text
22050 source:
  576 source frames
  -> 1,152 frames @ 44.1 kHz
  -> 4,608 bytes
  -> 288 lower cursor units

11025 source:
  576 source frames
  -> 2,304 frames @ 44.1 kHz
  -> 9,216 bytes
  -> 576 lower cursor units
```

This is useful because it shows that the frontend submission size and the lower admission threshold are not identical contracts:

```text
admission threshold = 482 cursor units
FBA 22.05-kHz expanded block = 288 units
SNES 11.025-kHz expanded block = 576 units
```

The lower driver therefore cannot be modeled as a simple one-threshold-equals-one-frontend-block system.

## Queue topology now closed geometrically [BIN]

```text
frontend ring
  18,432 bytes
  4,608 source stereo frames
  576-source-frame dequeue
       |
       v
optional low-rate repetition
  22.05k -> 1,152 frames / 4,608 bytes
  11.025k -> 2,304 frames / 9,216 bytes
       |
       v
lower SND circular storage
  131,328 bytes
  8,208 cursor units
  16 bytes / cursor unit
  4 stereo S16 frames / unit
  software cursor +0x46
  hardware cursor state +0x44
  wrap modulus +0x48 = 8,208
  admission threshold +0xFA = 482 units
       |
       v
SND/I2SO hardware
```

## Latency boundary

We can now calculate the **capacity** of both software queue layers, but normal emulator-to-DAC latency remains OPEN because normal occupancy is not yet known.

Do not add the 744.49-ms lower capacity to the frontend capacity and call the result latency.

The next required closure is cursor semantics over time: identify which MMIO cursor is hardware consumption, establish the normal producer-to-consumer distance, and determine startup/prebuffer behavior.

## 960 semantics

This finding does not change the safe wording from `audio-960-hardware-count-register.md`:

> 960 is the stock `sample_num` and is programmed as a lower SND hardware count-register value.

Although `(960 >> 1) + 2 = 482` directly creates the admission threshold, the exact vendor/hardware meaning of the 960 register itself remains OPEN.

## Next offline target

Trace startup and steady-state cursor behavior:

1. identify which of MMIO `+0x38/+0x3A` is the advancing hardware-consumption cursor;
2. identify how the software cursor is committed to hardware;
3. recover any startup/prebuffer threshold;
4. determine whether silence, old PCM, or stopped DMA occurs when producer data runs out;
5. derive normal lower-ring occupancy and only then calculate latency.

## Hardware gate

**Not reached.** No hardware candidate is authorized.
