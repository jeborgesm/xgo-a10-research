# Hidden Controller-Test Trigger

Status: **firmware trigger, input-code mapping, and physical reproduction confirmed**.

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

The hidden controller-test trigger is consequently **Player 1 L + SELECT**.

The equality check is exact, so the safest reproduction is to press only **L + SELECT** together.

## Physical reproduction — confirmed

On the tested XGO unit, pressing **L + SELECT** from the normal menu reliably launches the Super Famicom-style controller diagnostic corresponding to `Resources/Test.zsf`.

With no accessory attached, all Player 1 controls can be exercised normally in the diagnostic.

This turns the bundled test ROM into a useful non-invasive input probe for Handle Interface experiments.

## OTG-adapter behavior inside the diagnostic

A bare OTG adapter was inserted while `Test.zsf` was running.

Observed:

- all usable controller input immediately stopped responding;
- no button acknowledgement appeared in the diagnostic after insertion;
- the on-screen test timer continued running;
- therefore the emulator/application itself did **not** hang.

The important distinction is now:

```text
OTG adapter inserted
    -> input path becomes unresponsive
    -> Test.zsf / emulator / CPU continue executing
```

The previously used word `freeze` should therefore be interpreted as an **input freeze**, not a whole-system lockup.

This result weakens the simple model `pin 4 grounded -> only P2 DATA stuck low`. The XGO firmware scans two independent local data lines in parallel; a fault confined only to the external/P2 data line would not naturally explain complete loss of usable P1 input while the test ROM keeps running.

The result better fits one of these broader mechanisms:

1. grounding the OTG-specific contact alters shared controller-interface hardware state;
2. the connector contact affects a shared clock/load/pinmux resource used by both serial channels;
3. lower-level USB/OTG hardware changes GPIO ownership without stopping the emulator task.

The exact mechanism remains unresolved.

## Zero-delay encoder experiment

A generic zero-delay USB arcade encoder was then attached through the **non-OTG** connection while `Test.zsf` was running.

Observed:

- the XGO still did not recognize the encoder as a usable USB controller;
- built-in input did not globally freeze;
- the diagnostic showed **R continuously asserted**;
- no comparable continuous assertion of the other buttons was observed.

This is especially interesting because **R is serial sample 0** in the reconstructed XGO local-controller scan:

```text
sample 0   R
sample 1   Y
sample 2   X
sample 3   L
sample 4   A
sample 5   B
sample 6   SELECT
sample 7   START
sample 8   UP
sample 9   DOWN
sample 10  LEFT
sample 11  RIGHT
```

The scanner drives each DATA line low during its load/reset phase, releases it back to input, and immediately samples R before beginning the clock sequence for the remaining bits.

Therefore an external USB device producing a transient or slow recovery on a connector contact shared with the serial DATA line could plausibly yield exactly this symptom:

```text
host drives DATA low
    -> releases DATA
    -> immediate sample still reads low  => R asserted
    -> line recovers high before later samples
    -> remaining buttons read inactive
```

This is now a strong candidate explanation for the R-only pattern.

It is not yet proof that USB D+ or D- is physically the controller DATA contact, but it is the first accessory experiment to produce a specific bit pattern matching the reconstructed serial timing.

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

## Confidence

### CONFIRMED from firmware

- the application contains the literal path `%s/Resources/Test.zsf`;
- executable code branches into that launch path when the Player 1 event word equals `0x1001`;
- controller event translation maps SELECT to `0x0001` and L to `0x1000`;
- therefore `0x1001` corresponds to **L + SELECT**;
- the comparison is an exact equality test;
- R is the first serial sample after the DATA-line load/release phase.

### CONFIRMED physically

- L + SELECT reproducibly launches the bundled controller diagnostic;
- normal Player 1 buttons are visible and testable there;
- bare OTG insertion kills controller input while the diagnostic timer continues running;
- a zero-delay USB arcade encoder through a non-OTG path causes R to appear continuously asserted without globally freezing the test.

### STRONG EVIDENCE

- the OTG symptom is an input-subsystem failure rather than a whole-system hang;
- the simple `pin 4 = P2 DATA only` model is less likely than before;
- at least one ordinary USB-connected electrical state can perturb the serial scanner even when ID remains open;
- the zero-delay board's R-only pattern is consistent with a slow/transient line recovery immediately after the firmware's DATA-low load phase.

### NOT YET CONFIRMED

- which micro-USB contact carries the serial DATA signal;
- whether the affected ordinary USB contact is D+ or D-;
- whether B15 or L0 is physically the Handle Interface data channel;
- whether OTG ID grounding changes pinmux/ownership, shared clock behavior, or another piece of interface circuitry.

## Best next discriminator

The most valuable next passive measurement is now to determine the idle voltage behavior of the ordinary micro-USB data contacts with the XGO powered, using a high-impedance voltmeter only.

A particularly useful comparison would be:

- connector with nothing attached;
- non-OTG cable only;
- zero-delay encoder attached through non-OTG;
- bare OTG adapter.

Do not use continuity/resistance mode while powered and do not short adjacent contacts.
