# Hidden libretro input targets in XGO keymaps

Status: **confirmed from `set_keymap()` and `retro_input_state_cb()` executable behavior**.

## Headline

XGO exposes the full 16-ID libretro joypad namespace for both controller ports even though the physical serial scanner only has 12 positions. The per-game/default `.kmp` compiler accepts those IDs as mapping targets.

This means the six remappable physical action/shoulder controls can target not only `B/Y/A/X/L/R`, but also the otherwise hidden libretro controls `L2`, `R2`, `L3`, and `R3`.

## `retro_input_state_cb()` table

`retro_input_state_cb` at `0x8035eb20` computes an index as:

```text
(port * 16 + id) * 4
```

into the table at `0x80a3d4d0`, and ANDs the selected mask with the final mapped controller word at `0x80c33ac4 + port*4`.

Both port tables are identical:

```text
id  libretro name   XGO final-state mask
0   B               0x4000
1   Y               0x8000
2   SELECT          0x0001
3   START           0x0008
4   UP              0x0010
5   DOWN            0x0040
6   LEFT            0x0080
7   RIGHT           0x0020
8   A               0x2000
9   X               0x1000
10  L               0x0400
11  R               0x0800
12  L2              0x0100
13  R2              0x0200
14  L3              0x0002
15  R3              0x0004
```

The callback rejects only `port >= 2`; IDs 0..15 are represented by the table.

## `.kmp` compiler accepts IDs 12..15

`set_keymap()` at `0x8035e83c` processes twelve 32-bit mapping records: six for Player 1 followed by six for Player 2.

For every remappable physical control it takes:

```text
low 16 bits  -> target libretro joypad ID
bit 16       -> turbo/repeat flag
```

The low selector is used directly to index the same 16-entry mask table used by `retro_input_state_cb`. There is no check restricting the selector to the six IDs used by stock defaults.

Therefore these are valid hidden targets:

```text
0x0000000c -> L2
0x0000000d -> R2
0x0000000e -> L3
0x0000000f -> R3

0x0001000c -> L2 + turbo
0x0001000d -> R2 + turbo
0x0001000e -> L3 + turbo
0x0001000f -> R3 + turbo
```

## Stock defaults explain why this stayed hidden

The embedded default maps use only IDs 0, 1, 8, 9, 10, and 11 (`B/Y/A/X/L/R`) plus the `0x10000` turbo bit for duplicate NES/GB controls. The stock UI never exposes L2/R2/L3/R3.

The capability therefore exists below the UI layer.

## Practical consequence

An XGO PC configuration tool can expose a richer mapping editor than the original firmware UI:

- six remappable physical controls per player;
- any libretro joypad target ID 0..15;
- optional turbo on each mapping;
- hidden L2/R2/L3/R3 targets;
- independent in-memory P1/P2 mappings, subject to the stock `.kmp` persistence routine's known P2-mirroring behavior if that routine is used unchanged.

For an XGO Multicore port this is particularly useful because newer libretro cores commonly expose extra shoulder/trigger inputs that the stock emulator set never needed.
