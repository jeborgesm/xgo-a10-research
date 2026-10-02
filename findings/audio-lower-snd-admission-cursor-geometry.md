# Audio lower-SND admission threshold and hardware cursor geometry

Date: 2026-10-01  
Branch: `research-audio-fidelity-latency`  
Status: **STATIC BIN ARCHAEOLOGY — NO HARDWARE CANDIDATE**

## Scope

This pass follows the concrete audio-device readiness callback `0x802FD5A4`, its helper `0x802FD720`, and the SND register getters used by that helper.

It closes the purpose of the previously unexplained derived value:

```text
(sample_num >> 1) + 2
960 -> 482
```

## Readiness callback [BIN]

The frontend submission helper waits on audio-device callback `+0x5C = 0x802FD5A4`.

For the normal device modes, `0x802FD5A4`:

1. reads private halfword `+0xFA`;
2. if it is zero, returns through the exceptional/assert path;
3. calls `0x802FD720`;
4. divides the returned distance by `+0xFA`;
5. returns true only when the quotient is at least one.

Therefore the lower device admits a new frontend submission only when the lower cursor distance is at least one complete `+0xFA` unit.

With stock `sample_num=960`:

```text
+0xFA = (960 >> 1) + 2 = 482
```

So **482 is the lower-device admission/refill threshold** for the stock 960 configuration. [BIN]

## Hardware cursor registers [BIN]

`0x802FD720` obtains two 16-bit values from the lower SND object:

```text
0x8030A174 -> MMIO +0x38
0x8030A198 -> MMIO +0x3A
```

The helper retains one cursor in private `+0x44` and computes the modular distance between the two cursors using private `+0x48` as the wrap modulus.

Conceptually:

```text
if cursor_A < cursor_B:
    distance = modulus - cursor_B + cursor_A
else:
    distance = cursor_A - cursor_B
```

That modular distance is returned to `0x802FD5A4`, which tests whether:

```text
distance / 482 >= 1
```

This proves that the readiness loop immediately above PCM submission is governed by **hardware-facing cursor geometry**, not merely by an arbitrary software delay.

## Lower ring/cursor state [BIN]

The submission callback `0x802FDF54` also uses private halfwords:

```text
+0x46 = software submission cursor/index
+0x48 = wrap modulus
```

It advances `+0x46` and wraps it to zero when it reaches `+0x48`.

The same `+0x48` value is used by the hardware-cursor distance helper. This ties the software producer position and hardware cursor comparison to a common lower circular geometry.

The setup path around `0x803073E0` initializes `+0x48`, forces it even when necessary, and clears both `+0x46` and `+0x44`.

Thus a second circular producer/consumer-style transport below the frontend PCM ring is now statically established. [BIN]

## Relationship to 960 [BIN]

The lower geometry now has two related stock values:

```text
sample_num = 960
admission threshold = 482
```

The setup path also programs 960 into the lower SND count register described in `audio-960-hardware-count-register.md`.

This is strong structural evidence that 960 configures the hardware transfer geometry while 482 is the corresponding software admission/refill threshold.

However, the exact physical unit of the cursors is still OPEN. We must not yet convert 482 or 960 directly into milliseconds.

## Queue topology update [BIN]

The proven path is now:

```text
frontend PCM ring
  producer/consumer offsets
  576-source-frame dequeue
        |
        v
optional 2x/4x low-rate repetition
        |
        v
lower SND circular geometry
  software cursor +0x46
  wrap modulus +0x48
  hardware cursors MMIO +0x38/+0x3A
  admission threshold +0xFA = 482
        |
        v
SND/I2SO count register (sample_num=960)
        |
        v
DAC/output
```

## Underrun/latency consequence

The lower device can refuse a new submission until its cursor-distance test reaches 482. This explains the blocking readiness loop observed in `0x8035C4A8`.

It also proves that queue occupancy below the frontend ring is actively flow-controlled against hardware cursor movement.

What remains OPEN is whether the returned distance represents free writable space or consumed/available units under the vendor's cursor naming convention. Because the callback is an admission predicate, it functions operationally as writable/admission capacity, but exact register naming should await the interrupt/register closure.

## Next offline target

1. Close the initialization formula and runtime value of private `+0x48` (lower wrap modulus).
2. Trace MMIO `+0x38/+0x3A` updates/interrupt semantics to identify producer versus hardware consumer.
3. Trace submission writes indexed by `+0x46` and determine the unit represented by one cursor step.
4. Then convert the lower queue geometry into milliseconds and combine it with frontend occupancy bounds.

## Hardware gate

**Not reached.** No hardware candidate is authorized.
