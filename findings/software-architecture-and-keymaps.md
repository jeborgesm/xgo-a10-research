# XGO Software Architecture and Keymap Findings

Status: **active executable paths confirmed; software architecture substantially reconstructed**.

## Scope

This note records a deeper static-analysis pass over the preserved XGO `bios/bisrv.asd` and microSD `Resources` tree. Runtime virtual addresses below use the full ASD image mapped at `0x80000000`, preserving the 0x200-byte LCFG header. This mapping reproduces the previously confirmed hidden `L + SELECT` comparison at `0x80356444`.

## Major finding: per-game `.kmp` loading is active

The XGO does not merely retain an obsolete `.kmp` filename string. Its executable game-launch path actively constructs, opens, reads, and applies a per-ROM keymap.

At `0x8035ed48` the loader prepares a path with the format string at `0x809a3418`:

```text
%s/save/%s.kmp
```

When the file exists, firmware reads exactly **12 items of 4 bytes = 48 bytes** into the working keymap buffer at `0x810a0f58`, closes it, and immediately invokes the mapping compiler at `0x8035e83c`.

This is a **CONFIRMED executable feature** in the XGO firmware.

### Exact 48-byte structure

Cross-checking the XGO mapping compiler against the public SF2000 button-mapping tool resolves the record layout:

```text
physical record order: X, Y, L, A, B, R
Player 1: 6 records x 4 bytes = 24 bytes
Player 2: 6 records x 4 bytes = 24 bytes
Total: 48 bytes
```

Each 4-byte little-endian record is effectively:

```text
byte 0 / low selector = emulator logical-button selector
byte 1                = normally zero
byte 2                = turbo/autofire flag (1 = enabled)
byte 3                = normally zero
```

The XGO compiler independently tests the low selector and bit `0x00010000`, matching this format exactly.

### Firmware also writes `.kmp` files

Function `0x80353fac` is an active persistence routine. It operates on the same working keymap at `0x810a0f58`, compiles it, constructs `%s/save/%s.kmp`, opens the target with `wb`, and writes exactly 12 x 4-byte records.

Before writing, the code compares six corresponding P1/P2 records through a permutation table at `0x808dd2e0`:

```text
02 01 00 05 04 03 08 07 06 0B 0A 09
```

The compared/copied pairs are:

```text
2 <-> 8
1 <-> 7
0 <-> 6
5 <-> 11
4 <-> 10
3 <-> 9
```

If corresponding P1/P2 entries differ, the persisted P2 side is made to mirror P1. This confirms that the XGO vendor retained writable per-game mapping machinery, while intentionally keeping the two players synchronized in persisted profiles.

## Default fallback maps

If the per-game `.kmp` cannot be opened, firmware selects one of six embedded 48-byte defaults according to the active emulator/system bitmask.

Exact native system IDs from the extension dispatcher are:

```text
0x01 = NES / Famicom
0x04 = Mega Drive / Genesis / Master System
0x08 = SNES / Super Famicom
0x10 = Game Boy Advance
0x20 = Game Boy / Game Boy Color / SGB
0x40 = Arcade / FBA
```

The embedded defaults, in physical `X,Y,L,A,B,R` order, are:

```text
Sega    [10,11, 9,8,0,1] x 2
SNES    [10,11, 9,8,0,1] x 2
GBA     [ 9, 1,10,8,0,11] x 2
Arcade  [10,11, 9,8,0,1] x 2
GB/GBC  [0x10008,0x10000,0x10000,8,0,0x10008] x 2
NES     [0x10008,0x10000,0x10000,8,0,0x10008] x 2
```

`0x10000` is the autofire bit, so the NES/GB-family defaults deliberately make several otherwise redundant physical buttons turbo duplicates of A/B.

## Exact ROM-extension dispatcher

Function `0x80360a08` searches a 40-entry table beginning at `0x80a3c4c8`, with 0x84 bytes per entry. Confirmed entries include:

