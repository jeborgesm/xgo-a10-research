# Hardware test — Audio OSD v2 fine-volume PASS

Date: 2026-09-05
Candidate: `xgo-audio-osd-v2-fine-volume-test.zip`

## Result

**PASS.**

Physical XGO testing confirmed:

- intermediate software-volume values are audibly distinct;
- the single physical Volume button now provides many useful levels instead of the stock four;
- the OSD bar visibly tracks the finer levels;
- mute at zero still works;
- gameplay OSD behavior remains good;
- the user explicitly preferred this behavior.

The hardware-confirmed volume cycle is:

```text
0 -> 9 -> 18 -> 27 -> 36 -> 45 -> 54 -> 63 -> 72 -> 81 -> 90 -> 99 -> 0
```

This proves the final XGO sound-driver path does not collapse these intermediate frontend values back to the original four steps.

## Remaining frontend limitation

The main 640x480 frontend/game-selection menus do not continuously submit frames through `run_screen_write`.

Therefore volume changes are applied audibly in those menus, but the v2 bar does not become visible/refreshed until another frontend presentation occurs (for example launching a game).

Gameplay and the in-game pause menu do refresh the OSD normally.

This is a presentation-cadence limitation, not an audio or volume-state limitation.

## Artifact identity

Tested ZIP SHA-256:

```text
086c60d7595843c778b04663aa5922ccd05ac966b1c4cb5ee736a78edbba428c
```

Firmware SHA-256:

```text
6b3261a9871c2b5678428ae1985176718c140178564ea924241bf6889ec714ac
```

The exact tested ZIP is preserved in the private artifact vault at:

```text
golden/xgo-audio-osd-v2-fine-volume-test.zip
```

## Next step

Keep v2 as the protected fine-volume baseline and solve only the sparse main-menu repaint behavior.
