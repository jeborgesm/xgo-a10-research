# XGO Multicore Port Feasibility

Status: **the SF2000 Multicore architecture is highly compatible in concept with XGO and is a substantially better near-term route to improved emulator cores than replacing the entire XGO firmware. A port requires retargeting stock-function/global addresses and XGO-specific runtime constants.**

## Major finding

SF2000 Multicore is not a complete alternative operating system or board firmware.

Its loader keeps the stock firmware running, intercepts a stock emulator launch path, loads a standalone libretro core binary from the SD card into RAM at:

```text
0x87000000
```

and then connects that external core to the stock firmware's existing frontend services:

```text
retro_video_refresh_cb
retro_audio_sample_batch_cb
retro_input_poll_cb
retro_input_state_cb
retro_environment_cb
run_emulator
```

This architecture is especially attractive for XGO because XGO-specific hardware support can remain in the vendor firmware while emulator cores can be replaced independently.

## Multicore loader behavior

Public `madcock/sf2000_multicore` source uses fake GBA-style launch names with the form:

```text
[corename];[rom filename].gba
```

When such a path is detected, it loads:

```text
/mnt/sda1/cores/<corename>/core_87000000
```

into RAM address:

```text
0x87000000
```

and resolves the real ROM as:

```text
/mnt/sda1/ROMS/<corename>/<rom filename>
```

The loaded core exposes the normal libretro API, which is wired directly to stock firmware callbacks before calling the stock `run_emulator()` loop.

Therefore the external core supplies emulation logic while the stock firmware still supplies:

- display output;
- audio output;
- controller polling;
- controller state callbacks;
- SD-card/filesystem services;
- emulator run-loop integration;
- board initialization already completed before the core is loaded.

## Why this fits XGO unusually well

The hardest part of a fully new XGO firmware is not emulator code. It is reproducing all board-specific platform behavior correctly:

```text
ST7789V MCU8080 LCD path
640x480 logical frontend -> 320x240 panel scaling
TV/LCD route GPIO
battery SAR ADC initialization and thresholds
single-button volume behavior
SDIO configuration
XGO dual-DATA Player-2 scanner
Handle Interface electrical behavior
XGO-specific resource/front-end layout
```

A Multicore port can leave all of those mechanisms in the already-working XGO `bisrv.asd`.

Only the emulator core is replaced at runtime.

## XGO already supplies the critical two-player callback

Recent XGO disassembly confirms that the stock XGO libretro input callback at approximately:

```text
0x8035eb20
```

accepts `port < 2` and selects from a two-player mapped-state array.

Thus an external Multicore libretro core would inherit the XGO's already-confirmed Player-2 software path rather than requiring separate controller support in the loader.

## Stock global pointer is a known required port change

SF2000 Multicore explicitly contains a helper named `restore_stock_gp()` because dynamically generated emulator code may leave `$gp` changed when an interrupt occurs.

The SF2000 implementation hardcodes:

```text
$gp = 0x80c114f4
```

We independently recovered the XGO startup code and confirmed:

```text
$gp = 0x80c34774
```

Therefore an XGO Multicore build must change the restore helper to:

```text
lui    $gp, 0x80c3
addiu  $gp, $gp, 0x4774
```

This is no longer an unknown porting parameter.

## Why existing SF2000 Multicore binaries must not be used directly

Multicore is tightly linked against stock firmware addresses through `stockfw.h` / linker-script symbols.

Known SF2000 symbols include fixed addresses for:

```text
filesystem functions
malloc/free/memcpy/etc.
cache helpers
OS delay/tick functions
video callbacks
screen-write path
audio callback
input callbacks
run_emulator
run_gba
keymap state
global buffers/state variables
```

XGO comparison has already proved that address relocation is **piecewise**, not one global offset.

Examples:

```text
libc block       XGO shift about +0x634c
other blocks     different shifts
$gp/data layout  SF2000 -> XGO shift +0x23280
```

Therefore applying one arithmetic delta to the SF2000 linker map would be unsafe.

The port must use the XGO symbol map being reconstructed function by function.

## What is already mapped enough to help the port

The research now has confirmed or strongly anchored XGO addresses for several Multicore dependencies, including:

```text
malloc          0x80291c04
free            0x80292814
memcpy          0x8029496c
memset          0x80294b9c
printf          0x802947c0
strlen          0x80294e30

screen-write path around 0x8035c398
Player-2-aware input callback 0x8035eb20
XGO global pointer             0x80c34774
```

Additional stock imports still need exact XGO addresses before a safe Multicore build can be attempted.

## Strategic consequence

There are now three distinct modification tiers:

```text
Tier 1 — card configuration
  main game lists
  thumbnails/wrappers
  favorites/history
  per-game .kmp button mappings

Tier 2 — stock-firmware enhancement
  small patches to XGO bisrv.asd
  LCFG CRC reseal
  Multicore loader retargeted to XGO
  external upgraded libretro cores

Tier 3 — complete replacement firmware
  UniFrog/HCRTOS-style board port
  reimplement all board initialization
  potentially replace the full vendor frontend
```

For the stated goals, Tier 2 may deliver most of the desired functionality with substantially lower board-bring-up risk than Tier 3.

## Practical target

A realistic high-value XGO enhancement path is:

```text
stock XGO boot + board init
        |
        v
patched/resealed XGO bisrv.asd
        |
        +-- original built-in cores still available
        |
        +-- XGO-port of Multicore loader
                 |
                 +-- load newer libretro cores from SD
                 +-- use XGO stock video/audio/input
                 +-- retain Player 2 path
```

This would allow emulator experimentation without sacrificing the currently working XGO hardware support.

## Confidence

### CONFIRMED

- public SF2000 Multicore dynamically loads external core binaries to `0x87000000`;
- it uses stock firmware callbacks/services rather than replacing the entire board firmware;
- it requires fixed stock symbol/global addresses;
- it explicitly restores the stock `$gp` during interrupt-sensitive operation;
- XGO `$gp` is independently known as `0x80c34774`;
- XGO's input callback supports libretro ports 0 and 1;
- XGO address shifts are piecewise, so stock SF2000 Multicore binaries/linker maps cannot be used unchanged.

### STRONG CONCLUSION

Retargeting Multicore to XGO is likely a more practical route to improved/stable emulator cores than writing a complete replacement firmware first.

### OPEN

- exact XGO addresses for every symbol imported by Multicore;
- exact hook/call site used to redirect XGO's GBA launcher into the Multicore loader;
- whether `0x87000000` is equally safe/free on the XGO memory layout;
- core-by-core RAM requirements on XGO;
- save-state integration, since upstream Multicore currently stubs some state operations;
- whether XGO's audio timing requires core-specific adjustments beyond the stock SF2000 Multicore assumptions.
