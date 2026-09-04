# Generic XGO libretro runtime — input contract

## Status

The stock XGO input callback is already suitable as the base input abstraction for a generic external libretro runtime.

## Stock callback contract

`retro_input_state_cb @ 0x8035eb20` exposes two independent libretro ports and all 16 standard joypad IDs.

Final mapped controller words:

```text
port 0 / Player 1 = 0x80c33ac4
port 1 / Player 2 = 0x80c33ac8
```

Libretro ID -> XGO final-state mask:

```text
0  B       0x4000
1  Y       0x8000
2  SELECT  0x0001
3  START   0x0008
4  UP      0x0010
5  DOWN    0x0040
6  LEFT    0x0080
7  RIGHT   0x0020
8  A       0x2000
9  X       0x1000
10 L       0x0400
11 R       0x0800
12 L2      0x0100
13 R2      0x0200
14 L3      0x0002
15 R3      0x0004
```

The callback rejects only ports >= 2.

## Existing remapping capability

The stock `.kmp` compiler processes six remappable physical controls per player. Each mapping record contains:

```text
low 16 bits -> target libretro joypad ID
bit 16      -> turbo/repeat flag
```

The selector is used directly against the same 16-entry libretro mask table. Therefore stock firmware infrastructure can target hidden IDs `L2`, `R2`, `L3`, and `R3` even though the stock UI never exposes them.

Examples:

```text
0x0000000c -> L2
0x0000000d -> R2
0x0000000e -> L3
0x0000000f -> R3
0x0001000c -> L2 + turbo
...
```

## Physical-to-port path

The two controller streams remain independent end-to-end:

```text
GPIO B15 -> slot 0 -> libretro port 0 / Player 1
GPIO L0  -> slot 1 -> libretro port 1 / Player 2
```

The serial physical ordering is:

```text
R, Y, X, L, A, B, SELECT, START, UP, DOWN, LEFT, RIGHT
```

Only the six action/shoulder controls are remapped by the stock keymap compiler; SELECT/START/D-pad retain their fixed frontend semantics.

## Consequence for the generic runtime

Do not replace the proven stock input callback with a new input driver unless a later core proves it necessary.

The generic runtime should:

1. keep `xgo_stock_input_state()` as the libretro input source;
2. preserve fixed SELECT/START/D-pad behavior, including the hardware-proven `Select+Start` frontend exit gesture;
3. treat the stock `.kmp` representation as a reusable mapping layer for the six physical action/shoulder controls;
4. expose all 16 joypad target IDs to tooling/configuration, including hidden L2/R2/L3/R3;
5. account for the documented stock `.kmp` persistence issue that can mirror Player 2 mappings if the stock persistence routine is used unchanged.

## SNES implication

A conventional SNES pad needs D-pad, SELECT, START, A/B/X/Y, L/R. Those controls already exist directly in the XGO/libretro input contract. Therefore SNES does not require hidden trigger IDs merely to achieve a standard SNES layout.

The hidden L2/R2/L3/R3 capability is still valuable for later systems/cores and for custom mapping tools.

## Next input task

The next engineering task is not a low-level driver rewrite. It is to define a core-neutral mapping policy/configuration layer around the existing proven callback and `.kmp` compiler semantics.
