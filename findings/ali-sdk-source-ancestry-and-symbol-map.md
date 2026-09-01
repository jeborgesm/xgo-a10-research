# ALi SDK source ancestry and first reusable XGO symbol map

## Status
New firmware-wide mapping pass after parking the Handle Interface as a diminishing-return subsystem.

## Headline
The XGO `bisrv.asd` is not only SF2000-family software. Large parts of its platform/application skeleton can now be tied directly to older **ALi Corp. set-top-box SDK/demo source code** that is publicly mirrored in unrelated repositories.

This matters because those source trees provide names, structures and intent for routines that were previously only anonymous MIPS code in the XGO image.

## Direct source-lineage evidence

The XGO firmware string block around `0x8099d2xx`-`0x8099d9xx` contains source/module markers and debug strings including:

```text
system_data.c
board.c
control.c
disk_manager.c
root.c
m_boot_vpo_active
pre_tv_mode
AppInit : get_sysinfo_from_bl(TRANS_VDEC_TYPE) fail
AppInit : get_sysinfo_from_bl(TRANS_VPO_TYPE) fail
share memory mapping
__MM_VBV_START_ADDR
__MM_MAF_START_ADDR
__MM_FB_START_ADDR
AVC VBV
LWIP_MEM
LWIP_MEMP
```

Public ALi SDK/demo source mirrored in `levi028/loader` contains the same application architecture. In particular:

- `ali_upg_128m/prj/app/demo/combo/sabbat_dual/root.c` defines `m_boot_vpo_active`, `pre_tv_mode`, calls `get_sysinfo_from_bl(...)`, initializes hardware, and contains the same boot/video-output architecture.
- `ali_upg_128m/prj/app/demo/combo/sabbat_dual/ui_debug.c` contains the same memory-layout debug machinery and labels such as `share memory mapping` and `__MM_VBV_START_ADDR`.

This is stronger than generic SDK similarity: multiple uncommon identifiers and debug messages match the same ALi application framework.

## Interpretation

### CONFIRMED

- XGO carries ALi/TDS application-framework code descended from ALi's embedded media/STB SDK lineage.
- The `root.c`/video-output/memory-layout layer is not an XGO invention.
- Many apparently exotic strings in `bisrv.asd` are inherited platform framework rather than evidence that the retail XGO actually exposes every compiled capability.

### Important caution

Strings such as:

```text
LWIP_MEM
LWIP_MEMP
network
http://
https://
```

must **not** be interpreted by themselves as proof that the XGO has usable Ethernet/Wi-Fi/network hardware. The ALi demo framework contains optional networking code and generic media/STB infrastructure. Runtime reachability and board configuration are required before calling such features active.

This source ancestry gives us a way to separate inherited SDK baggage from XGO/SF2000-specific code.

## XGO runtime mapping convention

As in the existing firmware notes, the full ASD image is mapped at:

```text
runtime VA = file offset + 0x80000000
```

The LCFG header remains part of that mapping.

## First source-assisted XGO function anchors

Static xref analysis of the local XGO binary produced these anchors:

| XGO VA | Evidence / provisional identity |
|---|---|
| `0x801b72b0` | routine referencing `h1512_gpio_pinmux_sel` |
| `0x801b9c84` | low-LCD video-parameter routine; emits `lcd 800*480 init` and writes 800x480 timing geometry |
| `0x801b9de4` | LCD/TV video-output switching/configuration routine cluster |
| `0x8027747c` | `adc_attach` device-construction/attach routine |
| `0x802784?` | surrounding ADC/SAR driver family; more mapping pending |
| `0x8029846c` | SD/TF GPIO-detect setup; referenced by main control/startup path |
| `0x80298b2c` | serial-flash storage device setup referencing `STO_SFLASH_0` |
| `0x80299a90` | SPI-NOR flash-ID/probe routine; prints three-word NOR ID buffer |
| `0x80306cdc` | I2S/audio-output configuration path; prints sample-rate/sample-count/DAC format |

The ADC attach routine configures a device structure whose hardware base is explicitly:

```text
0xb8818400
```

and installs a family of operation callbacks. This gives us a concrete hardware-block anchor for later ADC/key/power analysis.

## 800x480 video path now visible in code

At XGO `0x801b9c84`, the routine writes a video-parameter structure with literal geometry including:

```text
0x0320 = 800
0x01e0 = 480
```

