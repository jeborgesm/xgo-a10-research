# Audio lower-SND cursor roles and startup admission

Date: 2026-10-01  
Branch: `research-audio-fidelity-latency`  
Status: **STATIC BIN ARCHAEOLOGY — NO HARDWARE CANDIDATE**

## Scope

This pass follows the lower-SND cursor helper and submission callback after closure of:

- 8,208-unit lower circular modulus;
- 16 bytes per cursor unit;
- 482-unit readiness/admission threshold.

Goal: distinguish the software submission cursor from the hardware progress cursors and determine whether stock has a separate large startup prebuffer.

## Cursor roles [BIN]

The lower submission callback owns private halfword `+0x46`.

It uses that value to select the destination inside the 131,328-byte lower PCM ring:

```text
dst = lower_ring_base + (+0x46 << 4)
```

After copying a submission it advances `+0x46` by the number of 16-byte cursor units written and wraps it against `+0x48 = 8208`.

Therefore:

> private `+0x46` is the software PCM write/submission cursor.

The readiness helper `0x802FD720` reads the two SND hardware cursor registers through:

```text
0x8030A174 -> MMIO +0x38
0x8030A198 -> MMIO +0x3A
```

and retains one sampled hardware cursor in private `+0x44`.

The modular-distance calculation uses the same `+0x48` modulus as the software write cursor. Thus the hardware cursor domain and software write cursor share the exact 8,208-unit circular coordinate system.

## Startup state [BIN]

Lower-ring initialization clears:

```text
+0x44 = 0
+0x46 = 0
```

after establishing `+0x48 = 8208`.

No separate "fill N percent of the 131,328-byte ring before enabling playback" threshold has been found in the traced startup path.

The admission predicate is instead the same runtime predicate already closed:

```text
modular hardware-cursor distance >= +0xFA
```

with:

```text
+0xFA = 482 units
```

This is the only proven lower-ring gating threshold in the path from frontend submission to the SND transport.

Therefore the static evidence does **not** support a claim that stock intentionally prebuffers hundreds of milliseconds merely because the lower allocation can hold 744.49 ms.

## Operational interpretation [BIN/INF]

The lower ring is large storage, but the active flow-control granularity is much smaller:

```text
482 units
= 7,712 bytes
= 1,928 stereo S16 frames
= 43.72 ms of 44.1-kHz PCM
```

The software producer advances in variable submission chunks (for example 288 units for the 22.05-kHz FBA path after 2x expansion and 576 units for the 11.025-kHz SNES path after 4x expansion), while admission is controlled by hardware progress in the shared circular coordinate system.

This is consistent with a producer writing opportunistically into a much larger circular backing store rather than deliberately maintaining the ring near full.

That interpretation is strong, but **normal producer-to-hardware-consumer distance is still not statically measured**.

## Hardware cursor naming boundary

The two MMIO registers at `+0x38` and `+0x3A` are proven to be cursor/progress values used by the lower circular transport.

The exact vendor labels and which register is the instantaneous playback/DMA consumer versus its paired boundary/reference cursor remain OPEN pending interrupt-path closure.

Do not assign speculative names such as "DMA read pointer" to one register yet.

## Latency consequence

We can now reject one pessimistic model:

> lower-ring capacity (744.49 ms) == intentional stock prebuffer/latency.

There is no static evidence for that model.

What is proven is a **43.72-ms admission granularity** in the normalized 44.1-kHz PCM domain.

This still cannot be added mechanically to the frontend 576-frame block duration to produce an exact emulator-to-DAC latency number. Admission granularity and steady-state queued occupancy are different quantities.

## Pause/menu/restart implication [BIN/OPEN]

Because both software and retained cursor state are explicitly reset during lower-ring initialization, a full audio-device reinitialization does not inherit arbitrary old cursor coordinates.

Whether the PCM storage itself is zeroed is separate and remains OPEN. Therefore stale-audio behavior across a restart cannot yet be declared impossible.

Pause/menu paths that do not perform this lower initialization must be analyzed independently.

## Next offline target

Trace the SND interrupt/status path associated with the `+0x38/+0x3A` cursor pair and determine:

1. which cursor advances with actual hardware consumption;
2. how/when the paired cursor is committed;
3. whether the device repeats, silences, stops, or reuses data on underrun;
4. whether interrupt cadence exposes normal steady-state producer lead.

Then derive a defensible latency range rather than using total ring capacity.

## Hardware gate

**Not reached.** No hardware candidate is authorized.
