# Audio 960 semantics — hardware count-register closure

Date: 2026-10-01  
Branch: `research-audio-fidelity-latency`  
Status: **STATIC BIN ARCHAEOLOGY — NO HARDWARE CANDIDATE**

## Scope and correction

This pass follows the active I2SO configuration routine at `0x80306CDC` far enough to determine what stock firmware actually does with the caller-supplied value 960.

Earlier findings correctly separated 960 from the frontend 576-frame dequeue and from the 1152/2304-frame low-rate resampler outputs, but described 960 generically as a lower-SND "working-buffer count." This finding tightens that wording.

## Retained lower-driver state [BIN]

At entry:

```text
a1 = requested hardware rate
a2 = sample_num
a3 = precision
```

The routine masks `a2` to 16 bits and retains it as `s0`.

For the normal callers:

```text
sample_num = 960
```

It stores this value at audio-private state offset `+0x108`.

It also derives:

```text
(sample_num >> 1) + 2
```

and stores that 16-bit value at private offset `+0xFA`.

For 960 this is:

```text
960 / 2 + 2 = 482
```

Thus 960 and the derived 482 are both persistent lower-SND configuration values.

## Direct hardware-register programming [BIN]

Later in the same active setup path, the retained `+0x108` value is passed to one of two low-level register setters:

```text
0x8030A830(device, value)
0x8030ADA4(device, value)
```

depending on the selected SND/I2SO route.

These are not abstract buffer-management helpers. Each writes the low 16 bits of a memory-mapped SND register shadow/window:

```text
0x8030A830 -> device MMIO +0x11C low 16 bits
0x8030ADA4 -> device MMIO +0x19C low 16 bits
```

A special route can multiply the retained value by four before programming the register; the normal path passes it directly.

Therefore 960 is now proven to be a **hardware-facing SND count-register value** used by the active output setup.

## Safe semantic boundary

CONFIRMED [BIN]:

- caller supplies 960 as `sample_num`;
- lower driver retains 960 at private `+0x108`;
- lower driver derives 482 at private `+0xFA`;
- 960 is programmed into a 16-bit SND hardware count field at MMIO offset `+0x11C` or `+0x19C` for the selected route;
- 960 is downstream of the frontend ring and low-rate resampler.

OPEN:

- exact vendor name of the `+0x11C/+0x19C` register;
- whether the hardware interprets the count as samples, words, halfwords, or another transport unit;
- whether it is a period length, terminal count, FIFO threshold, DMA count, or related playback counter;
- exact meaning of the derived 482 value.

Accordingly, prefer:

> 960 is the stock `sample_num` and is programmed as a lower SND hardware count-register value.

Do not yet call it a DMA period or assign 20/21.8 ms of latency solely from its numeric value.

## Rate normalization remains separate [BIN]

The same setup routine explicitly recognizes source rates 11025 and 22050 and substitutes 44100 into its hardware-rate state while retaining the original source rate separately.

This agrees with the independently closed software repetition converter:

```text
11025 -> repeat each stereo frame 4x -> 44100 hardware path
22050 -> repeat each stereo frame 2x -> 44100 hardware path
```

The 960 hardware count is therefore configured in the normalized hardware-rate domain, but its exact unit remains to be closed.

## Why this matters for latency

This removes an unsafe assumption from the latency model. Although 960/48000 = 20 ms and 960/44100 ~= 21.77 ms numerically, those durations are not yet evidence-backed queue depths until the hardware register semantics are identified.

The correct latency investigation must now trace the register's consumer/interrupt behavior rather than treating the debug label `sample_num` as sufficient proof of a DMA period.

## Next offline target

Trace:

1. reads/writes of SND MMIO offsets `+0x11C` and `+0x19C`;
2. interrupt/status helpers associated with those fields;
3. use of private `+0xFA` (482 for the stock 960 setting);
4. producer/consumer ownership changes around the corresponding interrupt;
5. the descriptor accepted after the 2x/4x low-rate conversion.

This should determine the exact unit of 960 and the true lower-level queued duration.

## Hardware gate

**Not reached.** No hardware candidate is authorized.
