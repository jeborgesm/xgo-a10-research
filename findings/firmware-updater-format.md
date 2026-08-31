# XGO `Firmware.upk` Updater — Static Reverse Engineering

Status: **update entry path and outer container signature confirmed; flash operation is dangerous and remains analysis-only**.

## Entry point

The XGO startup path directly references:

```text
/mnt/sda1/UpdateFirmware/Firmware.upk
```

At approximately `0x80355bb4`, the frontend checks for the package during startup. If present, control reaches the updater routine at approximately `0x8035bca8`.

This is an **automatic startup updater**. It is not an option exposed through the normal XGO menu.

## File open mode

The updater opens the package with:

```text
r+b
```

so it requests binary read/write access rather than a read-only stream.

## Outer magic is `WQW`

The updater reads exactly the first three bytes and validates them explicitly:

```text
byte 0 == 0x57   // 'W'
byte 1 == 0x51   // 'Q'
byte 2 == byte 0 // 'W'
```

Therefore a valid outer package begins:

```text
57 51 57
 W  Q  W
```

If this check fails, firmware emits:

```text
%s format error!
```

This is executable validation, not merely a string inference.

## `WQW` + ZIP lineage

Public reverse engineering of closely related Data Frog updater implementations independently reports that their `Firmware.upk` format is made by prepending the three bytes `WQW` to a ZIP archive and renaming the result `Firmware.upk`.

The XGO's executable three-byte check is an exact match for that mechanism. The updater then hands the stream to a substantial archive-processing library and uses entry-oriented open/read/close functions before performing flash writes.

Thus the current XGO conclusion is:

**CONFIRMED:** XGO requires the `WQW` three-byte outer signature.

**VERY STRONG EVIDENCE:** the payload after that signature is the same ZIP-derived update container family used by related Data Frog/H1512 products.

A benign future analysis can confirm the internal ZIP header and entry names from a known-compatible XGO update package if one is ever recovered; no package should be fabricated for execution merely from this finding.

## Updater working structures

After the signature check, the updater:

1. allocates a `0x10000` / 64 KiB working buffer;
2. clears an approximately `0x130`-byte metadata structure;
3. opens/parses the update archive through a library wrapper;
4. obtains payload/archive metadata;
5. compares the payload size with the available flash limit;
6. allocates/uses a payload buffer;
7. reads archive data in chunks;
8. compares data before/after flash operations;
9. retries verification/write operations up to three times in relevant failure paths;
10. reports success or failure on screen/log output.

The updater explicitly contains the error:

```text
File size over flash memory!
```

which is reached after comparing parsed payload size against a firmware-maintained flash-capacity value.

## Flash write and verification behavior

The updater calls lower-level SPI-NOR helpers already identified elsewhere in the firmware. Nearby diagnostic strings include:

```text
spi_nor_cmd_read
spi_nor_cmd_write
NOR flash id_buf[0]=...
STO_SFLASH_0
```

The high-level update loop processes the image in chunks no larger than `0x10000` bytes and performs byte-for-byte comparison of read/working buffers. The verification path can retry failed sectors/chunks rather than simply issuing one blind write.

The final user-visible states are:

```text
Update success.
Update fail.
Alloc memory fail!
```

On success the firmware also calls a follow-up routine after displaying/logging success, consistent with finalization/restart/UI transition.

## Why this matters

This establishes that the XGO has **two very different firmware mechanisms**:

```text
bios/bisrv.asd
    SD-loaded executable/application firmware
    changing it does not inherently require SPI-NOR flashing

UpdateFirmware/Firmware.upk
    automatic startup package
    explicitly enters SPI-NOR update machinery
    can permanently alter internal flash
```

The distinction is important for future custom-firmware experimentation. Testing an alternate SD-loaded `bisrv.asd` on a disposable card is materially different from placing a `Firmware.upk` on the card.

## Safety conclusion

Do **not** place a generic SF2000, GB300, Y2, or other Data Frog `Firmware.upk` on the XGO merely because the package signature and updater lineage match.

A public report from a related Data Frog product explicitly warns that mismatched board/flash revisions can require recovery with an external programmer. The `WQW` wrapper establishes container-family compatibility, not board-image compatibility.

For XGO research, `Firmware.upk` should remain **analysis-only** unless an original package for the exact XGO board is recovered and its target ranges are understood.

## Confidence

### CONFIRMED from XGO executable code

- startup path `/mnt/sda1/UpdateFirmware/Firmware.upk`;
- automatic update entry;
- package opened as `r+b`;
- exact three-byte outer signature `WQW`;
- explicit format rejection;
- flash-size bound check;
- use of chunked payload processing;
- SPI-NOR update/verification path;
- success/failure reporting;
- retry logic exists in the verification/write loop.

### VERY STRONG EVIDENCE

- XGO belongs to the same `WQW`-prefixed ZIP updater-container family documented on related Data Frog products.

### OPEN

- exact ZIP entry filename(s) expected by the XGO parser;
- internal image/header metadata beyond the outer `WQW` bytes;
- exact SPI-NOR address ranges written by an XGO-compatible package;
- whether XGO's internal flash contains only bootstrap/configuration or additional board-specific data that must be preserved;
- whether the updater modifies the package/file during processing, explaining the `r+b` open mode.