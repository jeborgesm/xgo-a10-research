# XGO GBA BIOS Identification

Status: **the preserved XGO card contains the canonical 16 KiB Nintendo GBA BIOS image, confirmed by cryptographic hash.**

## Major finding

The XGO card contains:

```text
bios/gba_bios.bin
size: 16384 bytes
```

The file hashes are:

```text
SHA-1  300c20df6731a33952ded8c436f7f186d25d3492
MD5    a860e8c0b6d573d191e4ec7db1b1e4f6
SHA-256 fd2547724b505f487e6dcb29ec2ecff3af35a841a77ab2e85fd87350abd36570
```

The SHA-1 `300c20df6731a33952ded8c436f7f186d25d3492` is the widely documented canonical hash for the original Game Boy Advance BIOS image. Public emulator projects use the same 16 KiB size and SHA-1 as their expected reference.

Therefore the XGO file is not merely an approximate, replacement, or HLE-compatible BIOS image: it is **byte-identical to the canonical original GBA BIOS dump identified by that hash**.

## XGO gpSP path

The gpSP core embedded in `bisrv.asd` contains the absolute path:

```text
/mnt/sda1/bios/gba_bios.bin
```

alongside diagnostics:

```text
Could not load BIOS image file, using built-in BIOS
BIOS image seems incorrect, using built-in BIOS
```

and core options that distinguish:

```text
auto
builtin
official
```

The firmware therefore has both:

1. a built-in fallback BIOS implementation; and
2. an active path for loading an external official BIOS image from the SD card.

The shipped card supplies the canonical image at exactly that expected path.

## Practical implication

For preservation/reimplementation purposes, the vendor baseline for GBA emulation is not just the gpSP built-in BIOS fallback. The shipped software environment includes the external BIOS and can use it for compatibility-sensitive games.

A custom XGO firmware or clean-room SD-card reconstruction should treat the BIOS as an external user-supplied dependency rather than assume the built-in gpSP replacement perfectly reproduces the shipped behavior.

This finding is descriptive only and does not imply that copyrighted BIOS contents should be redistributed.

## Confidence

### CONFIRMED

- `gba_bios.bin` is exactly 16,384 bytes;
- its SHA-1 is `300c20df6731a33952ded8c436f7f186d25d3492`;
- public GBA emulator projects identify that exact size/hash as the expected canonical GBA BIOS;
- XGO gpSP hard-codes `/mnt/sda1/bios/gba_bios.bin`;
- XGO gpSP contains built-in fallback and incorrect/missing-BIOS handling.

### OPEN

- exact gpSP core-option selection used by the XGO frontend at runtime (`auto` vs explicit `official`), though the external BIOS is present and available;
- whether any shipped GBA title depends materially on behavior unique to the original BIOS rather than gpSP's fallback.
