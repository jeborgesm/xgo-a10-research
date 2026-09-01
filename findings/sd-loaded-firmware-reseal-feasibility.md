# XGO SD-Loaded Firmware Reseal Feasibility

Status: **XGO `bisrv.asd` integrity fields are reproducible exactly; public SF2000-family boot reconstruction shows the corresponding bootloader check is CRC32/MPEG-2 rather than a cryptographic signature. Exact XGO bootloader authentication behavior remains to be proven from an internal-flash dump.**

## Why this matters

For a practical custom-firmware path, the key distinction is:

```text
cryptographically signed image
    -> modifying firmware requires a vendor private key or a boot-chain exploit

integrity-checked image
    -> modified image can potentially boot after recomputing public checksum fields
```

The XGO evidence is currently much closer to the second model.

## Confirmed XGO LCFG integrity fields

The preserved XGO `bios/bisrv.asd` is:

```text
file size             12,768,452 bytes
LCFG header size      0x200 bytes
payload size          12,767,940 bytes = 0x00c2d2c4
payload CRC32/MPEG-2  0x5ee51f11
```

The image stores:

```text
0x184  0x00c2d2c4  little-endian payload size
0x18c  0x5ee51f11  little-endian CRC-32/MPEG-2
```

Recomputing the CRC independently over every byte from file offset `0x200` through EOF produces exactly:

```text
0x5ee51f11
```

Rewriting the size and CRC fields with independently generated values while leaving the payload unchanged produces a **byte-identical copy of the shipped XGO image**.

This confirms that the sealing algorithm is understood exactly for these fields.

## Public family boot-chain evidence

FrogQEMU's reconstructed SF2000 boot path explicitly reports that the bootloader reads `BISRV.ASD` and requires the CRC32/MPEG-2 check to pass before entering the stock application.

The public `sf2000_hcrtos` build tool creates `bisrv.asd` by:

1. reserving a 0x200-byte LCFG header;
2. writing `LCFG` magic;
3. storing payload length at `0x184`;
4. calculating CRC-32/MPEG-2 over the payload;
5. storing the CRC at `0x18c`.

That builder does not add an RSA/ECDSA/public-key signature to the generated image.

The XGO uses the same header offsets and the same CRC algorithm, giving strong evidence that its SD-loaded application belongs to the same non-cryptographic image-container design.

## Important confidence boundary

We have **not yet dumped the XGO's internal bootloader**.

Therefore the strongest defensible statement is:

### CONFIRMED

- the XGO application image has reproducible public size/CRC integrity fields;
- no cryptographic signature field has been identified in the XGO LCFG image;
- the corresponding open SF2000-family boot reconstruction validates CRC32/MPEG-2 and successfully boots rebuilt images using that scheme;
- an unchanged XGO image can be independently resealed to a byte-identical result.

### STRONG EVIDENCE

- small, carefully controlled modifications to the SD-loaded XGO `bisrv.asd` should be bootable after recomputing the LCFG integrity fields, provided no unobserved XGO-specific bootloader check exists.

### NOT YET PROVEN

- that the exact XGO internal bootloader has no extra board-specific authentication or secondary checksum;
- that an arbitrary rebuilt application satisfying LCFG CRC will initialize all XGO hardware correctly;
- that boot failure always leaves the device recoverable without restoring the SD card.

## Practical development consequence

The safest firmware-modification ladder is now:

```text
1. modify only SD-card resources/configuration
2. patch one behavior in a COPY of stock XGO bisrv.asd
3. reseal LCFG size + CRC
4. test from a disposable/recoverable SD card
5. preserve original bisrv.asd and original card
6. do NOT use Firmware.upk for these experiments
7. only later consider a fully rebuilt replacement application
8. only after flash-map recovery consider touching internal SPI-NOR
```

This avoids conflating the comparatively recoverable SD-loaded application with the dangerous automatic SPI-NOR updater.

## New repository tool

`tools/reseal_lcfg.py` implements the confirmed sealing operation without flashing anything.

It:

- validates `LCFG` magic;
- recalculates `file_size - 0x200`;
- calculates CRC-32/MPEG-2 over `0x200..EOF`;
- writes those values to `0x184` and `0x18c` in an output copy;
- refuses in-place modification.

The preserved stock XGO image passes the tool with both original fields already valid.

## Relevance to a future PC application

This is one building block for an XGO configuration/firmware utility. A future desktop application can safely operate on copies of the SD card and provide separate levels of modification:

```text
Low risk:
  edit game indexes
  edit per-game .kmp mappings
  edit settings/resources

Intermediate:
  patch known stock bisrv.asd behaviors
  automatically reseal LCFG CRC
  verify expected firmware hash/version before patching

High risk / future only:
  construct Firmware.upk
  write internal SPI-NOR
```

Keeping these tiers separate should be a design requirement rather than exposing all operations behind one generic "update firmware" button.
