# Stock dly_tsk(1) uses the millisecond timer domain

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **BIN + MIPS TIMER ARCHITECTURE — 1-MS REQUEST QUANTUM CLOSED**

## Why this matters

The frontend producer, frontend consumer, and lower-SND readiness loops all use:

```text
dly_tsk(1)
```

when blocked.

Earlier audio notes correctly refused to invent a large DMA-period delay, but left the RTOS/timer duration of this retry OPEN.

The stock timer implementation now closes the requested delay unit.

## os_get_tick_count [BIN]

`os_get_tick_count @ 0x8030FEC8` simply returns the global tick counter at:

```text
GP-0x0FA4
```

The stock scheduler uses this counter directly with integer frame periods expressed as:

```text
PAL: 20
NTSC: 17,17,16
```

which independently identifies this timer domain as milliseconds.

## Tick-source implementation [BIN]

Timer initialization around `0x80310470`:

1. reads the platform clock value;
2. constructs a frequency value equal to that clock in Hz;
3. divides it by 2000;
4. stores that divisor for the CP0 timer accounting path.

The live update path around `0x803104F8` reads:

```text
0x80049FC8
```

which is the MIPS:

```text
mfc0 v0,$9
```

CP0 Count register.

The elapsed Count delta is divided by the stored clock/2000 divisor and accumulated into the tick global returned by `os_get_tick_count`.

On the MIPS timer architecture used here, CP0 Count advances at half the processor clock, so:

```text
(CPU/2 counts per second) / (CPU/2000)
= 1000 timer units per second
```

or:

```text
1 timer unit = 1 ms
```

This matches the independently recovered 17/17/16-ms scheduler contract.

## dly_tsk path [BIN]

`dly_tsk @ 0x8030F480` forwards its argument directly into the stock timer/sleep registration path:

```text
dly_tsk(delay)
 -> 0x8030F9EC(delay, callback)
 -> timer queue
 -> block current task
```

There is no multiplication by a larger audio period in `dly_tsk`.

Therefore:

> `dly_tsk(1)` requests a delay in the stock **1-ms timer domain**.

Actual task wakeup can of course occur later because of scheduling/interrupt latency; this finding closes the requested timer quantum, not a hard real-time upper bound.

## Audio implications

### Lower readiness polling

The lower admission path:

```text
read playback +0x3A
compute queued distance
if not ready:
    dly_tsk(1)
    retry
```

therefore polls on approximately millisecond request granularity.

There is still no evidence for an assumed 960-frame or DMA-period software wait.

### Frontend producer/consumer blocking

The same applies to:

- producer waiting for frontend ring space;
- consumer waiting for >=576 source frames;
- sound-task shutdown waits.

Their retry primitive is a 1-ms requested sleep, not a full audio block delay.

## Correction to prior OPEN list

The following item can now be removed from the audio OPEN list:

```text
RTOS tick/dly_tsk(1) duration
```

The still-OPEN timing details are narrower:

- physical +0x3A advancement granularity;
- interrupt/completion granularity;
- scheduler wakeup jitter beyond the requested 1 ms;
- exact DAC empty/fade behavior.

## Latency-model consequence

Future lower-queue latency bounds may include a roughly one-millisecond **polling request quantum** where relevant.

Do not convert that into a guaranteed <=1-ms response bound; task scheduling can add delay.

## Hardware gate

Not reached.
