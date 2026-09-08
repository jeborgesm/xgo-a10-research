# Arcade Test15 hardware result — external MAME2000 black-screen hang

Date: 2026-09-08
Branch: `research-game-list-arcade-expansion`

Status: **HARDWARE FAIL — Classic Arcade external MAME2000 path does not reach gameplay**

## Hardware result

Both fifth-page games tested under Test15:

- Pac-Man
- Ms. Pac-Man

produce the same behavior:

- screen goes black;
- no game video appears;
- device becomes unresponsive;
- normal pause/quit recovery is unavailable.

This is materially different from the previously proven MAME2000 CPS1 Test12, where Street Fighter II reached playable gameplay.

## Interpretation

Because two independent classic sets fail identically before any visible MAME gameplay, classify Test15 as an integration/path failure rather than evidence that MAME2000 cannot emulate these games on XGO.

The strongest newly identified mismatch is in the inherited MAME2000 frontend:

`xgo_mame2000_frontend.c`

The old CPS1 integration ignores the `filename` argument passed to the external-core entry and constructs the ROM path from fixed stock globals:

```text
XGO_STOCK_SYSTEM_DIR @ 0x810a0eb0
XGO_STOCK_GAME_NAME  @ 0x8109fce8
```

That contract was proven for the stock CPS1 list, but list ID 11 is newly activated and uses a synthetic `Resources/None` catalog. There is no proof those globals carry the same inner-archive basename semantics on ID 11.

Stock FBA can still launch Pac-Man from Test10/Test14 because stock FBA understands the XGO `.zfb` wrapper path itself. The external MAME frontend may therefore be constructing an invalid `ARCADE/bin/...` content path before entering MAME.

## Next correction

Do not alter MAME2000 emulation yet.

Build a Classic-Arcade-specific frontend that derives the real archive basename directly from the selected XGO `.zfb` wrapper:

```text
selected ARCADE/<title>.zfb
 -> read wrapper
 -> skip 59,904-byte RGB565 thumbnail
 -> skip 4-byte reserved field
 -> read NUL-terminated archive basename
 -> construct /mnt/sda1/ARCADE/bin/<basename>
 -> pass exact path to MAME2000 retro_load_game
```

This removes the CPS1-era stock-global assumption entirely.

Test15 remains non-golden and must not be promoted.
