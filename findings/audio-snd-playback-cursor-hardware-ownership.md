# SND playback cursor +0x3A is hardware-owned and must clamp/rebase at empty

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **BIN OWNERSHIP CLOSED; EMPTY CLAMP IS STRONGLY CONSTRAINED INF**

## Cursor ownership closure

The primary lower-SND cursor helpers are asymmetric.

### Commit cursor +0x38

`0x8030A130` is a setter:

```text
lhu old,+0x38
sh  new,+0x38
```

Stock software writes this cursor directly, including writing zero during runtime sound reconfiguration.

### Playback cursor +0x3A

`0x8030A198` is a getter.

Direct call sites recovered in the active sound stack include:

```text
0x802FD748   queued-distance calculation
0x80302FD8   lower service/availability calculation
0x803093FC   legacy command/query case
```

No parallel low-level setter for primary `+0x3A` exists in the recovered active SND helper set.

The lower service path reads `+0x3A` into private state but does not write the hardware cursor back.

This strengthens the classification:

> SND +0x3A is hardware-owned playback/consumption progress. [BIN]

## Lower service readback [BIN]

The service path around `0x80302FD8` performs:

```text
playback3A = snd_get_playback_cursor()
private +0x44 = playback3A

private_commit = private +0x46
hardware_commit38 = snd_get_commit_cursor()

wait/recheck relationship

distance = (private_commit - playback3A) mod private_wrap
private +0x82 = distance
```

So the lower service layer observes the same producer-versus-hardware-consumer relationship already used by readiness.

## Runtime reset constraint

Runtime reinit writes:

```text
private +0x46 = 0
SND +0x38 = 0
```

but does not software-write `+0x3A`.

If hardware left `+0x3A` at an arbitrary old nonzero position, then the next queue-distance query would produce:

```text
(0 - old_playback) mod 8208
```

which is generally a very large apparent backlog and would fail the `queued < 482` admission test.

The recovered runtime path contains no software cursor repair between reset and normal readiness/submission.

Therefore the lower hardware reconfiguration necessarily resets/rebases playback progress into a relation compatible with the new commit cursor.

The exact register transition is hardware-owned and not directly visible as a software store.

## Normal empty constraint

The same argument applies during ordinary playback.

If `+0x3A` freely advanced past `+0x38` at empty:

```text
commit = N
playback = N+1
queued = 8207
```

The producer would immediately see a nearly-full queue and stop submitting.

Because there is no software writeback path repairing `+0x3A`, normal ALSA-mode operation must prevent that state from persisting.

The strongest architecture supported by the binary is therefore:

```text
+0x3A advances while committed PCM exists
+0x3A reaches +0x38 at empty
hardware stops/clamps/rebases playback progress
later commit advancement makes new PCM consumable
```

Whether the physical DAC outputs zero, holds/fades the last sample, or follows another underrun behavior while the cursor is clamped remains OPEN.

## Why this strengthens the SNES empty-gap model

The fixed-183 SNES path has a proven long-term PCM deficit.

The queue contract now strongly excludes a model where the hardware simply continues advancing through nonexistent PCM.

Therefore the deficit must be absorbed by periods in which real PCM consumption/progress is not occurring, or by an equivalent hardware empty-state transition.

Under immediate clamp/resume semantics, the exact deterministic model yields the previously derived nine short empty intervals per 3.2-s phase cycle.

The remaining uncertainty is principally **what the DAC emits during those intervals**, not whether software can magically account for the missing frames.

## Underrun-fade boundary

The stock firmware enables SND underrun fade.

Given hardware ownership of +0x3A, the fade behavior is increasingly likely to be implemented below the software queue layer.

No software routine in the recovered readiness/service path synthesizes replacement PCM at empty.

Thus any smoothing of the missing SNES PCM must occur in SND hardware/low-level behavior rather than by frontend sample generation.

## Evidence levels

- +0x38 software setter: **BIN**
- +0x3A getter/readback role: **BIN**
- no active software repair/writeback path found for +0x3A: **BIN search result**
- hardware must maintain a recoverable commit/playback relation: **INF strongly constrained by BIN**
- exact DAC empty waveform: **OPEN**

## Hardware gate

Not reached.
