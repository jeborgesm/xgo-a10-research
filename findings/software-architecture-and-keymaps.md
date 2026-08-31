# XGO Software Architecture and Keymap Findings

Status: **active executable paths confirmed; some UI reachability remains under analysis**.

## Scope

This note records a deeper static-analysis pass over the preserved XGO `bios/bisrv.asd` and microSD `Resources` tree. Runtime virtual addresses below use the full ASD image mapped at `0x80000000`, preserving the 0x200-byte LCFG header. This mapping reproduces the previously confirmed hidden `L + SELECT` comparison at `0x80356444`.

## Major finding: per-game `.kmp` loading is active

The XGO does not merely retain an obsolete `.kmp` filename string. Its executable game-launch path actively constructs, opens, reads, and applies a per-ROM keymap.

At `0x8035ed48` the loader prepares a path with the format string at `0x809a3418`:

```text
%s/save/%s.kmp
```

Representative code:

```text
8035ed64  lui    ...,0x809a
8035ed68  addiu  $a1,...,0x3418      ; "%s/save/%s.kmp"
8035ed6c  addiu  $a0,$sp,0x10        ; output path buffer
8035ed70  move   $a2,$s4             ; path/system argument
8035ed74  move   $a3,$s5             ; ROM-name argument
8035ed88  jal    0x802946d8          ; sprintf-like
8035ed90  ...                         ; "rb"
8035ed98  jal    0x802b3524          ; fopen-like
```

When the file exists, firmware reads exactly **12 items of 4 bytes = 48 bytes** into the working keymap buffer at `0x810a0f58`:

```text
8035edb4  move   $a0,$s2             ; keymap buffer
8035edb8  addiu  $a1,$zero,4         ; item size
8035edbc  addiu  $a2,$zero,12        ; item count
8035edc0  jal    0x802b3698          ; fread-like
```

It closes the file and immediately invokes the mapping compiler at `0x8035e83c`.

This is a **CONFIRMED executable feature** in the XGO firmware.

### 48-byte structure

The mapping compiler treats each 4-byte entry as:

```text
low 16 bits  = logical emulator button/key selector
bit 16       = turbo/autofire flag
```

It processes twelve entries. The structure therefore matches the SF2000-family pattern of six remappable physical buttons for Player 1 followed by six for Player 2.

The internal selector values seen in XGO defaults include:

```text
0, 1, 8, 9, 10, 11
```

These correspond to the familiar SF2000-family logical button values commonly represented in keymap documentation as `0x0000`, `0x0100`, `0x0800`, `0x0900`, `0x0A00`, and `0x0B00` respectively.

## Default fallback maps

If the per-game `.kmp` cannot be opened, the firmware selects one of six compiled 48-byte default tables according to the active emulator/system bitmask at `gp - 0xca4`.

Observed dispatch IDs:

```text
0x01
0x04
0x08
0x10
0x20
0x40
```

The file-extension dispatcher independently identifies several of these values:

```text
0x01 = NES / NFC / FDS / UNF        -> FC/NES
0x04 = BIN / MD / SMD / GEN / SMS   -> Mega Drive / SMS
0x08 = SMC / FIG / SFC / ...        -> Super Famicom / SNES
0x10 = GBA / AGB / GBZ              -> Game Boy Advance
0x20 = GBC / GB / SGB               -> Game Boy / Game Boy Color family
0x40 = remaining native arcade path -> strongly consistent with Arcade/FBA
```

Thus the keymap dispatcher maps directly onto the six principal emulator families exposed by the XGO UI.

All six default tables contain duplicated six-entry halves, indicating identical Player 1 and Player 2 default maps.

## Select + Start is an in-game system shortcut

A second exact multi-button comparison exists in the active emulator loop.

At `0x8035eecc`, firmware loads the current translated Player 1 event word and compares it with `0x0009`:

```text
8035eecc  lw     ..., -0xd18($gp)
8035eed0  addiu  ..., $zero, 0x0009
8035eed4  beq    ..., ..., 0x8035f010
```

From the already reconstructed event map:

```text
SELECT = 0x0001
START  = 0x0008
```

Therefore:

```text
0x0009 = SELECT + START
```

The branch calls the large UI routine at `0x80354bf8`. Its input handling recognizes the normal translated menu events (`UP`, `DOWN`, `LEFT`, `RIGHT`, `A`, etc.) and loads several in-game UI resources. This is **strong evidence that SELECT + START opens the XGO in-game/pause menu**.

This is separate from the already confirmed main-menu hidden shortcut:

```text
L + SELECT -> Resources/Test.zsf
```

A scan of the known P1 event-history variable found no second main-menu exact multi-button equality comparable to the `L + SELECT` test trigger. Other references mostly perform ordinary `A`-button bit tests.

## Remapping UI asset is physically present

`Resources/gpapi.bvs` exists on the XGO card and is exactly `614400` bytes, matching `640 x 480 x 2` RGB565.

Decoded as RGB565 little-endian, it visibly contains a controller-layout screen: a D-pad on the left, six round button positions on the right, and a selection arrow. It is unquestionably a button-layout/remapping UI background rather than a generic menu image.

The firmware resource-name table contains `gpapi.bvs` at `0x809a3020`, with a pointer in the central resource table at `0x80a3c328`.

Public SF2000 archaeology independently identifies the same filename as the fifth in-game-menu screen and associates it with button-layout changing. The XGO's copy therefore preserves a real UI component from that feature family.