and emits:

```text
lcd 800*480 init
```

The neighboring routine beginning at `0x801b9d20` instead contains a 320x240 parameter set, while the caller near `0x801b9de4` chooses between video-output configurations.

This strongly identifies the `0x801b9c84` block as the XGO high-resolution LCD parameter path rather than a random unused display string.

## SF2000 community symbol map becomes a reusable XGO oracle

`madcock/sf2000_multicore` publishes linker scripts for known stock SF2000 firmware. One script identifies, among many others:

```text
get_vp_init_low_lcd_para = 0x801b9d0c
switch_lcd_or_tv         = 0x801b9dd0
printf                   = 0x8028e474
memcpy                   = 0x8028e620
memset                   = 0x8028e850
```

The XGO firmware contains the corresponding libc routines with a **constant +0x634c displacement** across this block:

```text
SF2000 printf  0x8028e474 -> XGO 0x802947c0
SF2000 memcpy  0x8028e620 -> XGO 0x8029496c
SF2000 memset  0x8028e850 -> XGO 0x80294b9c
```

The identification is independently supported by XGO call semantics:

- `0x802947c0` is repeatedly called with printf-style format strings/arguments.
- `0x80294b9c` is called with destination, zero, size in structure-clearing paths.
- `0x8029496c` is used as a memory-copy style helper.

Because the same displacement holds across multiple adjacent libc symbols, this is a robust **section-level relocation map**, not a single guessed function.

### Derived XGO libc addresses under this verified +0x634c block shift

```text
malloc    0x80291c04
free      0x80292814
realloc   0x802928d8
calloc    0x80292b90
vsnprintf 0x80294624
sprintf   0x802946d8
vprintf   0x80294780
printf    0x802947c0
snprintf  0x802947e8
vsprintf  0x80294808
rand      0x802948b8
memcpy    0x8029496c
memset    0x80294b9c
memcmp    0x80294c7c
memmove   0x80294ce0
strcpy    0x80294dac
strcmp    0x80294dec
strlen    0x80294e30
atoi      0x80294e58
```

Several mapped entries were sanity-checked directly in the XGO binary and have plausible function prologues/instruction shapes.

## Why the displacement is not globally constant

The display/video block demonstrates that XGO is not simply the stock binary shifted as one unit:

```text
SF2000 get_vp_init_low_lcd_para 0x801b9d0c
XGO corresponding LCD-param path 0x801b9c84
```

while the libc region later moves by `+0x634c`.

Therefore XGO contains inserted/removed/recompiled regions between these landmarks. The correct comparative method is **piecewise address mapping by stable code sections**, not a single whole-image delta.

This is exactly what we need to reconstruct the OEM patch set.

## GB300 comparison

A current GB300 V2 multicore linker script places:

```text
get_vp_init_low_lcd_para = 0x801be3f0
switch_lcd_or_tv         = 0x801be4b4
```

The XGO video-output block remains much closer in address/layout to the SF2000 map than to GB300, while the already-reconstructed XGO input scanner has GB300-like dual-DATA topology.

This supports the broader model that XGO is a board-specific fork of the SF2000 application lineage that selectively adopts/reuses other HC15xx board-support patterns rather than being a straight GB300 derivative.

## New firmware-mapping strategy

Highest-value approach now:

1. use public SF2000 linker scripts as named anchors;
2. identify piecewise XGO address deltas using 2+ independently verified functions per region;
3. label the XGO binary progressively;
4. use ALi SDK source mirrors to recover function intent and structure definitions;
5. mark inherited optional SDK features separately from confirmed active retail-device features;
6. focus manual disassembly on regions where the XGO map diverges sharply from stock SF2000.

Those divergent regions are the likely OEM board-support patch set and therefore the best place to find XGO-specific hardware behavior.

## Sources

- Local XGO `bios/bisrv.asd`, SHA-256 `869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf`
- `levi028/loader`, `ali_upg_128m/prj/app/demo/combo/sabbat_dual/root.c`
- `levi028/loader`, `ali_upg_128m/prj/app/demo/combo/sabbat_dual/ui_debug.c`
- `madcock/sf2000_multicore`, `bisrv_08_03.ld`
- `madcock/sf2000_multicore`, `stockfw.h`
- `Trademarked69/sf2000_multicore`, `linker_scripts/bisrv_GB300_V2-core.ld`
