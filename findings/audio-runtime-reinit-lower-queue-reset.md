# Runtime sound reinit resets the lower SND queue as well as the frontend FIFO

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **BIN — LOWER RESET CLOSED; PHYSICAL EMPTY OUTPUT STILL OPEN**

## Major closure

The earlier runtime-reinit checkpoint proved that `sound_init @ 0x8035C998` resets the frontend PCM FIFO producer/consumer offsets.

It was still OPEN whether already-queued lower-SND audio survived while the frontend rebuilt.

It does not.

The same sound-init call executes the active sound object's configuration/reset callback before restarting the lower transport, and that callback explicitly clears lower queue/cursor state and writes the primary SND commit cursor back to zero.

## Call chain [BIN]

Every `sound_init` obtains the active class-`0x01090000` sound object and calls:

```text
0x8027A0AC
```

For the normal active object states this dispatches object `+0xA0`.

The concrete constructor at `0x80309C34` installs:

```text
object +0xA0 = 0x80308BB4
object +0x98 = 0x80308464
```

Therefore the sound-init sequence includes:

```text
0x80308BB4   lower sound configuration/reset
...
0x80308464   lower sound start/service initialization
```

before the later legacy controls including ALSA-mode enable.

## Lower reset behavior in 0x80308BB4 [BIN]

The configuration/reset path disables the lower service-enable groups and later clears the lower queue state.

Among the explicit resets:

```text
private +0x46 = 0
private +0x52 = 0
private +0x58 = 0

private +0x62 = 0
private +0x68 = 0
private +0x6E = 0

private +0x64 = 0
private +0x6A = 0
private +0x70 = 0

private +0x7C = 0
private +0x7E = 0
```

and multiple associated lower buffers are memset to zero.

The path then programs the zeroed primary cursor through:

```text
0x8030A130(SND_base, private+0x46)
```

`0x8030A130` directly performs:

```text
old = SND[+0x38]
SND[+0x38] = new_value
```

so runtime reinit explicitly writes:

> **SND +0x38 software commit cursor = 0**. [BIN]

The analogous secondary/tertiary stream cursors are also programmed from their zeroed private fields.

## Playback cursor +0x3A boundary

No matching software write to primary SND `+0x3A` has been found in this reset path.

That is consistent with the previous classification:

```text
+0x38 = software commit cursor
+0x3A = hardware playback/consumption progress
```

The exact hardware action that resets/stops/rebases `+0x3A` when the lower transport is reconfigured remains OPEN.

Do not assume a direct software write exists.

## Lower start after reset [BIN]

The subsequent object-`+0x98` callback `0x80308464` re-enables lower SND service groups through `0x80306168`.

That helper enables SND control bits for masks `0x04`, `0x40`, and `0x80`, and the start path also enables the broader SND control field through `0x8030B238`.

The exact vendor names of these enable bits remain OPEN, but the ordering is clear:

```text
lower transport/config state cleared
 -> lower cursor/buffers reset
 -> lower service/start controls enabled
 -> volume applied
 -> +0x15D periodic mode cleared
 -> ALSA mode enabled
```

## Complete runtime-reinit queue picture [BIN]

The runtime path now closes both software queue levels:

```text
L23 may remain OPEN
        ↓
lower SND configuration/reset
        ↓
lower queued PCM/cursor state cleared
        ↓
lower transport/service restarted
        ↓
frontend producer = 0
frontend consumer = 0
        ↓
frontend must accumulate >=576 fresh source frames
        ↓
first new lower PCM submission
```

Therefore old lower queued audio does **not** simply continue draining while the upper FIFO rebuilds.

The reinit creates a genuine digital discontinuity between old and newly accumulated PCM.

## SNES consequence

For normal stock NTSC SNES:

```text
183 fresh source frames per emulated frame
frontend threshold = 576
```

After reset:

```text
183
366
549
732 -> first 576-frame frontend transfer becomes possible
```

So fresh lower-SND PCM cannot be supplied until the fourth normal post-reset SNES callback, absent another path changing the accumulator.

The exact wall-clock silence at the DAC is still not stated because:

- reinit timing relative to the next emulated frame is not yet pinned;
- hardware `+0x3A` empty/reset behavior remains open;
- ALSA-mode/fade behavior may shape the physical output.

## Noise significance

This materially strengthens the runtime-reinit pop/gap hypothesis:

Initial startup:

```text
configure/reset queues
 -> initialize sound
 -> L23 open
```

Runtime reinit:

```text
L23 already open
 -> reset lower queue
 -> reset frontend queue
 -> rebuild fresh PCM
```

The stock firmware therefore protects initial startup with the analog speaker gate but does not use that gate around an equivalent lower+upper queue reset during runtime.

This is now a concrete, code-backed **noise/discontinuity improvement surface**, not merely a suspicious call ordering.

It still does not prove the subjective severity of the artifact.

## Candidate discipline

No hardware candidate yet.

If this lane eventually reaches hardware testing, a gate-assisted reinit should be tested separately from:

- resampler changes;
- frontend quantum changes;
- lower admission threshold changes;
- mono folding.

## Next target

Close the hardware-side empty/reset behavior:

1. what happens to playback cursor `+0x3A` when the lower path is reset;
2. what ALSA mode does at empty;
3. how underrun fade affects the DAC sample during the fresh-PCM gap;
4. what condition can safely replace an arbitrary delay before reopening L23.

## Hardware gate

Not reached.
