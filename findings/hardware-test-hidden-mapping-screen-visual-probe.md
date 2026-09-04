# Hardware test — hidden mapping-screen visual probe

Status: **HARDWARE CONFIRMED**

## Purpose

Hardware-confirm that the stock XGO in-game menu can safely expose its dormant fifth background resource, `Resources/gpapi.bvs`, when the menu navigation upper bound is extended from four reachable positions to five.

This was deliberately a visual-only proof. Static analysis predicted that the interactive position-5 editor logic is absent, so button remapping was not expected to work yet.

## Hardware result

**SUCCESS.**

On physical XGO hardware, the one-instruction navigation patch allows the stock Select+Start in-game menu to advance to the hidden fifth position and display the controller/action mapping background.

Observed behavior:

- the hidden controller mapping screen renders successfully;
- the screen contains the expected D-pad and six circular action-button positions from `gpapi.bvs`;
- no normal menu label/text is drawn for this fifth position;
- activating/confirming the fifth position performs no mapping action;
- the device remains responsive and can navigate away from the hidden position;
- the surrounding stock Save / Load / Quit / Resume menu remains intact.

This exactly matches the static prediction that the position-5 background renderer survived while the interactive editor/action handler did not.

User-supplied hardware photographs show the hidden screen rendered on the physical XGO immediately adjacent to the normal in-game menu.

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

## Proven execution chain

Hardware now proves:

```text
stock Select+Start menu
        -> patched navigation bound permits index 4
        -> stock five-entry background table
        -> index 4 selects gpapi.bvs
        -> stock renderer
        -> physical XGO display
```

The hidden screen is therefore not merely an unused SD-card asset or a static firmware-table artifact. It is a genuinely renderable dormant fifth in-game-menu position in this XGO firmware.

## Negative hardware result is also useful

Confirm/action on the fifth position does not enter a mapper or alter controls.

That independently supports the whole-firmware static conclusion that the original interactive position-5 editor/action body was removed or compiled out. The surviving pieces are the visual shell and lower-level keymap infrastructure, not a complete hidden feature that only needed its menu bound restored.

## Color observation during the same test

During this hardware run, the external FCEUmm image was reported to have returned to apparently correct black levels / brightness. Earlier external-core testing had shown slightly elevated brightness and gray/raised blacks relative to stock.

This observation is important but **not yet causally attributed to the mapping-screen patch**. The patch changes only one `slti` immediate in the menu navigation path and has no known connection to the video callback or RGB565 conversion path.

Therefore treat the color recovery as a new hardware observation requiring controlled reproduction, not as evidence that the menu patch fixed color. Candidate explanations to investigate include runtime initialization/state continuity, display-path state left by prior menu activity, core/runtime build differences, or another environmental variable between tests.

## Reproducibility tool

The branch contains:

```text
tools/patch_hidden_mapping_screen.py
```

The patcher is intentionally strict: it accepts only the exact preserved stock firmware SHA-256, verifies the original instruction and stock LCFG integrity fields, patches the single instruction, recomputes CRC-32/MPEG-2, and refuses in-place modification.

## Architectural consequence

The practical design can now proceed with hardware confidence:

```text
stock Select+Start menu
        |
        +-- positions 0..3 unchanged
        |
        +-- position 4: gpapi.bvs   [hardware proven]
                    |
                    +-- injected mapping controller
                              |
                              +-- edit existing 12-record mapping buffer
                              +-- reuse stock set_keymap()
                              +-- reuse stock .kmp writer
                              +-- return to stock menu/game
```

The next engineering target is therefore not further proof of screen reachability. It is the smallest possible position-4 controller/action hook: first edit one known mapping record in RAM, invoke the existing persistence path, and hardware-prove a deliberate button swap.