### Important difference from later stock SF2000 mapping UI

The XGO Resources tree does **not** contain:

```text
KeyMapInfo.kmp
kmbcj.acp
cketp.bvs
lk7tc.bvs
```

and the XGO firmware contains no literal `KeyMapInfo.kmp` string.

Those files belong to the later stock SF2000 global button-mapping UI. In contrast, the XGO firmware contains an active `%s/save/%s.kmp` per-game loader, even though later stock SF2000 firmware removed per-game keymaps.

This makes the XGO look like a **fork that retained the older per-ROM mapping mechanism while carrying other later/custom UI changes**, rather than a simple copy of one stock SF2000 release.

## Controller-test resources

The firmware resource table still includes names for:

```text
seltMap.key
dectMap.key
```

and code references the controller-test resource family, but these two files are absent from the extracted XGO `Resources` directory. By contrast, `Resources/Test.zsf` is present and is launched by the confirmed `L + SELECT` hidden path.

This is another example of retained SF2000-family code/resource metadata not necessarily matched one-for-one by the shipped XGO card contents.

## File-extension / emulator dispatcher

A 0x84-byte-per-entry table beginning around `0x80a3c4c8` maps ROM extensions to emulator bitmasks. Confirmed entries include:

```text
BKP, ZIP                    -> 0x00010000
ZFC, ZSF, ZMD, ZGB, ZFB     -> 0x00030000 wrapper/container path
SMC, FIG, SFC, GD3, GD7,
DX2, BSX, SWC               -> 0x00000008 (SNES)
NES, NFC, FDS, UNF          -> 0x00000001 (NES)
GBA, AGB, GBZ               -> 0x00000010 (GBA)
GBC, GB, SGB                -> 0x00000020 (GB/GBC)
BIN, MD, SMD, GEN, SMS      -> 0x00000004 (Mega Drive/SMS)
```

The same system IDs are consumed by the keymap loader, confirming that input mapping is selected as part of emulator launch rather than being merely a UI preference disconnected from emulation.

## `Foldername.ini` customization

The shipped XGO card contains:

```text
SF2000
6
FFFFFF
FF8000 ROMS
FF8000 FC
FF8000 SFC
FF8000 MD
FF8000 GB
FF8000 GBC
FF8000 GBA
FF8000 ARCADE
FF8000 ARCADE
FF8000 ARCADE
FF8000 ARCADE
FF8000 ARCADE
11 7 0
472 144 144 208
40 24
```

This confirms that the XGO still identifies its menu configuration with the hard-coded `SF2000` family header while using an XGO-specific section arrangement. The repeated ARCADE placeholders and `11 7 0` layout values differ from common stock SF2000 configurations and are evidence of a customized frontend configuration.

## Firmware update path remains dangerous

The binary contains an active update path for:

```text
/mnt/sda1/UpdateFirmware/Firmware.upk
```

alongside SPI-NOR read/write routines and user-facing strings such as `Update success`, `Update fail`, `format error`, and `File size over flash memory`.

This reinforces the existing safety rule: experiments with replacement `bisrv.asd` files or alternate HC15xx firmware should use a disposable microSD and should be inspected for flash-writing behavior before execution. A normal game-specific `.kmp` experiment is substantially lower risk because it uses the ordinary save-directory read path rather than the firmware updater.

## Current confidence summary

### CONFIRMED

- active per-ROM `%s/save/%s.kmp` path construction;
- `.kmp` files are opened in binary-read mode;
- exactly 48 bytes are read as twelve 4-byte mapping records;
- the loaded mapping is compiled into the emulator input tables;
- six emulator-family IDs select six compiled fallback keymaps;
- extension dispatch identifies FC/NES, MD/SMS, SFC/SNES, GBA, and GB/GBC IDs directly;
- `gpapi.bvs` exists on the XGO card and decodes to a controller-layout/remapping screen;
- the later stock `KeyMapInfo.kmp` filename is absent from both the XGO card and literal firmware strings;
- exact `SELECT + START` (`0x0009`) comparison exists in the active emulator loop;
- exact `L + SELECT` main-menu comparison launches `Test.zsf`.

### STRONG EVIDENCE

- `SELECT + START` is the in-game/pause-menu shortcut;
- `0x40` is the Arcade/FBA native emulator ID;
- the XGO's `.kmp` format is the familiar SF2000 6-buttons x 2-players mapping structure;
- XGO is a feature-mixed SF2000/HC15xx fork rather than a direct stock-version clone;
- the shipped `gpapi.bvs` screen is intended to participate in an in-game remapping interface, though exact reachability is still being traced.

### NOT YET CONFIRMED

- whether the `gpapi.bvs` remapping screen is reachable through the XGO's in-game menu without additional/missing resources;
- exact user-facing menu item sequence and labels on the XGO;
- whether writing a 48-byte per-game `.kmp` successfully overrides controls on physical XGO hardware;
- whether any other hidden exact multi-button shortcut exists through another state variable not yet enumerated;
- whether global mapping persistence exists under a filename generated dynamically rather than `KeyMapInfo.kmp`.

## Practical implication

The most promising low-risk modification path discovered so far is now **per-game button remapping through a 48-byte `.kmp` file on the microSD**. Before producing files for physical testing, the remaining work is to label the six physical-button slots precisely for each emulator family and verify the exact ROM filename/path semantics used by the XGO launcher.
