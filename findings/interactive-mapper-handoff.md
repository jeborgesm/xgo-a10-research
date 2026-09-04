# Interactive mapper handoff

## Status

**Hardware-confirmed complete on September 3, 2026.**

Interactive mapper v19 is the branch-closing implementation for the first XGO on-device remapping feature.

## User-visible behavior

```text
Start+Select
  -> stock pause menu
  -> Mapper (fifth option)
  -> A/Confirm opens mapper
  -> arrows change the selected physical control / logical target
  -> A/Confirm saves and resumes gameplay
```

Six physical remappable controls are exposed:

```text
X Y L A B R
```

Mappings use the XGO's existing 48-byte active keymap and existing per-game `<game>.kmp` persistence. Persistence has been confirmed after closing and reopening a game.

Hardware exercise includes NES, SNES, and CPS1.

## Manufacturer lineage recovered

GB300 v1 supplied the missing behavioral model:

```text
pause position 5
  -> native mapper state machine
  -> six physical controls
  -> logical assignment/turbo state
  -> 48-byte system mapping
  -> KeyMapInfo.kmp
```

XGO reuses the interaction concept above persistence, but terminates through its own active 48-byte mapping and existing per-game writer rather than GB300's global seven-system `KeyMapInfo.kmp` store.

## Critical implementation lessons

1. The XGO writer/loader filename mismatch was real; renaming the generated KMP to the filename the loader actually consumes proved persistence.
2. Mapper entry must be explicit from the pause menu. Automatically activating position five created a blind/hostile UI.
3. A/Confirm is the proven save-and-resume control. Start+Select is not the mapper commit action.
4. Static mapper artwork and dynamically drawn yellow selectors share one coordinate system. Scaling artwork without transforming marker coordinates creates ambiguous selections.
5. v8 introduced a resource-only regression by replacing `x=225..259` for all 480 rows. Firmware was unchanged from v7. Later visual builds inherited this amputated geometry.
6. v19 fixes the root cause by combining intact v7 geometry with mature v14 behavior, then transforming selector coordinates against the complete geometry.

## Final v19 geometry

```text
intact v7 mapper: x=225..639, 415 x 480
v19 scale:        88%
v19 canvas:       x=250, y=29, 365 x 422
physical marker:  x=290
target marker:    x=465
marker Y:          154 + row*37
```

Legend:

```text
A = OPEN / SAVE+PLAY
ARROWS = CHANGE
```

## Final v19 identity

```text
firmware SHA-256:
466b336ee601f16314b73fbc66f0135a7090942157fce77c749391fbaa4189ab

LCFG CRC-32/MPEG-2:
0x83bc2420

gpapi.bvs SHA-256:
759cc078816e6b865ac177ca39a37bb542ae5f64bbfbf0c0cb10f230532950c8

hardware-test card ZIP SHA-256:
c45925f965cf86b4e1efc622b02aabb5545122814743aaf7723d4dbf6ba4ec81
```

## Release/preservation recommendation

Do not make the proprietary stock `bisrv.asd` or stock XGO resources the canonical public release artifacts.

Canonical preservation should be:

- patch/build source;
- verified input hashes;
- exact binary offsets and transformations;
- generated-resource recipe;
- output hashes;
- hardware-test findings.

A public convenience release should preferably be a patcher/package that takes a user's verified stock XGO files and emits the modified firmware/resource locally. Internally, keep the exact v19 compiled test package and hashes as a golden hardware reference.

## Branch closure

The mapper feature itself is complete enough to merge. Cosmetic experiments v11-v18 remain useful archaeological evidence but are superseded by v19. Future work should start from the merged v19 state rather than any intermediate visual experiment.
