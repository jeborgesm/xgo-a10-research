# Runtime sound reinit performs device-control sequence before FIFO reset

Date: 2026-10-01  
Branch: `research-audio-fidelity-latency`  
Status: **DIRECT STOCK BIN + FAMILY ABI CROSSCHECK; COMMAND NAMES PARTLY OPEN**

## Scope

Continue the runtime re-entry trace through `sound_init @ 0x8035C998`.

The upper FIFO reset is already closed. This pass asks whether the initializer merely resets software pointers or also touches the underlying sound device.

## Result [BIN]

It touches the sound device extensively **before** resetting the frontend ring.

The initializer:

1. obtains/opens the sound-device object through `0x8027796C`;
2. invokes the object's setup callback through `0x8027A0AC`;
3. issues generic device-control calls through `0x80279F0C`, including command values:
   - `0x5D` with argument 1;
   - `0x4D` with the temporary configuration block;
   - `0x4C` with the same block;
4. invokes another object operation through `0x8027A060`;
5. reapplies the frontend volume through `set_audio_volume @ 0x801B3B40`;
6. issues `0x36` with argument 0;
7. issues `0x59` with argument 1;
8. only afterward reaches the frontend-ring state reset:
   - producer = 0;
   - consumer = 0;
   - capacity = 0x4800;
   - quantum = 0x240.

Therefore the runtime call at `0x8035F0C4` is a genuine device reconfiguration path, not a cosmetic reset of the upper FIFO.

## Family ABI crosscheck [UP]

The maintained HC15xx HCRTOS sound ABI exposes the expected lifecycle operations:

```text
HW_PARAMS
HW_FREE
START
DROP
DELAY
DRAIN
PAUSE
RESUME
XFER
AVAIL_MIN
UNDERRUN
SET/GET_VOLUME
...
```

and its I2SO implementation owns DMA ring state, write/read positions, availability, completion state, volume and underrun-fade configuration.

This makes it architecturally plausible that the XGO device-control sequence above resets or restarts lower transport state.

However, the XGO command numbers `0x5D/0x4D/0x4C/0x36/0x59` belong to its older SDK/device wrapper encoding. They must not be assigned modern HCRTOS ioctl names merely by analogy.

## Noise implication

The already-proven ordering is now:

```text
L23 remains open
       ↓
sound-device setup/control sequence
       ↓
volume reapplied
       ↓
additional device controls
       ↓
frontend FIFO pointers reset to empty
```

Thus the unmuted runtime re-entry exposes not only an upper-FIFO discontinuity but an actual lower sound-device reconfiguration window.

That strengthens the runtime pop/noise hypothesis without claiming an audible symptom before hardware correlation.

## What remains OPEN

For each XGO command above:

- exact legacy SDK symbolic name;
- whether it resets lower commit/playback cursors;
- whether it stops or starts DMA;
- whether it drains, drops or preserves queued lower PCM;
- whether underrun fade remains enabled across it.

## Next offline route

Rather than infer command names from modern headers, resolve the concrete XGO object's `+0xCC` control dispatcher used by `0x80279F0C`, then map these five command values to the lower SND operations they invoke.

That will close whether old lower PCM drains or is dropped during runtime re-entry.

## Hardware gate

Not reached.
