# Native SNES Core #2 — exact stock ASD patch fingerprint

Status: **OFFLINE PATCH REPRODUCED AGAINST THE PRESERVED PHYSICAL-CARD FIRMWARE**

## Inputs

Preserved XGO stock firmware:

```text
bytes       12,768,452
SHA-256     869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf
```

Canonical injected loader from successful GitHub Actions run `33836747646`:

```text
bytes       1,359
SHA-256     35b05a11d00565493210698d245c1c54d965c08ec3cfb461c00b07e0781cade4
```

Canonical external core:

```text
core-snes9x2005.xgc
SHA-256     ee694b5989e1d056f73de99a47588f124caa2df9b5e8c751862c92adb7a543bf
```

## Independent local verification

Before patching, the preserved stock image was independently checked for:

- exact stock SHA-256;
- the complete family-`0x08` / 11025-Hz `run_emulator()` instruction sequence;
- an all-zero `0x1500..0x217f` loader cave;
- exact stock SNES dispatch bytes at ASD `0x00360e40`:

```text
76 7e 0d 0c    jal 0x8035f9d8
```

The exact CI-produced 1,359-byte loader was then inserted into the cave and the SNES dispatch changed to:

```text
40 05 00 0c    jal 0x80001500
```

LCFG CRC-32/MPEG-2 was recalculated over the unchanged-size payload.

## Canonical patched ASD

```text
payload size       0x00c2d2c4
payload CRC        0xc03ba3b0
patched SHA-256    d26951d932dc4788b5a5e95ed162c9d89d73dfe5e0b9cb757192aff755e1654f
```

Byte-diff audit:

```text
unexpected changed bytes = 0
```

The only permitted mutation regions were:

1. injected loader bytes within `0x1500..0x217f`;
2. SNES runner JAL at `0x00360e40..0x00360e43`;
3. LCFG CRC field at `0x018c..0x018f`.

The LCFG payload size field did not change because the patch does not alter file length.

## Meaning

The complete offline chain is now deterministic:

```text
exact preserved XGO stock ASD
  + exact 1,359-byte GP-free SNES loader
  + one exact SNES dispatch redirect
  + LCFG reseal
  =
patched ASD SHA-256
d26951d932dc4788b5a5e95ed162c9d89d73dfe5e0b9cb757192aff755e1654f
```

Together with:

```text
/cores/snes9x2005/core.xgc
ee694b5989e1d056f73de99a47588f124caa2df9b5e8c751862c92adb7a543bf
```

this defines the first exact Core #2 hardware candidate.

## Safety boundary

This path modifies only files on a disposable SD-card clone. It does not create or install `Firmware.upk`, does not write SPI NOR, and retains automatic stock-SNES fallback in the injected loader for validation/open/CRC/bounds failures.

## Remaining evidence

At this point the unresolved question is no longer static architecture or package reproducibility.

The next decisive evidence is physical hardware behavior:

- does external Snes9x2005 reach `retro_load_game()` and gameplay;
- does the stock 11025-Hz audio path behave correctly;
- does stock RGB565 scaling preserve geometry/colors;
- do P1/P2 controls work;
- does Select+Start return to the stock save UI;
- do generic save/load states work with the larger SNES serializer;
- and, most importantly, is real SNES frame pacing materially better than the embedded 2016-era core.
