# Runtime audio reconfiguration includes an explicit 10-ms lower-reset delay

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **BIN — DELAY REQUEST CLOSED**

## Major transition-noise finding

The active sound configuration callback:

```text
object +0x60 = 0x80306CDC
```

contains an explicit lower-hardware reconfiguration delay.

In the normal configuration path, when private guard/state `+0x15C` is clear, the function:

```text
sets private +0x15C = 1
calls 0x80306218
calls dly_tsk(10)
clears private +0x15C
continues configuration
```

Exact sequence:

```text
0x80306D2C  private +0x15C = 1
0x80306D30  jal 0x80306218
0x80306D38  jal dly_tsk
0x80306D3C  a0 = 10
0x80306D40  private +0x15C = 0
```

The timer archaeology independently closes `dly_tsk` arguments as the stock millisecond timer domain.

Therefore this is an explicit:

> **10-ms requested delay during sound hardware reconfiguration.** [BIN]

Actual wakeup may be later due to scheduling, but not earlier by design.

## What 0x80306218 does before the delay

The lower configuration routine performs substantial SND reprogramming.

Among the already-recovered effects in this path:

- primary/secondary/tertiary commit cursors are programmed to zero;
- SND rate/format/clock state is reconfigured;
- underrun fade is enabled;
- initial hardware volume/configuration state is applied;
- additional SND control fields are reset/programmed.

Thus the 10-ms sleep occurs **after entering lower hardware reconfiguration**, not as an unrelated frontend delay.

## Runtime L23 consequence

Initial game startup is protected by ordering:

```text
sound initialization/reconfiguration
 -> lower reset/config delay
 -> later L23(0) opens speaker
```

The runtime reinit path does not close L23 around the equivalent sound-init call.

Therefore runtime reinit can execute:

```text
L23 remains open
 -> lower SND reset/reconfiguration
 -> explicit dly_tsk(10)
 -> remaining lower setup/start
 -> frontend FIFO reset
 -> wait for >=576 fresh source frames
```

This materially strengthens the transition discontinuity finding.

The lower path is not merely reset “instantaneously” while the speaker remains open; stock software deliberately waits at least a requested 10 ms during that reconfiguration.

## SNES transition scale

After sound-init later resets the frontend FIFO, stock SNES still requires four fresh 183-frame callbacks before the first 576-frame frontend transfer can occur.

The 10-ms hardware reconfiguration delay and the post-reset frontend refill are separate phases.

Do not simply add 10 ms to four full frame periods and call that measured silence, because exact alignment with the emulator loop and DAC empty/fade state is not yet pinned.

But the transition now has two independently proven delay sources:

1. **10-ms requested lower-hardware reconfiguration wait**;
2. **576-source-frame frontend refill requirement**.

## FBA transition scale

FBA similarly restarts from an empty frontend FIFO:

```text
367
734 -> first 576-frame transfer possible
```

so fresh FBA lower PCM can become available on the second normal post-reset audio callback.

Again, exact wall-clock DAC silence depends on loop phase and hardware empty behavior.

## Noise-lane implication

A future L23-gated reinit experiment now has a much stronger rationale.

The eventual unmute condition should not be a guessed replacement for the existing 10-ms wait.

The preferred evidence-based shape remains:

```text
mute L23
 -> perform stock reconfiguration including its 10-ms wait
 -> rebuild/submit fresh PCM
 -> detect proven ready/primed condition
 -> unmute
```

The ready/primed condition still needs recovery before a hardware candidate is justified.

## Evidence boundary

Proven:

- exact `dly_tsk(10)` call;
- 1-ms timer domain;
- lower reconfiguration occurs before it;
- runtime reinit can occur with L23 open.

Still OPEN:

- DAC output during the 10-ms wait;
- exact +0x3A transition during reset;
- underrun-fade waveform;
- best post-refill condition for safe L23 reopen.

## Hardware gate

Not reached.
