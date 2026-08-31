# Per-Game Keymap Runtime Behavior

Status: **loader, compiler, pause-time writer, and persistence constraints reconstructed from executable code**.

## Active per-game format

The XGO retains the older SF2000-family per-ROM mapping path:

```text
%s/save/%s.kmp
```

The launcher reads exactly 12 little-endian 32-bit records = 48 bytes.

The canonical physical record order for ordinary systems is:

```text
P1: X, Y, L, A, B, R
P2: X, Y, L, A, B, R
```

Each record uses:

```text
bits 0..15  logical emulator-button selector
bit 16      autofire/turbo flag
```

In byte-oriented form, common selector records are therefore:

```text
B       00 00 00 00
R/C     01 00 00 00
A       08 00 00 00
L/Z     09 00 00 00
X/C     0A 00 00 00
Y/D     0B 00 00 00
```

The exact logical meaning of selectors `01/09/0A/0B` depends on the emulator family. Setting turbo adds `01` in byte 2, e.g. turbo-A is `08 00 01 00`.

## Important pause-menu discovery: the writer is live even though the editor is gone

The keymap persistence function at `0x80353fac` has three direct callers inside the ordinary `SELECT+START` pause-menu function:

```text
0x80355808
0x8035588c
0x80355924
```

The top-level pause action dispatcher at `0x80355180` maps state 0/1/2/3 to the four visible menu actions. In particular, state 0 and state 1 enter paths that invoke the keymap writer before returning/resuming or exiting, while another save/load path also invokes it.

This resolves an apparent contradiction:

- the on-device remapping editor page is gone/unreachable;
- the per-game `.kmp` writer is still executable because pause/transition code still uses the persistence helper.

## P2 mappings are forcibly synchronized to P1 before persistence

Before writing, `0x80353fac` compares the six P1 records with their corresponding P2 records through permutation table `0x808dd2e0`:

```text
02 01 00 05 04 03 08 07 06 0B 0A 09
```

The effective compared pairs are:

```text
P1 record 2 <-> P2 record 8
P1 record 1 <-> P2 record 7
P1 record 0 <-> P2 record 6
P1 record 5 <-> P2 record 11
P1 record 4 <-> P2 record 10
P1 record 3 <-> P2 record 9
```

If a corresponding P2 value differs, firmware copies the P1 value over it. Only if at least one mismatch existed does the routine compile and write the 48-byte `.kmp` file.

**Practical consequence:** a hand-created XGO `.kmp` should use matching P1 and P2 halves unless there is a specific reason to study this synchronization behavior. Distinct P2 mappings are liable to be overwritten by ordinary pause-menu activity.

## Safe byte-level example: SNES A/B swap

For SNES/SFC, the normal six physical records are:

```text
physical X -> logical X = 0A 00 00 00
physical Y -> logical Y = 0B 00 00 00
physical L -> logical L = 09 00 00 00
physical A -> logical A = 08 00 00 00
physical B -> logical B = 00 00 00 00
physical R -> logical R = 01 00 00 00
```

A simple physical A/B swap, with P1 and P2 identical, would therefore be:

```text
0A 00 00 00
0B 00 00 00
09 00 00 00
00 00 00 00   # physical A -> logical B
08 00 00 00   # physical B -> logical A
01 00 00 00

0A 00 00 00
0B 00 00 00
09 00 00 00
00 00 00 00
08 00 00 00
01 00 00 00
```

Concatenated, this is exactly 48 bytes.

The expected filename follows the older SF2000 convention and includes the ROM filename/extension, for example conceptually:

```text
<SFC-folder>/save/Game Name.sfc.kmp
```

The XGO launcher itself confirms the `%s/save/%s.kmp` construction. Exact path casing and the ROM-name string supplied by each XGO list source should be preserved literally when testing.

## Emulator selector meanings

Community work on the same firmware family aligns with the XGO compiler values:

```text
NES/FC:  08=A, 00=B, 0A=FDS turn disk, 0B=FDS eject/insert
SNES:    08=A, 00=B, 0A=X, 0B=Y, 09=L, 01=R
MD:      08=A, 00=B, 0A=X, 0B=Y, 01=C, 09=Z
SMS:     00=button 1, 01=button 2
GBA:     08=A, 00=B, 0A=L, 0B=R
GB/GBC:  08=A, 00=B
FBA:     08=A, 00=B, 0A=C, 0B=D
```

The XGO embedded fallback tables independently use the same selector set and special GBA arrangement, providing firmware-side corroboration rather than relying solely on inherited documentation.

## Current recommendation

For stock-firmware remapping experiments, the least invasive path is:

1. preserve the original SD image;
2. use a copied/test card or backed-up save directory;
3. create a 48-byte `.kmp` for one known ROM;
4. keep P1/P2 halves identical;
5. begin with an obvious reversible mapping such as SNES A/B swap;
6. remove the `.kmp` to restore the embedded default.

This does not replace `bisrv.asd`, invoke the SPI-NOR updater, or modify internal flash.
