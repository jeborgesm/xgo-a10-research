# XGO LCFG Runtime Board Configuration

Status: **runtime LCFG-header copy and LCD selector source confirmed; XGO selector byte recovered directly from the shipped `bisrv.asd`.**

## Major finding

The XGO firmware does not obtain the LCD `cur_type` selector from an opaque hardware probe. It copies the relevant configuration bytes directly from the relocated LCFG application header.

Public SF2000 boot-chain reconstruction places the relocated application header at:

```text
lcfg_header = 0x80f00000
image_start = 0x80000200
```

This matches the XGO application's own behavior.

## XGO runtime copy

Function `0x801ba8b8` performs:

```text
destination = 0x80c343b0
source      = 0x80f00004
length      = 0x8c
memcpy(destination, source, length)
```

`0x801ba8ac` simply returns the destination pointer `0x80c343b0`.

The copy is executed during system initialization at `0x801ba938`.

Because the source begins four bytes after `0x80f00000`, it skips the ASCII `LCFG` magic and preserves the following 0x8c bytes as the application's runtime configuration/header structure.

## LCD selector comes from this copied header

Function `0x801b686c`, whose diagnostics are from `board.c`, obtains the runtime pointer through `0x801ba8ac` and reads:

```text
cur_type = *(uint8_t *)(config + 0x6e)
```

It prints:

```text
cur_type=%d
```

and dispatches through a 27-entry table.

Since the runtime structure begins from file offset `0x04`, runtime offset `+0x6e` maps exactly to ASD file offset:

```text
0x04 + 0x6e = 0x72
```

The shipped XGO `bisrv.asd` contains:

```text
file offset 0x70: 01 00 00 00 e0 01 10 01 1f 00 0a 00 2d 00 0a 00
                       ^
file offset 0x72 = 00
```

Therefore the XGO's LCFG-supplied `cur_type` value is:

```text
cur_type = 0
```

This is **CONFIRMED directly from the executable and its shipped LCFG header**.

## Why `cur_type = 0` does not contradict the ST7789V finding

The `board.c` dispatcher contains inherited cases for many optional LCD routes, including strings such as:

```text
LCD_TYPE_SPI_480_800_HSD_35510
LCD_TYPE_SPI_480_854_045LA
LCD_TYPE_SPI_480_854_BYF50
LCD_TYPE_HS450_480_854
LCD_TYPE_SPI_480_800_ZR038
```

For selector 0, the dispatch table falls through without one of those optional SPI-panel setup branches.

Separately, the XGO application initialization function around `0x801b8ab4` **unconditionally calls `0x801b66d8` at `0x801b8b48`**. That routine carries the diagnostic:

```text
LCD_TYPE_ST7789V_MCU8080
```

and builds the MCU-8080 LCD pin/interface configuration passed into the LCD subsystem. The later driver-registration path installs the recovered `ST7789V_80I` initialization callback and 320x240 command table documented separately.

Thus the current model is coherent:

```text
LCFG cur_type 0
    -> no optional SPI/480x8xx board.c branch
    -> standard/default MCU-8080 path remains active
    -> XGO root initialization explicitly configures ST7789V MCU8080
    -> ST7789V_80I driver executes 320x240 panel init table
```

This strengthens, rather than weakens, the conclusion that the XGO uses the default/standard ST7789V-style MCU-8080 route within this firmware build.

## LCFG header bytes relevant to future mapping

The first 0x90 bytes of the preserved XGO image are:

```text
0000: 4c 43 46 47 1a 1a 1a 1a 1a 1a 1a 1a 1a 1a 00 00
0010: 00 00 00 00 03 18 1e 00 6c 6f 67 6f 2e 6d 32 76
0020: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
0030: 00 00 00 00 00 00 00 00 00 00 00 00 00 32 32 32
0040: 32 5a 00 00 00 00 00 00 00 00 00 00 00 00 00 00
0050: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
0060: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
0070: 01 00 00 00 e0 01 10 01 1f 00 0a 00 2d 00 0a 00
0080: 03 00 10 00 00 00 00 00 00 00 01 00 00 00 00 00
```

Only fields demonstrated by executable consumers should be assigned semantics. `0x72 = cur_type` is now one such field. Other values remain candidates for future structure recovery rather than assumptions.

## Additional root/display confirmation

The root/application initialization around `0x801b8ab4` also allocates:

```text
0x96004 bytes
```

and clears exactly:

```text
0x96000 = 640 * 480 * 2
```

It then calls the XGO screen-write path at `0x8035c398` with:

```text
buffer
width  = 0x280 = 640
height = 0x1e0 = 480
pitch  = 0x500 = 1280 bytes
```

This is direct executable confirmation that the launcher/root application uses a 640x480 RGB565 logical framebuffer before the display engine scales it to the 320x240 ST7789V panel address window.

## Confidence

### CONFIRMED

- SF2000-family boot reconstruction relocates `lcfg_header` to `0x80f00000`;
- XGO copies 0x8c bytes from `0x80f00004` into runtime RAM at `0x80c343b0`;
- copy occurs during XGO system initialization;
- `board.c` LCD selector reads runtime offset `+0x6e`;
- this maps to shipped ASD file offset `0x72`;
- XGO byte at file offset `0x72` is `0x00`, so `cur_type = 0`;
- root initialization directly calls the ST7789V MCU8080 setup routine;
- root allocates and submits a 640x480 RGB565 logical screen buffer.

### STRONG EVIDENCE

- selector 0 represents the default/non-optional LCD board path in this build, while the explicit ST7789V MCU8080 initialization supplies the XGO's active panel route;
- the 480x800/480x854 strings belong to inherited alternate-board cases and should not be interpreted as XGO native geometry.

### OPEN

- semantic names for the remaining LCFG configuration/header fields;
- whether sibling X60/DY19/Q19 builds use different values at the same `0x72` selector position;
- exact bootloader code that copies/relocates the LCFG header to `0x80f00000` on XGO hardware.
