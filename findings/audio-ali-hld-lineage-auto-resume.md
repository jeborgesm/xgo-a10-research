# XGO sound API is an ALi HLD lineage; command 0x36 is SND_AUTO_RESUME

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **SRC/UP + BIN CORRESPONDENCE — COMMAND 0x36 CLOSED**

## Public legacy source match

Public ALi HLD sound headers from the 3202C/PDK lineage expose the same high-level API shape retained in XGO:

```c
snd_data_enough(struct snd_device *)
snd_config(struct snd_device *, UINT32 sample_rate,
           UINT16 sample_num, UINT8 precision)
snd_write_pcm_data(...)
snd_start(...)
snd_stop(...)
snd_io_control(...)
```

This is a much closer architectural match to the XGO binary than modern generic ALSA terminology alone.

The public command base is:

```c
#define SND_IO 0x0000000F
```

and includes:

```c
#define IS_SND_RUNNING   (SND_IO + 1)   // 0x10
#define IS_PCM_EMPTY     (SND_IO + 6)   // 0x15
...
#define SND_AUTO_RESUME  (SND_IO + 39)  // 0x36
```

Later ALi headers document `SND_AUTO_RESUME` as:

> Enable sound device auto resume function when error occurs.

## Exact XGO command-table validation [BIN]

The XGO legacy dispatcher `0x80309370` subtracts 0x10 and uses a jump table.

### Command 0x10

Target:

```text
0x803093BC
```

It reads the sound-device state at object +0x18, compares it with 4, and returns zero when the state is 4.

The public ALi header defines:

```text
SND_STATE_PLAY = 4
IS_SND_RUNNING = 0x10
```

This is an exact semantic match using the ALi convention where `RET_SUCCESS == 0`.

### Command 0x15

Target:

```text
0x803093FC
```

It reads:

```text
SND +0x3A playback cursor
SND +0x38 commit cursor
```

XORs them and returns zero when they are equal.

The public ALi command at 0x15 is:

```text
IS_PCM_EMPTY
```

Again, zero/RET_SUCCESS when the cursors are equal is an exact semantic match.

These two independent cases strongly validate the command-number lineage rather than relying on a coincidental numeric overlap.

## Command 0x36 closure

The XGO command used by `sound_init`:

```text
0x36(0)
```

dispatches to:

```text
0x80309834
 -> private +0x15D = arg
```

Because 0x36 is exactly `SND_AUTO_RESUME` in the validated ALi HLD command map:

> **XGO sound_init explicitly disables SND_AUTO_RESUME.** [BIN+SRC]

The object's default initialization earlier sets +0x15D to 1, so the emulator sound-init path actively changes it from enabled to disabled.

## What auto-resume controls in XGO [BIN]

The lower monitoring/service function beginning around `0x802FDAEC` maintains four byte counters.

When any monitored counter reaches 101, the code checks private `+0x15D`.

If +0x15D == 1, it can:

- invoke the registered private +0x17C callback when present;
- signal the associated lower event path;
- clear the monitor counters.

If +0x15D != 1, it skips that callback/event recovery path and clears the counters.

Thus the public “auto resume when error occurs” description is consistent with the exact XGO binary behavior.

## Gameplay significance

This is directly relevant to sustained CPS1 audio.

Stock emulator initialization deliberately disables an available lower-driver error-recovery mechanism.

That does **not** mean turning it on is automatically correct:

- the emulator path may disable it intentionally because ALSA mode supplies a different recovery contract;
- enabling it could restart/drop/rebase audio in a way that increases audible discontinuities;
- the exact four monitored error conditions are not all named yet.

Therefore `SND_AUTO_RESUME(1)` should **not** be bundled into the first native-22050 candidate.

But it becomes a high-value isolated experiment if heavy CPS1 games still exhibit audio stalls/choppiness after rate-path cleanup.

## New diagnostic opportunity

Because command 0x15 is now closed as `IS_PCM_EMPTY`, XGO already exposes a software-visible exact empty-state query through the legacy sound object.

That can potentially be used in a later diagnostic build to count real lower-buffer empty events during gameplay rather than inferring them from sound quality.

Such instrumentation would be far more useful for CPS1 tuning than transition-pop analysis.

## Evidence boundary

- ALi public HLD API/command map: **SRC/UP**
- XGO 0x10 running-state behavior: **BIN**
- XGO 0x15 cursor-equality empty behavior: **BIN**
- XGO 0x36 writes +0x15D: **BIN**
- 0x36 = SND_AUTO_RESUME: **SRC+BIN correspondence, closed**
- exact meaning of each of four 101-count monitor conditions: **OPEN**

## Hardware gate

No candidate built yet.
