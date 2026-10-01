# XGO sound reinitialization can occur without L23 muting

Date: 2026-10-01  
Branch: `research-audio-fidelity-latency`  
Status: **DIRECT STOCK BIN — NOISE-LANE LEAD**

## Startup ordering [BIN]

Inside stock `run_emulator @ 0x8035ED48`, the normal initial audio path performs:

```text
0x8035EE54  call sound init 0x8035C998
...
0x8035EEA0  os_get_tick_count
...
0x8035EEA8  a0 = 0
0x8035EEB0  gpio_L23(0)
```

Given the established L23 polarity:

```text
L23=1 mute/gate closed
L23=0 audio enabled
```

the initial game path initializes the sound subsystem before opening the board audio gate. This is a sensible anti-pop ordering.

## Reinitialization path [BIN]

A later path inside the same run loop reaches:

```text
0x8035F0C0  a0 = 0
0x8035F0C4  call sound init 0x8035C998
0x8035F0C8  a2 = 2
```

There is no L23 call immediately before or after this sound reinitialization.

Direct enumeration of every JAL to `gpio_L23 @ 0x801B4024` confirms that no call exists in the `0x8035F0xx` reinitialization region.

Therefore stock firmware can re-enter/reconfigure its sound initialization while the external L23 audio gate remains in its previous state — normally unmuted during gameplay. [BIN]

## Why this matters

This is a concrete **noise/pop improvement lead**.

Initial startup uses:

```text
sound configure
 -> open amplifier/audio gate
```

but at least one runtime reinitialization path does not bracket the same operation with:

```text
mute
 -> reconfigure/reset sound
 -> settle/re-prime
 -> unmute
```

If SND/DAC configuration creates a transient, stale sample, zero crossing discontinuity, or underrun during reinitialization, the internal amplifier can expose it.

This does **not** prove that a user-audible pop occurs at this exact path. It proves only that the hardware gate is not used to hide the reconfiguration.

## Relationship to pause/menu archaeology

Previous scheduler archaeology already identified this region as part of audio/timing re-entry behavior: timing state is refreshed around pause/menu/audio reinitialization so menu time is not counted as gameplay lateness.

The new result adds the audio-gate dimension:

```text
runtime audio re-entry
 -> sound init occurs
 -> scheduler/timing state is handled
 -> L23 is not locally muted around the reinit
```

Exact queue contents before/after the reinit remain to be traced.

## Safe future experiment shape

If this path is later shown to correlate with an audible transient, a controlled noise-only candidate could test:

```text
L23 = 1
sound reinit
wait only for a proven safe/primed condition
L23 = 0
```

Do not invent an arbitrary millisecond delay. Prefer an actual SND-ready/queue-primed condition recovered from the binary.

Do not combine this with resampler, latency, or mono-fold changes.

## Interaction with external AV

Because LCD/TV switching does not manipulate L23, L23 likely gates a board-specific analog destination rather than the entire software PCM transport.

That makes L23 particularly attractive for internal-speaker transient suppression, but the exact electrical destination remains OPEN.

## Next offline target

Trace the reinitialization path's queue state:

- whether frontend producer/consumer offsets are reset;
- whether lower SND commit/playback cursors are reset;
- whether a first 576-frame block is required before playback resumes;
- what SND underrun-fade does during the gap.

This can tell us whether the stock re-entry can expose stale/empty DAC output and what condition should precede unmute.

## Hardware gate

Not reached.
