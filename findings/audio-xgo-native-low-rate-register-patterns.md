# Exact XGO 11025/22050 clock-register programming patterns

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **BIN — REGISTER PROGRAMMING CLOSED, FIELD NAMES OPEN**

## Purpose

After correcting the MIPS delay-slot provenance in the native-rate comparison chain, the exact register values for the low-rate cases can be pinned without guessing vendor field names.

## 11025-Hz case [BIN]

Comparison:

```text
0x8030C3E4  bne s1,v0,0x8030C45C   ; v0 = 11025
0x8030C3E8  li  v0,22050            ; delay slot prepares next comparison
```

Programming body begins at `0x8030C3EC`.

It writes:

```text
0xB8800478 = 0x0119000E

0xB8800470:
    clear mask 0x00300000
    set        0x00200000

0xB8800148:
    preserve low 23 bits / replace upper selector with 0x20000000
    clear low 10-bit field
    set low field to 0x0200
```

## 22050-Hz case [BIN]

Comparison:

```text
0x8030C45C  bne s1,v0,0x8030C4D4   ; v0 = 22050
0x8030C460  li  v0,44100            ; delay slot prepares next comparison
```

Programming body begins at `0x8030C464`.

It writes:

```text
0xB8800478 = 0x0119000E

0xB8800470:
    clear mask 0x00300000
    set        0x00200000

0xB8800148:
    preserve low 23 bits / replace upper selector with 0x10000000
    clear low 10-bit field
    set low field to 0x0100
```

## Relationship

The 11.025- and 22.05-kHz cases share the same upstream clock-control values at `0xB8800478` and `0xB8800470`.

Their `0xB8800148` selectors scale by exactly two:

```text
11025: upper selector 0x20000000, low field 0x0200
22050: upper selector 0x10000000, low field 0x0100
```

That is strong binary evidence that these are intentional native divider configurations, not unreachable placeholder comparisons.

The exact vendor names of the `0xB8800148` fields remain OPEN.

## 44100 transition

The next comparison at `0x8030C4D4` is the 44100-Hz case.

It has a conditional subconfiguration selected by a GP state byte, so its exact register pattern should not be reduced to one unconditional value without first naming that selector.

This note deliberately does not overstate the 44.1-kHz branch.

## Fidelity significance

The low-rate hardware support is now stronger than a mere accepted numeric value:

- the binary contains dedicated low-rate branches;
- each branch writes a coherent, distinct divider pattern;
- 11.025 and 22.05 kHz form an exact 2:1 register relationship.

The stock higher layer nevertheless replaces both with 44.1 kHz and repeats source frames.

## Evidence boundary

- branch addresses and delay-slot provenance: **BIN**
- register addresses/masks/values: **BIN**
- interpretation as intentional divider relationship: **INF strongly supported by BIN**
- vendor field names and analog-output qualification: **OPEN**

## Hardware gate

Not reached.
