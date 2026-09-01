# XGO input topology synthesis: SF2000 logic + GB300 dual-data hardware pattern

## Status

Direct comparison of the reconstructed XGO scanner against current UniFrog SF2000 and GB300 input implementations.

## Headline

XGO is best described as a **hybrid HC15xx controller-bus implementation**:

- its **logical serialization is SF2000**: 12 active-low positions in the exact order `R,Y,X,L,A,B,SELECT,START,UP,DOWN,LEFT,RIGHT`;
- its **physical scanner topology is GB300-like**: two DATA lines sampled in parallel under one shared CLOCK, with both DATA lines temporarily driven low for the load phase.

This is stronger than saying XGO merely resembles either device. The current evidence shows that XGO combines traits that exist separately in the two best-documented HC15xx input implementations.

## SF2000 current open implementation

UniFrog uses:

```text
DATA  = L23
CLOCK = L24
```

Scan behavior:

```text
CLOCK high
DATA -> output
DATA low
wait 4 us
DATA -> input
wait 4 us settle
repeat 12 times:
    sample active-low DATA
    CLOCK low
    wait 3 us
    CLOCK high
    wait 3 us
```

The normalized 12-position result maps directly to the same logical button index sequence used by XGO.

FrogQEMU independently models the SF2000 local keypad as a 12-bit active-low L23/L24 shift source and defines the same exact index order.

## GB300 current open implementation

UniFrog uses:

```text
DATA0 = L27
DATA1 = L25
CLOCK = L26
```

Scan behavior:

```text
DATA0 -> output
DATA1 -> output
CLOCK -> output
DATA0 low
DATA1 low
CLOCK low
wait 4 us
DATA0 -> input
DATA1 -> input
wait 4 us settle
repeat 16 times:
    sample DATA0 active-low
    sample DATA1 active-low
    OR either active stream into one raw mask position
    CLOCK low
    wait 3 us
    CLOCK high
    wait 3 us
```

The current UniFrog GB300 normalizer uses the shift-position map:

```text
15,11,10,12,13,14,0,3,4,6,7,5,1,2,8,9
```

so GB300's 16-position physical order is not the same logical order as XGO/SF2000.

## XGO reconstructed scanner

XGO uses:

```text
DATA0 = B15
DATA1 = L0
CLOCK = B7
```

Scan behavior reconstructed from stock `bisrv.asd`:

```text
B7 idle high
DATA0 -> output
DATA1 -> output
DATA0 low
DATA1 low
wait about 4 us
DATA0 -> input
DATA1 -> input
sample both immediately
repeat across 12 positions:
    sample DATA0 + DATA1 active-low
    CLOCK low
    wait about 2 us
    CLOCK high
```

The two streams are not ORed together. They populate independent serial/local controller slots.

Exact XGO order:

```text
0  R
1  Y
2  X
3  L
4  A
5  B
6  SELECT
7  START
8  UP
9  DOWN
10 LEFT
11 RIGHT
```

## Side-by-side

| Property | SF2000 | GB300 | XGO |
|---|---|---|---|
| DATA lines | 1 | 2 | 2 |
| shared CLOCK | yes | yes | yes |
| active-low | yes | yes | yes |
| host drives DATA low for load | yes | both | both |
| DATA returns to input | yes | both | both |
| explicit load delay | 4 us | 4 us | ~4 us |
| explicit settle after release | 4 us | 4 us | none identified |
| physical samples | 12 | 16 | 12 |
| exact SF2000 logical order | yes | no | **yes** |
| parallel DATA sampling | no | **yes** | **yes** |
| channels kept separate | n/a | no, current implementation ORs | **yes** |
| idle clock before normal scan | high | restored high; load drives low | high |
| stock/open clock low delay | 3 us hardened | 3 us hardened | ~2 us |

## Confirmed interpretation

### CONFIRMED

- XGO and SF2000 share the exact 12-position logical protocol.
- XGO and GB300 share the dual-DATA/shared-CLOCK physical scanner shape.
- XGO and GB300 both drive two DATA lines low together and then return both to input.
- XGO uniquely preserves the two sampled streams independently in application state rather than collapsing them into one local-button mask.

### STRONG INFERENCE

XGO likely comes from a shared HC15xx input-driver lineage in which board variants combine reusable pieces of the same vendor controller architecture:

```text
SF2000
    one 12-bit local serial stream
    + separate wireless receiver path

GB300
    two physical keypad streams
    + shared clock
    + 16-position stock mapping
    + streams combined as one local control set

XGO
    two physical serial streams
    + shared clock
    + SF2000 12-position mapping
    + streams preserved as two controller slots
```

This is more consistent with an OEM board-variant driver than with an independently developed controller interface.

## Architectural consequence

The XGO input subsystem now looks less like "SF2000 plus an extra port" and more like a deliberate **two-player serialized keypad adaptation** built from the same HC15xx GPIO primitives used by both SF2000 and GB300.

That helps explain why XGO has:

- two local serial state words;
- a shared clock;
- one likely internal stream and one likely Handle-Interface stream;
- no USB enumeration gate;
- the same button contract as SF2000-compatible controllers.

It also strengthens the expectation that the external Handle Interface is electrically simple: a controller encoder only needs to participate in the same load/release/clock protocol and serialize the 12 SF2000-order button states.

## OTG R-only relevance

The topology comparison also makes the XGO R-only OTG artifact easier to frame.

Both modern UniFrog scanners deliberately wait 4 us after returning DATA to input before sampling. XGO has no separately identified post-release settle delay and samples position 0 immediately.

Therefore a board-specific detect/gate/bias circuit that slightly delays one DATA line's recovery can corrupt only position 0 (`R`) while leaving later positions inactive. This is consistent with the observed anonymous-OTG diagnostic result and is a more specific mechanism than a generic USB-mode theory.

## Research consequence

This comparison shifts priority away from further generic protocol hunting.

Highest-value unresolved questions are now:

1. which XGO DATA stream is internal versus Handle Interface;
2. whether D- or D+ carries B7 CLOCK;
3. whether the other D-/D+ contact carries B15 or L0 external DATA;
4. what micro-USB ID does to the load/release circuit;
5. whether an X60/DY12 controller can be directly adapted once the contact order is known.

## Sources

- XGO stock `bios/bisrv.asd` scanner reconstruction documented in this repository.
- `axgdev/UniFrog`, `foundation/src/platform/sf2000/input/unifrog_input.c` at current inspected revision.
- `axgdev/frogqemu`, SF2000 keypad reconstruction and exact logical key ordering.
