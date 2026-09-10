# Arcade Test10 hardware result — fifth Arcade + Pac-Man PASS

Date: 2026-09-07
Branch: `research-game-list-arcade-expansion`

Status: **HARDWARE PASS with presentation/audio follow-ups**

## Direct hardware result

Changing `Resources/Foldername.ini` from:

```text
11 7 0
```

to:

```text
12 7 0
```

successfully exposes the previously hidden fifth Arcade section.

This proves the first control value is the active main-menu section count on XGO and that the inherited fifth `FF8000 ARCADE` definition is usable.

## Fifth-section presentation

The newly visible fifth Arcade tile uses CPS2 artwork rather than a distinct Classic Arcade image.

Inside the list:
- one game is shown: Pac-Man;
- Pac-Man has no game artwork because the probe intentionally used a blank thumbnail;
- the lower system-name/banner area is scrambled/invalid.

This is consistent with list ID 11 having no dedicated valid presentation-resource set in the shipped configuration. The section/list path itself works; dedicated Classic Arcade artwork/banner resources remain to be supplied or redirected.

## Pac-Man execution

Pac-Man launches and is playable through the stock XGO arcade emulator.

Observed:
- gameplay works normally;
- controls work;
- stock pause menu works correctly;
- game has **no sound**.

This is decisive proof that the Pac-Man driver in the shipped XGO FBA payload is executable, not merely stranded string/ROM metadata.

The no-sound result is now a focused emulator-driver/audio initialization problem for the classic Pac-Man hardware path. It is not a frontend/list/wrapper failure.

## Architectural conclusions

Test10 proves all of the following:

1. XGO can expose a fifth native Arcade category with a one-byte ASCII config change (`11 -> 12` in the active-section count).
2. List ID 11 is reachable and can load a supplied `Resources/None` catalog.
3. A normal XGO `.zfb` reference can launch `ARCADE/bin/pacman.zip` from list ID 11.
4. The shipped stock FBA binary contains a working Pac-Man gameplay driver.
5. Existing stock pause-menu integration survives on this newly exposed classic driver.
6. The fifth page needs its own category artwork/system-banner resources.
7. Pac-Man's stock-driver audio path requires investigation.

## Priority next steps

1. Trace the fifth category's artwork/banner pointer selection and replace the CPS2/scrambled inherited presentation with a clean Classic Arcade identity.
2. Compare Pac-Man's compiled audio driver path with working stock arcade drivers to find why gameplay is silent.
3. Enumerate all non-CPS/NeoGeo/IGS drivers actually compiled into the XGO FBA binary and classify which can be added to the new fifth page.
4. Keep the user's requested classics as explicit targets: Pac-Man, Ms. Pac-Man, Galaga, Frogger, Donkey Kong, Mario Bros., Asteroids.
5. For targets absent from the stock binary, evaluate lifting the missing upstream FBA 0.2.97.42 driver modules or using the already-established external-core integration route.

## Hardware evidence images

User supplied three photographs showing:
- fifth Arcade category visible with CPS2 presentation;
- Pac-Man as the sole list entry with missing thumbnail and corrupted lower banner;
- Pac-Man running in-game through the stock arcade emulator.

These observations are authoritative hardware evidence for this milestone.
