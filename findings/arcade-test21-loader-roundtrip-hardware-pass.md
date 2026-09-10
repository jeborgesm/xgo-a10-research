# Arcade Test21 hardware PASS — list-11 external-core round trip proven

Date: 2026-09-08
Branch: `research-game-list-arcade-expansion`

Status: **HARDWARE PASS — loader/XGOC/entry/return boundary proven**

## Hardware result

Selecting Pac-Man from the fifth Arcade page produced ordinary stock Pac-Man gameplay after the Test21 continuity probe.

Pac-Man retained the already-known stock-FBA behavior:
- gameplay/video correct;
- controls functional;
- audio absent.

## Important distinction from the original fifth-page Pac-Man test

The visible end result is intentionally the same, but the internal path is not.

Original fifth-page proof:

```text
list 11 -> stock run_fba -> Pac-Man
```

Test21:

```text
list 11
 -> Classic Arcade external loader
 -> open/validate XGOC
 -> stop stock sound task
 -> move RAMSIZE ceiling
 -> copy payload to 0x87000000
 -> verify payload CRC
 -> zero runtime memory
 -> repair IRQ GP
 -> flush caches
 -> execute 16-byte XGO1 code at 0x87000000
 -> return to loader
 -> restore RAMSIZE
 -> XGO1 handshake
 -> stock run_fba
 -> Pac-Man
```

Therefore the list-11 external-core transfer boundary itself is proven functional.

## Closed failure domains

The Test15/16 full-MAME freeze is NOT explained by:
- inability to enter the list-11 loader;
- failure to open/validate a valid XGOC;
- upper-RAM payload copy;
- payload CRC;
- IRQ-GP repair;
- cache coherency sufficient for minimal external execution;
- inability to jump to 0x87000000;
- inability to return from external code to the loader.

Test20 additionally ruled out later golden `run_emulator()` changes as the primary blocker.

## Next direction: real MAME staged-return ladder

Do not repeat stock-Pac-Man observables.

Use the exact real MAME2000 image and progressively return at these boundaries:

1. production entry veneer -> immediate return;
2. enter `__core_entry_c` -> immediate return;
3. `init_core_runtime()` -> return;
4. ROM path construction -> return;
5. install callbacks/environment -> return;
6. `retro_init()` -> return;
7. content setup / `retro_load_game()` -> return;
8. only then enter stock `run_emulator()`.

Each stage should return naturally to the game list or another unambiguous non-frozen path, without filesystem tracing.

The first stage that freezes identifies the failing external-runtime layer.
