# XGO controller GPIO streams to libretro Player 1 / Player 2 ports

Status: **end-to-end physical-stream ordering confirmed from scanner through libretro callback**.

## Headline

The two serialized controller DATA lines are now mapped unambiguously to libretro controller ports:

```text
GPIO B15 -> controller slot 0 -> libretro port 0 / Player 1
GPIO L0  -> controller slot 1 -> libretro port 1 / Player 2
```

This removes one of the main ambiguities in the Handle Interface investigation. The XGO firmware does not merely maintain two anonymous serial streams: the second stream, sampled from GPIO L0, is the source that ultimately feeds Player 2.

## Physical scanner inputs

The controller scanner at `0x8035d770` uses:

```text
DATA0 = GPIO B15
  input register 0xb8800350
  sampled through bit 0x8000

DATA1 = GPIO L0
  input register 0xb8800050
  sampled through bit 0x0001

CLOCK = GPIO B7
  output register 0xb8800354
  clock bit 0x0080
```

Both DATA lines are sampled active-low in parallel for the same 12 serialized positions.

The scanner stores the two raw button words as a contiguous two-word array:

```text
gp = 0x80c34774

gp - 0xd2c = 0x80c33a48   raw slot 0 / B15
gp - 0xd28 = 0x80c33a4c   raw slot 1 / L0
```

Every serialized button position follows the same ordering. For example, first position `R`:

```text
B15 low -> OR 0x1000 into gp-0xd2c
L0  low -> OR 0x1000 into gp-0xd28
```

and the same pairwise pattern continues for `Y`, `X`, `L`, `A`, `B`, `SELECT`, `START`, `UP`, `DOWN`, `LEFT`, and `RIGHT`.

## Normalization preserves stream index

The controller task begins its two-player normalization loop around `0x8035d520`.

Relevant setup:

```text
0x8035d4fc  addiu $21,$gp,-0xd2c   # base of raw two-word array
0x8035d508  addiu $fp,$gp,-0xd18   # base of normalized two-word array
```

The loop index is `0..1`:

```text
offset = player_index * 4
raw    = *(gp - 0xd2c + offset)
...
normalized destination = gp - 0xd18 + offset
```

Therefore the physical order is preserved:

```text
normalized[0] <- B15 raw stream
normalized[1] <- L0 raw stream
```

The normalized globals are:

```text
gp - 0xd18 = 0x80c33a5c   normalized slot 0 / B15
gp - 0xd14 = 0x80c33a60   normalized slot 1 / L0
```

## Snapshot stage preserves the same order

Function `0x8035e360` performs a direct two-word copy:

```text
lw $2, -0xd18($gp)
lw $3, -0xd14($gp)
sw $2, -0xd34($gp)
sw $3, -0xd30($gp)
```

Thus:

```text
gp - 0xd34 = 0x80c33a40   slot 0 / B15
gp - 0xd30 = 0x80c33a44   slot 1 / L0
```

Again, no swapping or merging occurs.

## Keymap/mapping stage preserves player index

The mapping stage beginning at approximately `0x8035ea38` sets:

```text
source base      = gp - 0xd34
final state base = gp - 0xcb0
```

and loops with `player_index = 0..1`:

```text
offset = player_index * 4
final[player_index] = source[player_index]
```

It then applies the compiled six-button mapping/turbo tables for that same player index.

So the final mapped input words are:

```text
gp - 0xcb0 = 0x80c33ac4   final mapped slot 0 / B15
gp - 0xcac = 0x80c33ac8   final mapped slot 1 / L0
```

## Libretro callback proves port numbers

`retro_input_state_cb` is at:

```text
0x8035eb20
```

It computes:

```text
state_ptr = (gp - 0xcb0) + port * 4
```

and explicitly rejects ports >= 2.

Therefore:

```text
libretro port 0 -> gp-0xcb0 -> B15
libretro port 1 -> gp-0xcac -> L0
```

This gives the complete chain:

```text
GPIO B15
  -> raw[0]
  -> normalized[0]
  -> snapshot[0]
  -> mapped[0]
  -> libretro port 0

GPIO L0
  -> raw[1]
  -> normalized[1]
  -> snapshot[1]
  -> mapped[1]
  -> libretro port 1
```

## What is now confirmed

### CONFIRMED

- B15 is the physical DATA stream used for Player 1 / libretro port 0.
- L0 is the physical DATA stream used for Player 2 / libretro port 1.
- both streams use the same 12-position SF2000 logical serialization order;
- the firmware preserves the streams independently through every input-processing stage;
- Player 2 is not synthesized, mirrored, or ORed with Player 1 in the normal runtime path.

## Remaining electrical question

This result identifies the SoC GPIO for Player 2, but it does **not yet by itself prove which micro-USB contact carries L0**.

The highest-value remaining Handle Interface task is now much narrower:

```text
Find which micro-USB contact reaches GPIO L0.
Find which contact reaches shared CLOCK B7.
Determine what the ID contact does to detect/load/gating.
```

Once L0 and B7 are mapped at the connector, the external controller interface is essentially specified at the signal level.
