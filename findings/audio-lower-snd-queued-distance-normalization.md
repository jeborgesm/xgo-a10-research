# Lower SND queued-distance normalization helper at 0x802FD790

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **BIN; PUBLIC API NAME/UNIT OPEN**

## Function

`0x802FD790` is now decoded far enough to remove an important ambiguity.

It begins by calling the already-closed queued-distance helper:

```text
0x802FD790
  -> 0x802FD720
```

where:

```text
queued = (commit38 - playback3A) mod 8208
```

If queued is zero, `0x802FD790` returns zero.

Otherwise it selects a 16-bit divisor from the active lower-SND configuration/state and returns:

```text
queued / divisor
```

using integer division.

## Exact binary structure [BIN]

After obtaining queued distance in `v0`:

```text
queued -> a0
if queued == 0:
    return 0
```

The helper then inspects halfword fields at:

```text
+0x62
+0x64
+0x66
```

of the lower object/private state.

Depending on equality/current-position relationships it either:

- uses the halfword at private `+0xDA`; or
- indexes the table reachable from object/private `+0x28` and obtains a halfword divisor from the selected entry.

Finally:

```text
return queued / selected_divisor
```

No multiplication by milliseconds or sample rate occurs inside this helper.

## Call sites

Direct JAL references occur at:

```text
0x80304D50
0x80305558
```

The latter caches/compares the returned 16-bit value as part of higher-level sound state handling.

This confirms that `0x802FD790` is a **normalized queued-depth/delay quantity**, not the raw hardware cursor itself.

## Important correction / evidence boundary

It is tempting to name this function `snd_delay` because the maintained HCRTOS API exposes `SND_IOCTL_DELAY`.

Do not promote that name yet.

The binary proves:

```text
raw queued cursor distance
       ↓
configuration-dependent divisor
       ↓
small integer normalized backlog value
```

It does not yet prove whether the public semantic unit is:

- periods;
- fragments;
- milliseconds;
- frames;
- another legacy SDK delay unit.

Because the helper itself performs no sample-rate scaling, any time interpretation would have to be encoded by the selected divisor or by its caller.

## Cursor-role reinforcement

The helper directly depends on `0x802FD720`, which reads SND `+0x38` and `+0x3A` through:

```text
0x8030A174 -> lhu +0x38
0x8030A198 -> lhu +0x3A
```

This independently reinforces the prior result that the meaningful backlog quantity is the modular distance between software commit and hardware playback/consumption progress.

## Empty-state clue

At `queued == 0`, the normalized helper immediately returns zero and performs no special recovery operation.

Therefore empty-queue recovery is **not implemented in this query helper**. Any stop/fade/restart behavior must live in:

- the lower transfer/ISR/state-machine path;
- SND hardware itself;
- or the higher-level caller reacting to zero.

This narrows the underrun search.

## Next target

Trace writes/updates around the lower state fields `+0x62/+0x64/+0x66/+0xDA` and the transfer/interrupt path around `0x803016xx`.

That region both manipulates these fields and is a better candidate for the actual lower-buffer completion/empty transition than `0x802FD790`.

## Hardware gate

Not reached.
