# Deep Software Pass — Persistent State, Dead UI, and OEM Fork Evidence

Status: **new static-analysis findings confirmed from the preserved XGO `bisrv.asd` and SD resources**.

## `gpapi.bvs` is present but excluded from the active four-page in-game state machine

The in-game renderer at `0x80354640` indexes a resource-pointer array beginning at `0x80a3c318` using `gp-0xdc4` as a zero-based page state.

The five consecutive inherited menu resources are:

```text
index 0 -> 0x809a2ff0 -> dism.cef
index 1 -> 0x809a2ffc -> d2d1.hgp
index 2 -> 0x809a3008 -> bisrv.nec
index 3 -> 0x809a3014 -> pwsso.occ
index 4 -> 0x809a3020 -> gpapi.bvs
```

The active navigation logic at `0x80354ebc` explicitly permits increment only while the state is less than 3:

```text
state < 3 -> state++
state == 3 -> cannot advance
```

The renderer likewise only dispatches special behavior for states `0..3`. Runtime testing independently confirms the visible items are Resume, Quit, Load, and Save.

The pointer to `gpapi.bvs` occurs only once in the binary, as the fifth element immediately following the live four-page array. No executable path has been found that selects index 4.

**Conclusion:** `gpapi.bvs` is inherited remapping-related artwork stranded immediately after the live pause-menu resource array. The XGO vendor retained the asset and the separate per-ROM `.kmp` machinery, but the shipped frontend no longer exposes the old fifth-page remapping editor.

## `Archive.sys` is a three-word persistent settings file

The shipped `Resources/Archive.sys` is 12 bytes:

```text
00 00 00 00   word 0
00 00 00 00   word 1
21 00 00 00   word 2 = 33
```

Startup routine `0x8034c670` opens the file and performs three consecutive 4-byte reads into:

```text
word 0 -> gp-0xd7c
word 1 -> gp-0x5f40
word 2 -> gp-0xd20
```

Persistence routine `0x80353a20` writes the same three 4-byte values back in the same order.

### Word 0: language index

The first value is a six-state selector. UI code increments it and wraps `5 -> 0`, exactly matching the six languages declared by XGO `Foldername.ini`. It is repeatedly used to index localized frontend resource arrays.

**CONFIRMED:** `Archive.sys` word 0 is the language index, values `0..5`.

### Word 1: binary display/TV-standard setting

The second value is toggled as:

```text
(value + 1) & 1
```

and immediately fed into a display/video reconfiguration path before `Archive.sys` is saved. The inherited SF2000 format identifies the corresponding second word as the NTSC/PAL TV standard.

**STRONG EVIDENCE:** XGO retains the same second-word NTSC/PAL setting. The static code independently confirms it is a persisted binary video-output setting.

### Word 2: volume

Startup normalizes the third word to exactly:

```text
0
33
66
99
```

The controller task increments it by 33 and wraps after 99. It then calls the audio-volume helper and persists the settings file.

**CONFIRMED:** word 2 is the four-step volume level.

## GPIO L29 is the volume-button input

The controller task at `0x8035d648` reads `0xb8800050` and masks `0x20000000`, i.e. GPIO bank L bit 29.

When L29 is active and the debounce flag permits a new press, firmware:

```text
volume += 33
if volume >= 101: volume = 0
apply volume
save Archive.sys
```

This directly identifies L29 as the XGO's one-button volume control. It corrects an earlier speculative interpretation of this GPIO as RF/Handle/display-mode related.

## XGO-renamed Favorites and History files

Two otherwise opaque XGO resource files match the established SF2000 list-storage format exactly.

### `Falas.clk`

Size: 40 bytes.

```text
uint32 count = 9
9 x { uint16 list_id, uint16 game_index }
```

The file length is exactly `4 + 9*4` bytes.

### `Hisas.boa`

Size: 804 bytes.

```text
uint32 count = 200
200 x { uint16 list_id, uint16 game_index }
```

The file length is exactly `4 + 200*4` bytes.

Public SF2000 documentation describes `Favorites.bin` and `History.bin` using this same count-plus-pairs layout. The names differ, but the XGO structures are exact.

**STRONG EVIDENCE:** `Falas.clk` is the XGO-renamed Favorites store and `Hisas.boa` is the XGO-renamed History store. The preserved card currently contains 9 favorites and a 200-entry history.

The XGO pair data includes list IDs above the classic seven stock systems, consistent with its expanded/repeated Arcade menu sections.

## Exact `Foldername.ini` has been independently observed on another noname OEM device

The XGO file is:

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

A 2024 4PDA report from the SF2000 community independently posted this exact configuration from an unnamed AliExpress console. That owner reported that the device's native firmware/menu worked, while ordinary/newer SF2000 `bisrv.asd` replacements reached a frozen main-menu image with no music or controls. The stated goal was also to obtain button remapping.

This external observation strongly supports the model that the XGO belongs to a broader OEM fork family rather than being a one-off modified SD card.

It also reinforces a critical compatibility warning: shared `SF2000` resources and HC15xx lineage do **not** imply drop-in compatibility with stock SF2000 firmware.

## Why this matters for button remapping

The current evidence now separates two formerly conflated mechanisms:

```text
old inherited on-device editor artwork
    gpapi.bvs
    -> present but unreachable in XGO pause state machine

actual per-game mapping engine
    %s/save/%s.kmp
    -> active loader
    -> active writer
    -> 48-byte 12-record format
    -> still executable in XGO
```

Therefore the practical route to remapping on the stock XGO is not to search for a fifth visible pause-menu item. It is to use the retained per-game `.kmp` mechanism directly from the SD card, after finishing exact record/value validation for each emulator family.

## Confidence summary

### CONFIRMED

- pause-page state is limited to four values `0..3`;
- `gpapi.bvs` is fifth in the inherited resource sequence but outside that live state range;
- `Archive.sys` is read and written as three uint32 values;
- Archive word 0 is a six-language index;
- Archive word 2 is volume quantized to `0/33/66/99`;
- GPIO L29 advances and persists the volume setting;
- `Falas.clk` and `Hisas.boa` have exact count-plus-uint16-pair structures matching favorites/history storage.

### STRONG EVIDENCE

- Archive word 1 retains the inherited NTSC/PAL TV-standard meaning;
- `Falas.clk` = Favorites and `Hisas.boa` = History;
- `gpapi.bvs` is dead/stranded legacy remapping UI artwork, not a hidden page reachable by ordinary input;
- the same XGO-style menu configuration exists on at least one other noname OEM fork whose firmware is not drop-in compatible with standard SF2000 images.

### STILL OPEN

- exact OEM/model lineage behind the shared `11 7 0` fork;
- exact mapping of XGO list IDs 8-10 to its additional Arcade sections;
- whether any unreachable remapping-editor code survives separately from the dead artwork;
- safest generated `.kmp` profiles for each emulator family.
