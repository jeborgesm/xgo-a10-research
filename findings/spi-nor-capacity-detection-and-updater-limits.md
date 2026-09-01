# XGO SPI-NOR Capacity Detection and Updater Limits

Status: **JEDEC-ID capacity decoding and updater capacity bound are confirmed from executable code.**

## Major finding

The XGO updater does not assume one fixed SPI-NOR size. It reads the flash JEDEC ID and derives the available flash capacity from the JEDEC capacity byte before accepting an update payload.

This is important for future firmware replacement work because the automatic `Firmware.upk` path enforces the detected flash size rather than blindly writing an arbitrary package.

## Flash-identification routine

Function `0x8035b5d8` obtains the SPI-NOR identification value and first accepts manufacturer/device-family low bytes including:

```text
0xB3
0x20
```

It then masks the returned identifier with:

```text
id & 0x00ff0000
```

and dispatches on the JEDEC capacity-code byte.

The resulting XGO capacity table is:

```text
JEDEC capacity field   XGO stored flash capacity
0x13xxxx                0x00800000 =  8 MiB
0x14xxxx                0x01000000 = 16 MiB
0x15xxxx                0x02000000 = 32 MiB
0x16xxxx                0x04000000 = 64 MiB
```

The derived capacity is stored at:

```text
gp - 0x5f4c = 0x80c2e828
```

with the recovered XGO global pointer:

```text
$gp = 0x80c34774
```

## Exact executable branches

Relevant code in `0x8035b798..0x8035b7cc` performs the equivalent of:

```c
switch (jedec_id & 0x00ff0000) {
    case 0x00160000: flash_capacity = 0x04000000; break;
    case 0x00150000: flash_capacity = 0x02000000; break;
    case 0x00140000: flash_capacity = 0x01000000; break;
    case 0x00130000: flash_capacity = 0x00800000; break;
}
```

This matches the standard JEDEC convention in which the capacity code encodes progressively larger power-of-two flash devices.

## Relationship to Firmware.upk

The high-level updater at `0x8035bca8` parses the update container, obtains its payload size, and compares that size against the detected flash capacity.

The bound check occurs around:

```text
0x8035bdcc..0x8035bde4
```

using:

```text
flash_capacity = *(gp - 0x5f4c)
```

If the package exceeds the detected flash size, the updater reaches the diagnostic:

```text
File size over flash memory!
```

Therefore the package-size limit is tied to live JEDEC identification rather than a compile-time XGO-only constant.

## Low-level write granularity

The updater's verification/write loop uses:

```text
0x10000-byte = 64 KiB chunks
```

for the main data path.

A later erase/finalization helper is invoked with:

```text
0x2000 = 8 KiB
```

and a `0x100`-byte pattern buffer is prepared with `0xff`, indicating that multiple lower-level granularities exist beneath the 64 KiB package loop.

The exact semantic distinction between erase sector size, page/program unit, and updater bookkeeping remains to be named from the lower storage driver.

## Important limitation

This code proves the updater can recognize flash capacities from 8 to 64 MiB, but it does **not** yet prove which capacity is physically installed in the preserved XGO unit because the JEDEC ID is read at runtime.

The original SD-card backup does not contain a dump of the internal SPI-NOR from which the physical capacity can be recovered directly.

A future non-destructive runtime diagnostic or hardware read of the JEDEC ID would resolve the exact installed part.

## Firmware-replacement consequence

The emerging boot model is now:

```text
internal SPI-NOR
    bootloader / board bootstrap / possibly persistent platform data
           |
           v
SD card bios/bisrv.asd
    main application + emulator cores + frontend
```

and separately:

```text
UpdateFirmware/Firmware.upk
    -> parse WQW/ZIP package
    -> read JEDEC flash ID
    -> derive 8/16/32/64 MiB capacity
    -> reject oversized payload
    -> erase/write/verify internal SPI-NOR
```

This reinforces a crucial development strategy: **early custom-firmware work should prefer replacing or patching the SD-loaded `bisrv.asd` while leaving the internal SPI-NOR untouched.** The automatic `.upk` updater should remain reserved for later research after the internal flash map is fully understood.

## Confidence

### CONFIRMED

- runtime SPI-NOR identification occurs before updater operation;
- JEDEC capacity codes `0x13`, `0x14`, `0x15`, `0x16` map to 8, 16, 32 and 64 MiB respectively;
- derived capacity is stored at `0x80c2e828`;
- the updater compares parsed payload size against that capacity;
- oversized packages are explicitly rejected;
- the primary update loop operates in chunks no larger than 64 KiB.

### OPEN

- exact SPI-NOR manufacturer/model installed in the XGO unit;
- exact physical flash capacity of the preserved unit;
- full partition/address map of internal SPI-NOR;
- which regions contain immutable bootloader versus writable firmware/configuration;
- exact meanings of the 8 KiB and 256-byte lower-level updater operations;
- whether an original XGO `.upk` writes the whole flash or only selected regions.
