# XGO Controller Scanner — Binary Search Signature

Status: **confirmed from original XGO `bios/bisrv.asd`**.

## Purpose

This note records byte-level landmarks for the XGO local/controller scanner so firmware from DY19, PGP AIO Union X35/X60, GB300 variants, and other HC15xx/H1512 siblings can be screened quickly before full disassembly.

The offsets below are file offsets in the preserved XGO `bisrv.asd` and correspond to previously reconstructed controller routines.

## Scanner entry vicinity

File offset `0x35D770` begins:

```text
80 b8 13 3c ff ff 05 24 ef dd 0b 0c 58 03 71 36
f4 f2 80 af d4 81 0b 0c d8 f2 80 af 00 00 2e 8e
ff ff 18 3c ff 7f 0f 37 24 68 cf 01 00 80 b4 35
58 00 07 03 60 00 03 4a ed e8 10 b0 c0 00 00 00
```

The first instruction word is little-endian `0x3c13b880`, i.e. loading the `0xb880....` GPIO register base used throughout the scanner.

A practical initial search pattern is therefore the opening 16 bytes:

```text
80 b8 13 3c ff ff 05 24 ef dd 0b 0c 58 03 71 36
```

Do **not** assume this whole sequence will survive recompilation. The high-value semantic landmarks are the `0xb880` register-base loads plus the surrounding direction/data register accesses and timing calls.

## Controller initialization vicinity

File offset `0x35DEB0` begins:

```text
a8 ff bd 27 38 00 b2 af 80 b8 12 3c 34 00 b1 af
58 00 51 36 50 00 bf af 4c 00 b7 af 48 00 b6 af
44 00 b5 af 40 00 b4 af 3c 00 b3 af d4 81 0b 0c
30 00 b0 af 00 00 26 8e ff df 14 3c ff ff 87 36
```

Again, `80 b8 12 3c` is little-endian `lui s2, 0xb880`, consistent with GPIO initialization.

## Nearby controller-task phase code

File offset `0x35D6F0` begins:

```text
21 80 40 00 f4 a0 83 8f 01 00 70 30 85 ff 00 12
03 00 68 30 f0 f2 86 93 74 89 85 27 01 00 c2 24
03 00 5f 30 21 18 e5 03 00 00 65 90 f0 f2 9f a3
df 74 0d 0c 25 00 04 24 dc f2 99 97 de f2 98 97
```

This region sits immediately before the scanner call path and is useful when looking for larger function-level similarity.

## Semantic signature to search for in sibling firmware

A candidate match should not be accepted from one byte pattern alone. The strongest fingerprint is the combination of:

1. H1512/HC15xx GPIO register base `0xb880....`;
2. B-bank and L-bank data/direction accesses matching the reconstructed roles;
3. one shared output clock line;
4. two data lines temporarily switched to output and driven low;
5. approximately 4 microseconds before returning data lines to input;
6. 12 active-low samples per data stream;
7. clock-low delay of approximately 2 microseconds between samples;
8. two resulting controller state words consumed as P1/P2-like inputs.

For XGO specifically the reconstructed roles are:

```text
B15 = serial data channel 0
L0  = serial data channel 1
B7  = shared clock
```

## Why this matters now

Public DY19 firmware is referenced in community archives, but currently available copies are behind MEGA / old 4PDA-hosted material. This byte-level fingerprint gives us a fast validation path as soon as any `bisrv.asd` candidate is obtained.

A direct match of the scanner structure would be substantially stronger than shared resource filenames or frontend behavior, because it would tie the devices at the board-input implementation level.

## Confidence

### CONFIRMED

- the byte sequences above are taken directly from the preserved XGO `bios/bisrv.asd`;
- `0x35D770` is the reconstructed scanner vicinity;
- `0x35DEB0` is the reconstructed controller/RF GPIO initialization vicinity;
- these regions contain `0xb880` GPIO-base loads consistent with the prior static analysis.

### NOT YET CONFIRMED

- whether DY19 contains byte-identical sequences;
- whether sibling firmware was built from the same compiler/link layout;
- whether GPIO numbering is unchanged across sibling boards.

## Next use

When a DY19/X35/X60 firmware candidate is recovered:

1. search for the exact 16-byte scanner prefix;
2. if absent, search for `80 b8 ?? 3c` / `0xb880` GPIO-base loads;
3. inspect nearby code for the two-data/one-clock state machine;
4. compare timing calls, masks, and sample count against XGO;
5. only then assign protocol-equivalence confidence.
