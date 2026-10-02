# Runtime reinit device controls route through object +0x68, not +0xCC

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **BIN CORRECTION**

## Correction

The previous runtime-reinit checkpoint correctly identified the generic device-control wrapper at:

`0x80279F0C`

but the next-step wording treated the object's `+0xCC` callback as the dispatcher to resolve for the observed reinit commands.

Direct decode of `0x80279F0C` shows that is not correct for these command values.

## Wrapper dispatch logic [BIN]

The wrapper loads both potential callbacks:

- object `+0xCC`;
- object `+0x68`.

For command numbers in a selected subrange beginning at 25, it computes a bit from:

```text
1 << (command - 25)
```

and tests that bit against mask:

```text
0xE007
```

Only commands selected by that range/mask are dispatched through `+0xCC`.

Otherwise the wrapper falls back to object `+0x68`.

## Reinit commands

The runtime sound initializer uses:

```text
0x5D
0x4D
0x4C
0x36
0x59
```

All are outside the `25..40` range tested by the `+0xCC` selection logic.

Therefore all five observed reinit controls route through:

> **object callback +0x68**

not +0xCC. [BIN]

## Why this matters

The correct reverse-engineering path for the runtime reinit sequence is now:

```text
sound_init 0x8035C998
       ↓
generic control wrapper 0x80279F0C
       ↓
active sound object's +0x68 callback
       ↓
legacy command decode for 5D/4D/4C/36/59
       ↓
lower SND operations
```

Following +0xCC would analyze the wrong command family and could produce false DROP/START/DRAIN labels.

## Evidence discipline

The semantic names of `0x5D/0x4D/0x4C/0x36/0x59` remain OPEN.

Modern HCRTOS ioctl names must still not be assigned by numeric analogy.

## Next target

Resolve the concrete active sound object's `+0x68` function pointer from its registration/constructor path, then decode those five cases.

## Hardware gate

Not reached.
