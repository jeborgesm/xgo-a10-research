# Independent Player-1 / Player-2 keymaps are supported on load

Status: **confirmed from the `.kmp` load/compiler path; stock save path intentionally mirrors P2 before persistence**.

## Headline

XGO's 48-byte per-game `.kmp` format genuinely carries two independent six-record mappings:

```text
records 0..5   Player 1
records 6..11  Player 2
```

The firmware's load/compiler path preserves that separation. The reason normal saved profiles appear synchronized is not a limitation of the runtime mapping engine; it is a policy in the stock `.kmp` writer.

Therefore a PC-side editor can create asymmetric Player-1 and Player-2 mappings that the unmodified XGO firmware will load and use.

## Load path

`run_emulator()` reads exactly 12 x 4-byte records from:

```text
%s/save/%s.kmp
```

into the 48-byte working mapping buffer and calls `set_keymap()` at `0x8035e83c`.

`set_keymap()` explicitly builds two independent player mapping blocks. Its player loop runs `player_index = 0..1`, advances the mapping source by six records / `0x18` bytes per player, and advances the compiled destination state by `0x40` bytes per player.

There is no load-time comparison or P1-to-P2 copy.

## Save path is where mirroring occurs

The stock persistence routine compares corresponding P1/P2 records using the known six-button permutation and, when they differ, copies the P1-side value into the P2-side record before writing the 48-byte file.

Thus:

```text
runtime format capability  = independent P1 and P2
stock writer policy        = force persisted P2 to mirror P1
```

These are separate behaviors.

## PC-tool consequence

An XGO card/configuration utility can safely expose two separate mapping editors and write the `.kmp` file directly.

The resulting profile can include, independently per player:

- different A/B/X/Y/L/R assignments;
- hidden L2/R2/L3/R3 targets;
- different turbo flags;
- different control layouts for the external Player-2 controller.

The stock firmware will load those values through its normal path.

## Caveat

If the user later invokes the stock firmware's mapping-save routine for that game, the on-device writer can overwrite the asymmetric profile and mirror P1 into P2 again.

A future firmware patch could remove that policy, but it is **not required** for a PC-managed asymmetric mapping workflow.

## Why this matters for Player 2

The Player-2 hardware path is already confirmed as:

```text
GPIO L0 -> mapped port 1 -> libretro port 1
```

This finding shows that the software mapping layer is also independently configurable for port 1. Once the external Handle Interface electrical connection is solved, Player 2 does not need to inherit Player 1's logical layout.
