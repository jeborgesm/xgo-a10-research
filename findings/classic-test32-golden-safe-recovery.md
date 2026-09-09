# Test32 — golden-safe CLASSIC recovery after Mapper v19 collision

Date: 2026-09-08
Branch: research-game-list-arcade-expansion

## Hardware regression that forced recovery

Test31 hardware:
- CLASSIC page visible and custom art acceptable;
- Pac-Man, Ms Pac-Man and Cadillacs and Dinosaurs all immediately returned to list;
- entering Contra pause menu showed Mapper yellow squares over the ordinary Resume/Quit/Load/Save menu;
- joystick moved Mapper markers while ordinary pause-menu options could not be selected.

This is a protected-golden regression.

## Root cause

The CLASSIC line from Test28 onward injected launcher code at:

```text
0x80001900..0x8000217f
```

Repository archaeology proves Mapper v19 occupies the early firmware cave beginning around:

```text
0x800014a0
```

and has active bytes throughout:

```text
0x80001500..0x8000217f
```

Therefore Test28-31 overwrote active Mapper v19 code.

The earlier Audio OSD archaeology had already documented:

> Existing low-memory cave is no longer available.

The CLASSIC work incorrectly violated that constraint.

This fully explains the Contra symptom and invalidates Test28-31 as regression-safe MAME evidence.

## Exact golden Test08 cave audit

Private CI scanned exact golden Test08:

```text
ZIP SHA-256
9c66fd727a2f894ad692b4868ba8bcee3daf2ff81b4d7eced539f80f2fd2e61e

firmware SHA-256
45831b0ea3c9ae336d82b240e6afe27167e5e83b88037152af237ab758ca1444
```

The Test08 scanner uses:

```text
0x807dab98...
```

and leaves a verified zero tail before:

```text
0x807dbba0
```

Test32 uses only that tail.

## Test32 architecture

Firmware contains only a 352-byte CLASSIC bootstrap at:

```text
0x807db9b0
```

The bootstrap:
- compares the stock current-system directory with `/mnt/sda1/CLASSIC`;
- non-CLASSIC immediately tail-jumps untouched stock `run_game @ 0x80360b88`;
- CLASSIC opens `/mnt/sda1/cores/classic/loader.bin`;
- loads fixed-size second stage to `0x86ff0000`;
- performs cache maintenance;
- calls the second stage with the original filename/load-state arguments.

The substantial CLASSIC launcher is no longer firmware-resident.

Second stage:
- 1,947 bytes;
- executes at `0x86ff0000`;
- verifies live heap remains below its reservation;
- parses the selected CLASSIC wrapper directly at embedded ZIP-name offset 59,908;
- writes `/mnt/sda1/CLASSIC` and the ZIP basename into the two globals expected by the hardware-proven Test12 frontend;
- loads exact archived Test12 MAME2000 core to `0x87000000`;
- uses the proven sound-task stop, RAMSIZE ceiling, IRQ-GP repair and cache handoff;
- enters Test12 core;
- restores RAMSIZE and frontend path globals after return.

Exact Test12 core remains:

```text
abf8e4ec6eb7c6d4c2162076e8faa868954a3663b8210c820e1267857b345461
```

## CLASSIC resource plumbing

List11 metadata filenames and dedicated artwork filename are no longer stored in low mapper memory.

They are placed in the unused tail of the same verified scanner cave immediately after the 352-byte bootstrap.

List11 still owns:
- `clm.tax`
- `clm.nec`
- `clm.bvs`
- `clssic.r56`
- `/CLASSIC/`
- `/CLASSIC/bin/`

Current menu artwork from Test31 is preserved unchanged because hardware confirmed it visually acceptable.

## Protected byte guards

CI composition explicitly proved these golden ranges remained byte-identical:

```text
Mapper v19   0x800014a0..0x8000217f
SNES loader  0x80002230..0x8000277f
Audio OSD    0x80002780..0x80002fff
```

CI identities:

```text
bootstrap size        352 bytes
bootstrap SHA-256     40fc040c26d3dcdb261f4f4050565c674174271deee6499047fa486bdf6e42bc
second-stage size     1,947 bytes
second-stage SHA-256  1b413ad9048e166010bbf7f4bce9d406cb29b3c5d57900cc6763d13aa571b040
```

Private CI run:
`34309041289`

Artifact ID:
`10087703544`

## Final composed hardware package

```text
xgo-classic-test32-recovered-golden-safe.zip
size              7,551,351 bytes
ZIP SHA-256        4b4df70835ab90fbbb3e363ddb14cbf73f73379b1e926ab1879c7cb538d96d11
firmware SHA-256   55dca4ec9b35cd7d8afd66087c04ea5a6893aebad91c96af48c2a8e672a49bb8
second-stage SHA   1b413ad9048e166010bbf7f4bce9d406cb29b3c5d57900cc6763d13aa571b040
Test12 core SHA    abf8e4ec6eb7c6d4c2162076e8faa868954a3663b8210c820e1267857b345461
CLASSIC art SHA    f738809ed3a90dca41445d30cb9ff440cbf46008f9c8d67e7b37866fdcddd9e5
```

## Hardware gate

Order matters:

1. boot;
2. launch Contra or another NES game;
3. open pause menu;
4. confirm Resume/Quit/Load/Save are selectable and Mapper no longer leaks into the normal menu;
5. verify stock Arcade Cadillacs remains golden;
6. launch Cadillacs and Dinosaurs from CLASSIC;
7. only if that works, test Pac-Man and Ms Pac-Man.

If the protected pause menu is still wrong, stop immediately and do not test CLASSIC.
