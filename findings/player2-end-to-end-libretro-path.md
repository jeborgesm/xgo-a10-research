# XGO Player 2 End-to-End Input Path

Status: **Player 2 is confirmed to survive the complete stock XGO input path from the second serialized GPIO stream through logical mapping and into the libretro input callback.**

## Major finding

Earlier work proved that the XGO scanner samples two DATA lines in parallel under one shared CLOCK and preserves them as two independent 12-bit controller streams.

A deeper disassembly now proves that the second stream is not stranded after scanning. It is processed symmetrically with Player 1, remapped, copied into the final two-player state array, and consumed by the libretro-facing input callback for `port == 1`.

This materially narrows the Player 2 mystery: **stock XGO software is already two-player capable. The unresolved problem is the physical/accessory path that must drive the second DATA stream correctly.**

## Stage 1: raw scanner produces two independent words

The GPIO scanner beginning at `0x8035d770` clears and fills two GP-relative state words:

```text
$gp = 0x80c34774

gp - 0xd2c = 0x80c33a48   raw serialized controller stream 0
gp - 0xd28 = 0x80c33a4c   raw serialized controller stream 1
```

Each sampled button position is tested independently on both physical inputs:

```text
DATA0 = GPIO B15
DATA1 = GPIO L0
CLOCK = GPIO B7
```

For every active-low sample the same logical button bit is ORed into the corresponding raw word. Examples from the first positions:

```text
R: raw0 |= 0x1000 ; raw1 |= 0x1000
Y: raw0 |= 0x2000 ; raw1 |= 0x2000
X: raw0 |= 0x4000 ; raw1 |= 0x4000
...
```

The complete order remains:

```text
R, Y, X, L, A, B, SELECT, START, UP, DOWN, LEFT, RIGHT
```

## Stage 2: two-player normalization loop

Function `0x8035d4c4` explicitly sets:

```text
raw_base       = gp - 0xd2c
aux_base       = gp - 0xd0c
logical_base   = gp - 0xd18
```

and loops while:

```text
player_index < 2
```

The loop indexes all three bases with `player_index * 4`.

Therefore it processes:

```text
player 0:
  raw      gp-0xd2c
  aux      gp-0xd0c
  logical  gp-0xd18

player 1:
  raw      gp-0xd28
  aux      gp-0xd08
  logical  gp-0xd14
```

The same button translation is applied to both players.

## Stage 3: both logical states copied to final controller array

Function `0x8035e360` performs:

```text
*(gp - 0xd34) = *(gp - 0xd18)
*(gp - 0xd30) = *(gp - 0xd14)
```

Absolute addresses:

```text
0x80c33a40   final player 0 state
0x80c33a44   final player 1 state
```

These two words are adjacent by design.

## Stage 4: keymap compiler also loops across two players

Function `0x8035ea38` takes the final controller array base:

```text
final_state_base = gp - 0xd34
```

and again loops with:

```text
player_index < 2
```

For each player it copies the corresponding final state into a second two-element array beginning at:

```text
gp - 0xcb0
```

then applies the selected six-button/turbo keymap tables.

This is the active mapping path already tied to the 48-byte per-game `.kmp` format. Thus Player 2 participates in the same mapping compiler rather than bypassing it.

## Stage 5: libretro input callback accepts ports 0 and 1

Function `0x8035eb20` has the exact shape expected of the stock libretro `input_state` callback.

Its first argument is treated as the controller port. It computes:

```text
state = *(mapped_state_base + port * 4)
```

and explicitly checks:

```text
port < 2
```

Only ports outside `0..1` return zero.

The function then indexes a logical-button mask table with the requested libretro input ID and returns the matching bit from the selected player's mapped state.

Therefore:

```text
libretro port 0 -> XGO player 1 state
libretro port 1 -> XGO player 2 state
```

This is executable proof that the XGO frontend/core interface exposes two controller ports.

## End-to-end chain

```text
GPIO B15 DATA stream 0 ─┐
                         ├─ scanner 0x8035d770
GPIO L0  DATA stream 1 ─┘       │
                                ▼
                     raw P1 / raw P2
                     0x80c33a48 / 0x80c33a4c
                                │
                                ▼
                     two-player normalizer
                       0x8035d4c4
                                │
                                ▼
                   logical P1 / logical P2
                                │
                                ▼
                        0x8035e360
                                │
                                ▼
                    final two-player array
                   0x80c33a40 / 0x80c33a44
                                │
                                ▼
                    two-player keymap compiler
                       0x8035ea38
                                │
                                ▼
                    mapped two-player array
                                │
                                ▼
               libretro input_state callback
                       0x8035eb20
                     port 0 / port 1
```

## Consequence for the Player 2 mystery

The software question is now substantially answered.

### CONFIRMED

- there are two independent physical serialized input streams;
- both streams use the same 12-button protocol;
- both are normalized by the same two-iteration loop;
- both are copied into adjacent final controller-state words;
- both enter the active keymap compiler;
- the libretro callback accepts exactly two ports and selects the state by `port * 4`;
- therefore stock XGO firmware has a complete software path for Player 2.

### STRONG CONCLUSION

A functioning external controller does not require a firmware feature to "enable Player 2". The primary unresolved requirement is to reproduce the correct electrical/protocol behavior on the physical DATA stream corresponding to the external Handle Interface.

### OPEN

- which of B15 or L0 is the built-in keypad versus the external Handle Interface;
- exact micro-USB contact assignment for CLOCK and external DATA;
- role of the micro-USB ID contact in bias/load/detection;
- whether the intended controller encoder is electrically identical to the X60/DY-family accessory;
- whether all bundled emulator cores actually implement two-player gameplay equally well once libretro port 1 is driven.
