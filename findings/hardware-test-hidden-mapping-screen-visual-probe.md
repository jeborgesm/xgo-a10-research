# Hardware test — hidden mapping-screen visual probe

Status: **PACKAGE PREPARED; HARDWARE RESULT PENDING**

## Purpose

Hardware-confirm that the stock XGO in-game menu can safely expose its dormant fifth background resource, `Resources/gpapi.bvs`, when the menu navigation upper bound is extended from four reachable positions to five.

This is deliberately a visual-only proof. Current static analysis shows that the interactive position-5 editor logic is absent, so the test does not expect button remapping to work yet.

## Minimal firmware change

Runtime / ASD offset:

```text
0x80354ec0 / 0x00354ec0
```

Stock instruction:

```asm
slti s0,v1,3
```

Raw word:

```text
0x28700003
```

Probe instruction:

```asm
slti s0,v1,4
```

Raw word:

```text
0x28700004
```

The change permits the existing menu index to advance from 3 to 4. The stock five-entry background table already maps index 4 to `gpapi.bvs`.

No other executable instruction is changed.

## LCFG reseal

Stock firmware:

```text
SHA-256: 869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf
CRC-32/MPEG-2: 0x5ee51f11
```

After the one-instruction patch, the LCFG payload CRC becomes:

```text
0x6063fb0d
```

Generated probe firmware SHA-256:

```text
bcbb733d478ae115fd025286af4f5fb37953ed786ad6800701aec688d8fe58dd
```

## Expected hardware procedure

1. Back up the current `bios/bisrv.asd`.
2. Replace it with the generated probe firmware.
3. Leave `Resources/gpapi.bvs` unchanged.
4. Launch a game normally.
5. Open the stock Select+Start in-game menu.
6. Navigate one position beyond the normal fourth item.
7. Observe whether the controller/action background appears.
8. Pressing confirm on the fifth position is not expected to launch an editor.
9. Navigate back to a normal position and exit the menu normally.

## Safety reasoning

Static analysis supports this as a low-risk probe because:

- the renderer already contains a five-entry resource table;
- index 4 selects a valid existing pointer to `gpapi.bvs`;
- the renderer returns cleanly for index 4 after drawing the common background;
- the confirm dispatcher has no index-4 action body and falls back to the menu loop;
- the reverse/decrement navigation path already handles values greater than zero;
- no ROM, core, save-state callback, keymap buffer, or filesystem path is modified.

## Reproducibility tool

The branch contains:

```text
tools/patch_hidden_mapping_screen.py
```

The patcher is intentionally strict: it accepts only the exact preserved stock firmware SHA-256, verifies the original instruction and stock LCFG integrity fields, patches the single instruction, recomputes CRC-32/MPEG-2, and refuses in-place modification.

## Interpretation

Success would hardware-prove the final missing part of the dormant-screen claim:

```text
stock Select+Start menu
        -> index 4 reachable
        -> stock renderer
        -> Resources/gpapi.bvs
        -> real XGO display
```

It would not prove that the old interactive mapper survives. Current whole-firmware evidence says that editor logic was removed or compiled out.