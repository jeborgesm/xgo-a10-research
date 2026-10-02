# Lower SND transfer-service state machine around 0x80301618

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **BIN STRUCTURAL RECOVERY; EVENT NAMES OPEN**

## Why this region matters

The normalized queued-depth helper at `0x802FD790` is read-only and cannot implement empty recovery.

A direct caller scan identifies `0x80301618` as a substantial lower-SND service/state-machine function. It is called from `0x80302F64` with the active sound object and its return value controls the surrounding service loop.

This is a better candidate for lower transport completion/state transitions.

## Direct call boundary [BIN]

```text
0x80302F64  jal 0x80301618
            a0 = active sound object
0x80302F6C  branch on returned v0
```

The function spans approximately:

```text
0x80301618 .. 0x803019BC
```

and returns `v0=1` on the recovered normal tail.

## Lower cursor/state fields [BIN]

The function directly reads and compares multiple halfword cursor/state fields including:

```text
+0x62
+0x64
+0x66
+0x68
+0x6A
+0x6C
+0x6E
+0x70
+0x72
```

and updates state including:

```text
+0xDA
+0xE0
```

This is the same `+0x62/+0x64/+0x66/+0xDA` family used by the queued-distance normalization helper `0x802FD790`.

Therefore `0x80301618` participates in the lower ring/fragment service machinery rather than being an unrelated control function.

## Blocking/synchronization behavior [BIN]

The state machine contains calls to the stock delay/synchronization primitive at `0x800030D4` when cursor relationships do not yet satisfy its required condition.

This reinforces that these fields represent live producer/consumer/fragment state whose ordering must be synchronized.

## +0xDA provenance [BIN]

Within this state machine, `+0xDA` is written from a 16-bit value selected from the active lower object's table/state:

```text
... select active cursor/entry
lhu selected_value
...
sh selected_value,+0xDA(object)
```

That explains why `0x802FD790` can later use `+0xDA` as a divisor for its normalized queued-depth result.

Thus `+0xDA` is not an arbitrary time constant injected by the query helper; it is maintained by the lower transfer state machine.

Its exact semantic name remains OPEN.

## Periodic higher-level callback [BIN]

The tail maintains a GP-global counter at `GP+0x9C68`.

When active, the counter increments until a threshold of `0x33` (51). Under an additional object-state condition (`+0x15D == 1`) the path can invoke an object callback stored at `+0x17C`, then resets the counter.

This proves the lower service machinery contains a periodic higher-level notification/action path in addition to raw cursor advancement.

The event's symbolic purpose is not yet proven and must not be labeled underrun/fade without further xref/context evidence.

## What this does NOT yet close

The current decode does not yet prove:

- which of +0x62/+0x64/+0x66 are DMA fragment producer/read/end positions;
- the exact event that invokes `0x80301618`;
- whether queue-empty causes DMA stop;
- whether +0x3A freezes, wraps or advances at empty;
- whether the 51-count callback is underrun-related;
- whether hardware underrun fade is entered here or autonomously by SND.

## Family-source limitation [UP]

The maintained HCRTOS public API exposes an explicit `SND_EVENT_UNDERRUN` and the sound platform abstraction exposes DMA/ring state.

However, the public family tree does not surface enough of the exact older XGO lower-driver implementation to map this binary state machine's field offsets or event numbers directly.

This is useful negative evidence: do not rename the XGO fields from modern HCRTOS structs by offset analogy.

## Next binary route

Continue from the caller around `0x80302Exx..0x80302Fxx` and identify the event source/flags that lead into `0x80301618`.

Then correlate:

```text
event source
 -> lower state-machine cursor update
 -> SND +0x38/+0x3A movement
 -> empty condition
 -> underrun-fade bit behavior
```

## Hardware gate

Not reached.
