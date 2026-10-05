# RP2040 XGO responder — implementation contract v1

Status: protocol-side implementation specification. Physical connector assignment and voltage levels remain OPEN.

## Exact XGO serial transaction

Firmware-confirmed XGO GPIO roles:

```text
B15 = DATA stream 0
L0  = DATA stream 1
B7  = shared CLOCK
```

Idle:

```text
DATA streams: inputs
CLOCK: output HIGH
```

Load/reset:

```text
1. XGO changes both DATA GPIOs to outputs.
2. XGO drives both DATA lines LOW.
3. XGO waits approximately 4 us.
4. XGO changes both DATA GPIOs back to inputs.
5. XGO immediately samples serial position 0.
```

Clock progression:

```text
sample current DATA
CLOCK LOW
wait approximately 2 us
CLOCK HIGH
sample next DATA
...
12 positions total
```

The accessory therefore behaves as a host-loaded active-low serial source. It does not initiate packets.

## Exact serialization order

```text
serial position  button
0                R
1                Y
2                X
3                L
4                A
5                B
6                SELECT
7                START
8                UP
9                DOWN
10               LEFT
11               RIGHT
```

Raw XGO masks reconstructed from firmware:

```text
R       0x1000
Y       0x2000
X       0x4000
L       0x0800
A       0x0080
B       0x0040
SELECT  0x0020
START   0x0010
UP      0x0008
DOWN    0x0004
LEFT    0x0002
RIGHT   0x0001
```

The serialization positions, not numeric raw-mask bit order, are the responder's wire-order contract.

## Family timing comparator

Modern UniFrog's hardened SF2000 implementation uses the homologous protocol with conservative explicit delays:

```text
load low     4 us
input settle 4 us
clock low    3 us
clock high   3 us
```

Stock XGO statically shows approximately 4 us load low and approximately 2 us explicit clock-low delay; no separate first-bit settle delay has been identified.

The responder should react to observed edges/state rather than reproduce host delays internally wherever possible.

## RP2040 v1 architecture

The simplest useful firmware is:

```text
physical arcade inputs
       |
       v
normalized GP2040-style state
       |
       v
12-position XGO state snapshot
       |
       v
PIO/IRQ serial responder
       |
       v
P2 DATA
```

The protocol engine needs only:

- current 12-button snapshot;
- detection of the host load/reset condition;
- position reset to 0;
- active-low presentation of the current serial position;
- advance on the XGO clock edge;
- release/high state for unpressed buttons.

No USB output, USB host, Bluetooth or commercial-controller translation is required for v1.

## Important electrical behavior

XGO itself temporarily drives the DATA line LOW during load/reset. Therefore the RP2040 must **not** behave as a permanent push-pull high/low driver on the shared DATA conductor.

The eventual interface should emulate a controller that can safely coexist with the XGO host-driven-low phase. An open-drain/open-collector-style sink/release model is the preferred starting architecture, subject to confirmation of the actual family controller electrical circuit and voltage.

Conceptually:

```text
button pressed   -> responder pulls DATA low
button released  -> responder releases DATA
load/reset       -> XGO is allowed to pull DATA low without contention
```

Do not implement the physical driver until the connector voltage/pull network is closed.

## Physical connector state

Strongest current model:

```text
micro-B D- / D+ -> DATA / CLOCK, order OPEN
GND             -> reference
VBUS            -> controller supply/reference, voltage OPEN
ID              -> secondary detect/load/bias/coupling role
```

Evidence supporting D-/D+ as the transport pair:

- X60 wired controller works as SF2000 Player 2 through an ordinary-looking passive Type-C/micro-B adapter.
- Such passive USB2 adapter paths carry VBUS, D-, D+ and GND; micro-B ID is not an ordinary cross-connector data conductor.
- SF2000 community evidence says ordinary USB wired gamepads do not work and compatible family controllers use proprietary polling.
- X60 controller-facing connector was independently observed at roughly 3 V.
- XGO's generic USB/GP2040 test failed while its firmware exposes the matching proprietary scanner.

This is still inference, not permission to wire an RP2040 directly.

## First hardware milestone once pinout is closed

Use a known two-player title and map only:

```text
UP DOWN LEFT RIGHT
A B
START SELECT
```

Leave L/R/X/Y released initially if desired.

Success criterion:

- XGO built-in P1 remains functional;
- external RP2040 actions appear only on P2;
- no phantom R or other button;
- no control freeze when adapter is inserted;
- P2 remains stable during sustained gameplay.

After that, add the remaining four face/shoulder positions and GP2040 mapping.
