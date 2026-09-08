# Arcade Test14 hardware result — Ms. Pac-Man stock FBA path broken

Date: 2026-09-07
Branch: `research-game-list-arcade-expansion`

Status: **HARDWARE FAIL for Ms. Pac-Man stock driver / architectural pivot evidence**

## Direct hardware result

Pac-Man remains playable but silent through the stock XGO FBA driver.

Ms. Pac-Man was added to the proven fifth Arcade section and launched through the same stock XGO arcade path.

Observed Ms. Pac-Man behavior:
- game executes far enough to render active game state;
- video is severely corrupted/glitched;
- audio is absent;
- result is not acceptably playable.

Photographic hardware evidence supplied by the user shows corrupted Ms. Pac-Man gameplay output.

## Conclusion

The hidden classic drivers embedded in the vendor FBA payload are not a reliable basis for the requested Classic Arcade library.

Pac-Man:
- gameplay: PASS
- video: PASS
- audio: FAIL

Ms. Pac-Man:
- execution: partial
- video: FAIL
- audio: FAIL

This strengthens the case for using the fifth Arcade category as a frontend/library surface while routing its games to a separate classic-arcade emulator.

## MAME2000 reconsideration

The project already proved an XGO-native external MAME2000 integration:
- core builds and loads on HC15xx/MIPS32;
- arcade ZIPs can be launched;
- video works;
- input was repaired;
- state contamination was isolated;
- XGO pause/OSD/runtime integration can coexist with the external core.

MAME2000 was rejected previously **as a CPS1 replacement** because Street Fighter II remained slower than stock even with frameskip. That result does not establish that early 1979-1984 arcade hardware is too slow.

The user's target set is exactly the class where MAME2000 is a much better architectural candidate:
- Asteroids
- Pac-Man
- Ms. Pac-Man
- Donkey Kong
- Mario Bros.
- Frogger
- Galaga

These are dramatically less demanding than CPS1 SFII and are canonical MAME-era targets.

## New direction

Preserve:
- stock FBA for CPS1/CPS2/NeoGeo/IGS;
- fifth Arcade category as Classic Arcade frontend;
- golden Test08 console scanner.

Route list ID 11 / Classic Arcade to a dedicated external MAME2000 core rather than stock FBA.

First proof should use Pac-Man and Ms. Pac-Man with MAME2000-compatible 0.37b5 ROM sets, reusing the already-proven external-core loader/runtime work.

Do not infer failure from the old CPS1 MAME2000 performance result; benchmark these much lighter classic drivers directly.