```text
BKP, ZIP                     -> 0x00010000
ZFC, ZSF, ZMD, ZGB, ZFB      -> 0x00030000 wrapper/container path
SMC, FIG, SFC, GD3, GD7,
DX2, BSX, SWC                -> 0x00000008 SNES
NES, NFC, FDS, UNF           -> 0x00000001 NES
GBA, AGB, GBZ                -> 0x00000010 GBA
GBC, GB, SGB                 -> 0x00000020 GB/GBC
BIN, MD, SMD, GEN, SMS       -> 0x00000004 Sega
```

This yields two useful conclusions:

- `.sms` is genuinely routed to PicoDrive by the stock XGO frontend, so Master System is a native hidden/under-advertised format.
- PicoDrive itself contains 32X and Sega-CD support strings/options, but `.32x`, `.cue` and `.iso` are absent from the XGO frontend dispatch table. Those core capabilities are therefore **dormant behind the current frontend**, not stock-accessible formats.

The launcher also contains `%s/skp/%s.skp`, ZIP/decompression messages, compressed/uncompressed-size handling, and wrapper extensions `ZFC/ZSF/ZMD/ZGB/ZFB`. These are part of the SF2000-family packaged-ROM/container layer above the native emulator cores.

## The in-game menu is definitively four items

`SELECT + START` (`0x0009`) is the active in-game menu shortcut. Physical testing confirms the visible menu contains exactly:

```text
Resume
Quit
Load
Save
```

Static analysis agrees. The top-level menu state is hard-limited to `0..3`. Renderer `0x80354640` indexes four consecutive resource pointers beginning at `0x80a3c318`, corresponding to resource entries 32-35. Navigation logic prevents incrementing past state 3, and action dispatch only handles these four states.

### `gpapi.bvs` is a stranded fifth-page asset

Resource index 36 is `gpapi.bvs`. It decodes as a 640x480 RGB565 controller-layout screen with a D-pad, six physical-button positions and a selection marker. In the inherited SF2000 resource ordering it sits immediately after the four active in-game menu backgrounds.

However, the XGO renderer never reaches index 36: the state bound is four pages, and no alternate frontend reference selecting the fifth resource was found.

Therefore the current evidence is:

**CONFIRMED:** `gpapi.bvs` is present and is remapping-related artwork.

**CONFIRMED:** the shipped XGO in-game menu cannot select it through its current 0..3 state machine.

**STRONG EVIDENCE:** it is stranded/dead inherited artwork from an older SF2000 remapping page whose visible editor was removed or disconnected in this XGO fork.

Merely patching the menu bound from 3 to 4 would not be sufficient: the state-dependent action logic also only dispatches the existing four actions. Restoring an on-device editor would require reconstructing or recreating mapping-edit behavior.

## Hidden-combo inventory

A broader scan of the central translated P1 event state found two meaningful exact multi-button equality comparisons:

```text
L + SELECT      = 0x1001 -> launch Resources/Test.zsf
SELECT + START  = 0x0009 -> enter in-game save/load menu
```

Other central frontend uses are ordinary single-button masks or navigation logic. No third comparable hidden frontend shortcut has emerged from the known event variables.

Core-specific combinations/options can still exist inside individual emulators (for example FBA diagnostic-input handling), but they are distinct from XGO frontend hidden menus.

## CPU clock and SoC identity

The firmware now provides executable proof of both the SoC family and its configured clock target.

### H1512 chip-ID check

At `0x80274d24`, firmware reads MMIO `0xb8800000`, shifts the chip identifier and explicitly compares against `0x1512` / `0x15120` forms before allowing the clock getter to proceed. Failure reaches the SDK message `chip id does not match, get cpu clock failed!!!`.

This upgrades H1512 from a string-based inference to a direct executable hardware identity check.

### XGO configures the PLL for 810 MHz

Initialization function `0x802749c8` writes:

```text
0x812b0900 -> 0xb8800380
```

