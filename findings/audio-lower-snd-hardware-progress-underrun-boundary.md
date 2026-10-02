# Audio lower-SND hardware progress and underrun boundary

Date: 2026-10-01  
Branch: `research-audio-fidelity-latency`  
Status: **STATIC BIN ARCHAEOLOGY — NO HARDWARE CANDIDATE**

## Scope

This pass follows the SND cursor pair used by the lower admission helper after closure of:

- lower PCM write cursor `+0x46`;
- common wrap modulus `+0x48 = 8208`;
- 16 bytes per lower cursor unit;
- admission threshold `+0xFA = 482` units.

The goal is to distinguish hardware progress from software submission and bound what static analysis can say about underrun.

## Hardware progress is sampled, not synthesized [BIN]

The readiness path does not advance its own notion of playback time. It reads the two 16-bit values from the SND MMIO block on every admission check:

```text
MMIO +0x38
MMIO +0x3A
```

One sampled value is retained at private `+0x44`; the modular distance is then calculated in the common 8208-unit circular domain.

No software increment of these MMIO-derived values occurs in the readiness helper.

Therefore the changing distance that eventually releases the blocked producer is driven by **lower SND hardware progress**, not by a software timer or frontend frame counter. [BIN]

## Producer/consumer relationship [BIN/INF]

The software submission cursor `+0x46` advances only when PCM has actually been copied into the lower circular storage.

The readiness predicate blocks new submission until the hardware cursor geometry reports at least 482 units of admissible distance.

Operationally this establishes:

```text
software producer: +0x46
hardware progress: MMIO +0x38/+0x3A
flow-control threshold: 482 units
```

The exact vendor names of the two hardware registers remain unavailable, so this finding deliberately does not assign "read pointer" versus "limit pointer" labels beyond what the code proves.

## No frontend underrun fill [BIN]

The upper consumer behavior remains unchanged:

- fewer than 576 source frames in the frontend ring -> wait with `dly_tsk(1)`;
- no partial frontend block;
- no zero-filled replacement frontend block.

Likewise, the lower readiness path merely waits for hardware progress before admitting another copied block. It does not generate silence in that predicate.

Thus there is no software silence synthesis in either of the two admission loops already closed.

## What happens when accepted PCM is exhausted [OPEN]

Static code traced so far does **not** prove what the SND/I2SO engine emits after it reaches the end of valid accepted PCM while no replacement block is ready.

Possible behaviors that remain to distinguish include:

- stop/hold transport;
- emit hardware zero/silence;
- repeat stale memory;
- continue around the circular buffer;
- assert an underrun status handled elsewhere.

None is promoted without evidence.

This is now a genuine lower-hardware/interrupt question, not a frontend-ring question.

## Latency model update [BIN/INF]

The producer is released by real hardware cursor movement. Therefore the 482-unit threshold is a hardware-progress-based refill/admission granularity, not an arbitrary periodic sleep.

At 44.1-kHz stereo S16:

```text
482 units * 16 bytes/unit = 7,712 bytes
7,712 / 4 = 1,928 frames
1,928 / 44,100 = 43.72 ms
```

This means hardware must expose 482 units of progress in the common lower-ring domain before the blocked admission test succeeds.

It still does not prove that steady-state producer lead equals exactly 482 units: submission chunks can be 288 units (FBA 22.05-kHz expanded block) or 576 units (SNES 11.025-kHz expanded block), so producer lead can cross the threshold in different-sized steps.

## Important scheduler separation

The hardware-driven lower refill gate is independent of the frontend frameskip/scheduler findings. A late emulation frame may delay production, but the lower admission geometry itself is governed by SND progress.

Do not "fix" this investigation by changing frameskip or scheduler behavior; that remains a separate experimental lane.

## Static-analysis boundary reached for exact underrun waveform

We can continue to search interrupt/status handlers and sibling source for register names and status bits. However, the exact **analog/digital waveform emitted at the moment accepted PCM runs dry** cannot be inferred merely from the cursor arithmetic.

If the vendor hardware documentation or maintained HC15xx source identifies the underrun behavior, that can close it as SRC/UP evidence. Otherwise direct hardware capture would eventually be required.

This is not yet authorization for a firmware candidate.

## Next offline target

Before requesting hardware:

1. compare SF2000/GB300/UniFrog HC15xx SND code for the same cursor/count register layout;
2. recover names/semantics for SND offsets `+0x38/+0x3A`, count offsets `+0x11C/+0x19C`, and associated interrupt/status bits;
3. determine whether sibling source documents underrun behavior;
4. compare their low-rate conversion helper with XGO's 2x/4x zero-order hold.

Only if those sources fail to close actual steady-state occupancy/underrun should a minimal observation-only hardware diagnostic be considered.

## Hardware gate

**Not reached for a firmware candidate.** Offline family/source comparison remains available.
