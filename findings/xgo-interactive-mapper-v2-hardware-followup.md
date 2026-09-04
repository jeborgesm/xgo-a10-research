# XGO interactive mapper v2 hardware follow-up

Status: **v1 arbitrary remapping hardware-proven; v2 UX/commit candidate ready for hardware test**

## v1 hardware result

The v1 interactive mapper successfully allowed arbitrary remapping on hardware. The tested device was able to change the face-button mapping so that A and B were exchanged.

This proves that the injected editor can:

- enter the dormant fifth mapper page,
- maintain independent physical-source and logical-target selectors,
- decode the current XGO 48-byte active map,
- stage arbitrary six-record edits,
- encode selector choices back into libretro logical IDs,
- and eventually persist the resulting mapping through the already-proven stock writer/loader path.

The hardware test also exposed several UX/control defects in v1:

1. The mapper artwork was partially transparent over the stock pause-menu graphics, causing text-on-text overlap.
2. Pressing the intended `START` save control gave no obvious response.
3. The user ultimately exited the mapper by pressing physical L, proving that the inferred standalone auxiliary event assignments in v1 were not trustworthy.
4. Because commit/resume feedback was ambiguous, it appeared possible that moving the yellow selectors itself was committing changes even though the code was intended to stage them until save.

The correct conclusion is that v1 proved arbitrary mapping but did **not** prove the standalone Start/Select raw event identities.

## Important input correction

Stock XGO directly proves only the combined Start+Select raw controller state:

```text
0x1001
```

The frontend checks this exact value to detect the existing Start+Select menu chord.

v1 incorrectly assigned the two component bits individually as:

```text
0x1000 -> START/save
0x0001 -> SELECT/cancel
```

The hardware result invalidates those labels. They must not be treated as established physical-button identities.

## v2 design

v2 deliberately removes the guessed individual auxiliary-button interpretation.

### Launcher

The fifth pause-menu page remains a launcher. Reaching it does not edit or save anything.

```text
RIGHT -> enter editor
A     -> ignored on launcher
```

### Editor

Only the four hardware-established D-pad event values manipulate editor state:

```text
0x10 / 0x40 -> physical source selector
0x80 / 0x20 -> logical target selector
```

Face and shoulder events are ignored while editing.

The six selected mappings are held in an injected working buffer. Arrow movement therefore changes staging state only; it does not write the active `0x810a0f58` map.

### Save and resume

v2 commits only when the current raw controller state equals the exact stock-proven Start+Select chord:

```text
raw controller state == 0x1001
```

At that point v2:

1. converts all six staged selector values through the recovered logical-ID encode table,
2. updates the six P1 records in the active XGO 48-byte map,
3. enters the previously hardware-proven writer/resume path,
4. allows the stock writer to mirror P1 into P2 and write the corrected per-ROM `.kmp`,
5. and resumes gameplay immediately.

This makes the commit action unambiguous and avoids using any of the six remappable buttons.

## Visual correction

The v2 `gpapi.bvs` replacement is completely opaque rather than a translucent overlay. No stock pause-menu graphics should bleed through it.

The screen presents two columns:

```text
PHYSICAL        MAP TO
X               B
Y               Y
L               A
A               X
B               L
R               R
```

Two yellow bars identify the current source and target selectors.

Footer:

```text
ARROWS = CHANGE     START+SELECT = SAVE + PLAY
```

## Candidate identity

Exact stock input SHA-256:

```text
869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf
```

v2 firmware:

```text
SHA-256: e25ca2e9962e5ee1e7c5f7526b6642c831fe2cd350b5988f507ac1c646d868b5
LCFG CRC-32/MPEG-2: 0x0c017409
```

The v2 injected routine begins at `0x800014a0`, is 936 bytes long, and ends at `0x80001848`, remaining inside the previously verified zero-filled cave.

Stock instruction edits are limited to:

```text
0x00354054  writer filename buffer repair
0x00354ec0  expose dormant page 4
0x00354e88  page-4 dispatcher hook into injected editor
```

Unlike v1, the stock input-poll mask at `0x00354e78` is left unchanged at `0x20f8`; Start+Select commit is detected from the refreshed raw controller-state global instead.

## Next hardware acceptance test

The acceptance test for v2 is intentionally short:

1. Open the fifth `BUTTON MAPPER` page.
2. Press Right; yellow selectors must appear.
3. Change A/B or another obvious mapping with the arrows.
4. Press Start+Select together.
5. The mapper must immediately disappear and gameplay must resume.
6. The selected remap must be active.
7. Restart the game and verify persistence.

If this passes, arbitrary six-button mapping plus explicit save/resume is hardware-proven. Standalone Start can be investigated separately without blocking a usable mapper.