and configures related clock registers at `0xb8800074` and `0xb880007c`.

The companion clock getter at `0x80274b78` maps that exact PLL register value to:

```text
0x32a = 810 decimal
```

with adjacent known patterns mapping to 864 and 918.

Therefore the XGO firmware **deliberately programs the H1512 clock configuration that its own SDK reports as 810 MHz**. This is much stronger than a generic datasheet capability claim.

## Frontend framebuffer / logical resolution

Frontend initialization writes:

```text
gp - 0xe18 = 0x280 = 640
gp - 0xe1c = 0x1e0 = 480
```

This matches the many `614400`-byte resources exactly:

```text
640 x 480 x 2 bytes = RGB565
```

Thus the XGO frontend uses a **640x480 logical framebuffer/canvas**. The SDK contains many LCD controller drivers (ILI9341, ST7789V, ST7701S, NT35510, etc.), so those driver strings alone do not identify the physical panel controller.

## `Archive.sys` persistent-state format

`Resources/Archive.sys` is exactly 12 bytes / three little-endian 32-bit words. The shipped file is:

```text
00000000 00000000 00000021
```

Startup reads the three words into persistent frontend state.

The first word (`gp-0xd7c`) is used as a six-state `0..5` selector and wraps from 5 back to 0. It participates heavily in main-menu resource/list indexing, so it is a persistent primary frontend/category selection state.

The second word (`gp-0x5f40`) is a binary `0/1` toggle. The frontend flips it with `(value + 1) & 1`, persists `Archive.sys`, and calls a display/UI reconfiguration routine. Its exact user-facing meaning remains unresolved and should not yet be labeled.

The third word (`gp-0xd20`) is now identifiable as the **volume level**. Startup normalizes it to four milestones:

```text
0, 33, 66, 99
```

The controller task advances it by 33 and wraps after 99, then passes the value to the audio-setting helper. This matches the XGO's single `V+` hardware control: it cycles four persisted volume levels rather than exposing independent up/down controls.

## Core versions and capabilities

Embedded core fingerprints include:

```text
FCEUmm             git 7cdfc7e
Snes9x 2005        v1.36
PicoDrive          1.91 cbc93b6
gpSP               v0.91 261b2db
TGB Dual           v0.8.3 9be31d3
FB Alpha libretro  v0.2.97.42 621e371
```

Their compiled option surfaces are substantially richer than the XGO frontend exposes.

Examples include:

- FCEUmm: region, palette, sprite limit, overclock, overscan, turbo, aspect ratio.
- PicoDrive: 3/6-button input, region/FPS, sprite limit, Mega-CD RAM cart, aspect/overscan.
- gpSP: BIOS mode, frameskip modes, color correction, frame mixing, save method, turbo period, fast-forward.
- TGB Dual: GB link-cable emulation, screen layouts, player-screen switching and audio-source selection.
- FBA: diagnostic input, Neo Geo controls, DIP-switch mode, UNIBIOS/AES/MVS, hiscores, CPU-speed adjustment, L/R remapping and control-scheme options.

These are **core capabilities**, not proof that the stock XGO UI exposes them. They are nevertheless important targets for a future custom frontend or firmware.

## GBA BIOS path

The gpSP core contains a hard-coded absolute XGO/SF2000-family path:

```text
/mnt/sda1/bios/gba_bios.bin
```

alongside fallback messages for missing/incorrect BIOS images and an option description stating that a user-provided official BIOS gives best compatibility. The preserved XGO card contains a 16 KiB `bios/gba_bios.bin`, strongly indicating that the vendor intended gpSP to use an external official-compatible BIOS path rather than only its built-in fallback.

## Resource architecture

Many bizarre fake extensions (`.dll`, `.sys`, `.ctp`, `.bvs`, `.nec`, etc.) are simply application assets. A large class are raw 640x480 RGB565 screens. Examples decoded during this pass include Capcom CPS1/CPS2 platform screens, language/setup graphics, search/list screens, save-state `NODATA` imagery and the stranded controller-remap background.

