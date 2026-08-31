# XGO LCD / Panel Initialization

Status: **ST7789V-family active initialization sequence recovered from executable code; physical controller package not yet electrically verified**.

## Major finding

The XGO firmware contains an ST7789V MCU-8080 style LCD driver registration path and an initialization table used by that driver. The relevant driver name string is:

```text
ST7789V_80I
```

The driver-registration wrapper at approximately `0x802a0ebc` registers the initialization callback at approximately `0x802a0dd4`. That callback directly accesses LCD control register `0xb8800094`, sets bit 16, and walks a packed command table at runtime address approximately `0x80a39604`.

The command-table format matches the HC15xx/SF2000 ST7789V driver format independently documented by the public `sf2000_hcrtos/tools/lcd.py` reverse-engineering utility: two-byte records distinguish command, data and millisecond-delay entries, terminated by `0xffff`.

## Recovered XGO initialization sequence

Decoded sequence:

```text
SLPOUT
wait 99 ms
MADCTL  A0
COLMOD  55
B1      40 04 14
B2      0C 0C 00 33 33
B7      71
BB      3B
C0      2C
C2      01
C3      13
C4      20
C6      0F
D0      A4 A1
D6      A1
E0      D0 06 06 0E 0D 06 2F 3A 47 08 15 14 2C 33
E1      D0 06 06 0E 0D 06 2F 3B 47 08 15 14 2C 33
CASET   00 00 01 3F
RASET   00 00 00 EF
INVON
DISPON
```

The most important geometry commands are:

```text
CASET 0x0000..0x013f = columns 0..319 = 320 pixels
RASET 0x0000..0x00ef = rows    0..239 = 240 pixels
```

`COLMOD 0x55` selects a 16-bit RGB565-style pixel interface for the controller. `MADCTL 0xA0` selects the vendor's panel orientation/order configuration.

## Resolution distinction

This resolves an important ambiguity in earlier findings:

- XGO frontend/application canvas: **640x480** RGB565.
- LCD controller addressable panel region initialized here: **320x240**.

Therefore the 640x480 logical frontend is scaled/downsampled by the display/video pipeline before reaching the physical 320x240 LCD. The many 640x480 resource images do not imply a 640x480 native panel.

## Why this matters for custom firmware

The active panel initialization had been one of the largest unknowns for an XGO-specific UniFrog/HC15xx port. We now have the exact controller command sequence used by the vendor firmware, including orientation, RGB565 mode, timing/power/gamma values, and native address window.

A future XGO board definition can reproduce this initialization rather than guessing from generic SF2000 display settings.

## Relationship to SF2000 tooling

The public `bnister/sf2000_hcrtos` `tools/lcd.py` utility specifically searches HC15xx firmware for the same ST7789V initialization code pattern:

```text
load 0xb8800094
set bit 16
load packed LCD initialization array
```

Applying that same documented structure to the XGO executable finds the sequence above at the expected code/data locations. This is strong independent validation that the recovered table is genuinely an ST7789V-family LCD initialization path rather than unrelated data.

## Confidence

### CONFIRMED from XGO executable code

- driver name string `ST7789V_80I` exists;
- driver registration references the recovered initialization callback;
- callback accesses `0xb8800094` and executes the packed initialization table;
- exact recovered command/data sequence;
- panel address window configured as 320x240;
- controller pixel format configured with `COLMOD 0x55`;
- inversion and display-on commands are issued.

### STRONG EVIDENCE

- the physical LCD controller is ST7789V or a command-compatible derivative using the same MCU-8080 style interface;
- the XGO native LCD is 320x240 and the 640x480 frontend framebuffer is scaled by the HC15xx display engine.

### OPEN

- exact physical panel module/model and controller silicon revision;
- exact LCD data/control GPIO pin assignment on the XGO board;
- backlight PWM/control pin;
- whether the controller is literally an ST7789V die or a compatible clone;
- exact display-engine scaling/filter configuration between the 640x480 frontend and 320x240 panel.