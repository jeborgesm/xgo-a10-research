# Hidden Controller-Test Trigger

Status: **firmware trigger and input-code mapping confirmed; physical reproduction still pending**.

## Summary

The XGO firmware contains a direct hidden launch path for `Resources/Test.zsf`, the bundled SNES controller-test program.

The application checks the previous Player 1 joystick event word for the exact value `0x1001`. If it matches, execution branches directly into code that displays `LOADING......`, resolves `%s/Resources/Test.zsf`, and launches the file.

Disassembly:

```text
0x80356444  lw    $15, -0xd34($gp)      # previous P1 event word
0x80356448  addiu $14, $zero, 0x1001
0x8035644c  beq   $15, $14, 0x80358fb4  # hidden Test.zsf path
```

The test-launch path later references the hard-coded resource string through the pointer table at `0x809a3658`:

```text
0x809a351c  "LOADING......"
0x809a352c  "%s/Resources/Test.zsf"
0x809a3658  -> 0x809a352c
```

This proves `Test.zsf` is not merely an unused bundled resource: stock application code contains an explicit input-triggered launch path for it.

## Event-code mapping

The main controller routine at `0x8035d4c4` first combines each local serial controller state with the corresponding RF state. It then translates the raw 12-button bitmap into a UI/joystick event word stored beginning at `gp - 0xd18`.

For Player 1, the relevant translations are:

| Physical/raw button | Raw mask | UI event mask |
|---|---:|---:|
| SELECT | `0x0020` | `0x0001` |
| START | `0x0010` | `0x0008` |
| UP | `0x0008` | `0x0010` |
| DOWN | `0x0004` | `0x0040` |
| LEFT | `0x0002` | `0x0080` |
| RIGHT | `0x0001` | `0x0020` |
| A | `0x0080` | `0x2000` |
| B | `0x0040` | `0x4000` |
| L | `0x0800` | `0x1000` |
| X | `0x4000` | `0x0400` |
| Y | `0x2000` | `0x0800` |
| R | `0x1000` | `0x8000` |

Therefore:

```text
0x1001 = 0x1000 | 0x0001
       = L      | SELECT
```

The hidden controller-test trigger is consequently **Player 1 L + SELECT**, not raw mask `0x1001` interpreted directly.

The equality check is exact, so the safest reproduction attempt is to hold **only L and SELECT together**, without additional buttons.

## Current-state vs previous-state words

During controller processing:

```text
gp - 0xd18   Player 1 translated/current event word
gp - 0xd14   Player 2 translated/current event word
```

A separate routine copies these into:

```text
gp - 0xd34   previous/snapshotted Player 1 event word
gp - 0xd30   previous/snapshotted Player 2 event word
```

The menu loop checks `gp - 0xd34` against `0x1001`, so the trigger is sourced from Player 1 input after the normal local/RF merge and button translation.

## Why this matters for Handle Interface research

A reproducible controller-test screen gives a non-invasive diagnostic environment for the external Player 2 path.

Once `Test.zsf` is running, the most informative experiment is to insert the empty OTG adapter that normally freezes menu controls and observe the diagnostic display:

- if Player 2 suddenly reports many or all buttons pressed while Player 1 remains observable, that strongly supports the hypothesis that OTG pin 4 grounds the active-low P2 serial DATA line;
- if both controller states stop changing or the test itself becomes globally unresponsive, a shared-clock or lower-level mode/pinmux disruption remains more plausible;
- a repeatable partial P2 pattern would provide further information about which controller signal the adapter is loading.

## Confidence

### CONFIRMED from firmware

- the application contains the literal path `%s/Resources/Test.zsf`;
- executable code branches into that launch path when the Player 1 event word equals `0x1001`;
- controller event translation maps SELECT to `0x0001` and L to `0x1000`;
- therefore `0x1001` corresponds to **L + SELECT**;
- the comparison is an exact equality test.

### TO VERIFY PHYSICALLY

- whether holding only L + SELECT from the normal XGO menu reliably launches the test on this unit;
- whether the trigger requires a short hold, edge, or menu state beyond the exact event combination;
- what P1/P2 state the diagnostic shows when the empty OTG adapter is inserted.