The central resource pointer table links these opaque filenames to frontend states; the extensions themselves carry essentially no semantic meaning.

### Arcade metadata

Three small resources form a clear arcade metadata set:

```text
sensc.bvs  -> internal short identifiers
             SGZJ, SGZJ115, SGZJZZPLUS, SGZJZZPLUSA, WYSEC, ZGLII

aepic.nec  -> Chinese display titles
             三国战纪
             三国战纪 1.15
             三国战纪 正宗 Plus
             三国战纪 正宗 Plus a
             西游释厄传
             中国龙 II

subst.tax   -> packaged filenames
             Knights of Valour.zfb
             Knights of Valour 1.15.zfb
             Knights of Valour Plus.zfb
             Knights of Valour Plus a.zfb
             Oriental Legend.zfb
             Dragon World II.zfb
```

This shows that at least part of the bundled arcade frontend metadata is externalized on the SD card rather than being hard-coded exclusively in `bisrv.asd`.

## Firmware lineage

Public SF2000 mapping-tool source records the historical architecture transition:

- mid-March / April firmware stored global mappings inside `bisrv.asd` and supported per-game `.kmp` files;
- May 15 and later stock firmware moved mappings to `Resources/KeyMapInfo.kmp` and removed the per-game mechanism.

The XGO has:

```text
active per-game KMP load/write
embedded fallback maps
older gpapi.bvs fifth-page artwork
no KeyMapInfo.kmp file
no KeyMapInfo.kmp literal string
other vendor/later frontend features such as search/favorites
```

This is **strong evidence of a feature-mixed vendor fork based substantially on the older/pre-May mapping architecture**, with later or independent vendor changes merged into the frontend. It is not safe to assign an exact stock SF2000 fork date from this evidence alone.

## Firmware update path remains dangerous

The binary contains an active updater for:

```text
/mnt/sda1/UpdateFirmware/Firmware.upk
```

with SPI-NOR read/write code and progress/error messages. Generic SF2000 update packages should not be flashed to the XGO merely because of the shared lineage.

By contrast, a game-specific `.kmp` uses the ordinary save-directory path and does not require touching internal flash or replacing `bisrv.asd`.

## Current confidence summary

### CONFIRMED

- active per-ROM `%s/save/%s.kmp` loader and writer;
- exact 48-byte, 12-record mapping size;
- physical record order `X,Y,L,A,B,R`, P1 then P2;
- turbo/autofire flag behavior;
- six native emulator-family IDs and exact extension routing;
- `.sms` is routed natively by the stock frontend;
- 32X/Sega-CD core code exists but their normal extensions are not routed by the frontend;
- four-item `SELECT+START` in-game menu;
- `gpapi.bvs` exists as remapping artwork but is outside the reachable four-state menu renderer;
- direct H1512 chip-ID comparison;
- firmware programs the PLL setting its SDK reports as 810 MHz;
- 640x480 frontend canvas;
- `Archive.sys` is a three-word persistent-state file;
- its third word stores the four-step volume state;
- exact `L+SELECT` and `SELECT+START` frontend combinations;
- active internal-flash update path.

### STRONG EVIDENCE

- XGO is a feature-mixed fork of the older SF2000/HC15xx software architecture rather than a clone of one stock release;
- the fifth `gpapi.bvs` screen is inherited dead/stranded remapping UI art;
- per-game `.kmp` is the safest practical route to remapping controls without firmware modification;
- the shipped GBA BIOS file is intended for gpSP's explicit external-BIOS path.

### STILL UNRESOLVED

- exact meaning of `Archive.sys` word 2 / the persistent binary UI toggle;
- exact physical LCD controller;
- whether a dynamically generated filename implements any additional global mapping persistence;
- whether any emulator-specific debug combination is user-accessible outside the frontend's two identified combinations;
- how much of the compiled emulator option surface can be activated without replacing or patching the frontend.
