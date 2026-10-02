# run_emulator audio re-entry has an explicit 40-ms scheduler quarantine

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **BIN — DELAY/ORDERING CLOSED**

## Discovery

The runtime audio/state re-entry path in `run_emulator @ 0x8035ED48` contains a second explicit timing barrier beyond the 10-ms lower-hardware delay inside sound configuration.

Around `0x8035F03C`:

```text
0x8035F03C  os_get_tick_count()
0x8035F048  scheduler_start_tick = now
0x8035F04C  dly_tsk(40)
0x8035F054  os_get_tick_count()
...
0x8035F074  compare elapsed with current frame period
```

The stock timer archaeology closes `dly_tsk` arguments as milliseconds.

Therefore this path deliberately requests a:

> **40-ms delay after resetting the scheduler timing origin.** [BIN]

## Relationship to the family-8 sound reinit

Immediately before this region, the state machine tests the current family/state value.

The family-8 path reaches:

```text
0x8035F0C0  a0 = 0
0x8035F0C4  sound_init @ 0x8035C998
0x8035F0C8  a2 = 2
0x8035F0CC  branch back to 0x8035F03C
```

Thus after the runtime sound reinitialization path returns to the common re-entry region, the scheduler timing origin is refreshed and the frontend enters the explicit 40-ms wait/quarantine behavior.

The exact state-variable mutation performed inside sound init determines whether family/state 8 immediately re-enters that branch again; this note does not infer an infinite loop from the static branch because the called initializer can mutate shared state.

## Audio significance

There are now three distinct transition-time mechanisms that must not be conflated:

1. **10-ms lower-hardware reconfiguration delay** inside active sound configuration;
2. **frontend FIFO reset** requiring fresh source PCM to reach 576 frames;
3. **40-ms run_emulator scheduler/re-entry delay** in the common state-reentry path.

The 40-ms delay is not normal steady-state audio latency.

It is transition behavior.

## L23 significance

No corresponding L23 close/open pair surrounds this runtime re-entry sequence.

Initial startup still has the stronger analog ordering:

```text
sound initialization
 -> timing setup
 -> L23 open
```

whereas runtime state re-entry can perform substantial sound/timing work with the speaker gate already open.

This further strengthens the transition-noise lane without proving an audible pop.

## Important non-additivity warning

Do **not** simply calculate:

```text
10 ms + 40 ms + frontend refill
```

and call the result speaker silence.

The 10-ms delay is nested inside sound initialization, while the 40-ms wait belongs to the run-emulator re-entry state machine, and physical DAC output during both remains dependent on lower hardware state/fade behavior.

These are proven software delays, not yet a measured end-to-end silence interval.

## Latency-model consequence

Steady-state latency estimates should exclude this 40-ms transition quarantine.

Pause/menu/reinit testing should include it because it can dominate the subjective delay before gameplay/audio resumes.

## Evidence boundary

- `dly_tsk(40)` request: **BIN**
- millisecond timer domain: **BIN**
- scheduler tick reset before wait: **BIN**
- exact physical speaker waveform during wait: **OPEN**
- exact user-visible transition in every state-machine entry: **OPEN pending state semantics**

## Hardware gate

Not reached.
