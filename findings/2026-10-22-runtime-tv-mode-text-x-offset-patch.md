# Runtime TV mode label relocation (2026-10-22)

## User-approved baseline (HW)
Bold SETUP/REFRESH/HANDLE caption resources passed hardware testing. Retain the six RGB565 resources from `XGO_Bold_Setup_Refresh_Handle_Typography_Resource_Test.zip` (SHA-256 `10925f556f871fc2468d200c8e84b54255eb06ce8e0bf31e6822fb99187139fb`). Controller routing and P1/P2 underline work in NTSC. PAL Refresh and Handle submenus **still fail to display**.

## Exact binary search result (BIN)
Found literal firmware strings `NTSC\0` at offset `0x9B5818` and `PAL\0` at `0x9B57F4`. The Setup UI native text path refers to those strings and calls the same text-rendering routine `jal 0x80354A29`. The first parameter is framebuffer, and the next parameters are X and Y positions:

| File offset | Instruction | Text path / observed X, Y |
| --- | --- | --- |
| `0x359B88` | `0x2405007D` = addiu a1,zero,125 | NTSC Setup label, Y=297 |
| `0x35AC98` | `0x24050085` = addiu a1,zero,133 | secondary NTSC Setup label, Y=297 |
| `0x35ACD0` | `0x2405008D` = addiu a1,zero,141 | PAL Setup label, Y=297 |

All three point to same rendering API and are followed by X/Y assignment and literal NTSC/PAL string pointer. No need to relocate the TV icon or redraw text in bitmaps to correct the offset.

## New experimental build (BIN, offline verified; HW untested)
`XGO_TV_Text_Left24_Bold_P1_P2_PAL_Pending_TEST.zip`

- Source ZIP: bold-caption package above, retained completely.
- Patched only three immediate instructions to shift native runtime mode label **24 framebuffer pixels left**, preserving relative offsets:
  - `0x359B88`: `0x2405007D` → `0x24050065` (125 → 101)
  - `0x35AC98`: `0x24050085` → `0x2405006D` (133 → 109)
  - `0x35ACD0`: `0x2405008D` → `0x24050075` (141 → 117)
- Recalculated CRC32/MPEG-2 at `0x18C`. Exact firmware changed byte offsets: `0x18C..0x18F`, `0x359B88`, `0x35AC98`, `0x35ACD0`. All other firmware bytes and **all six approved bold Setup resources** preserved byte-for-byte.
- Verified fixed P1/P2 underline branch `0x80A38AB4: 0x1120FD3B` still active; controller normalization hook unchanged; ZIP integrity passes.
- ZIP SHA-256: `c08c43f1f58c9bfefcc6ad3acf9b85fbcb0a6e06b8e52b0fa510d42a865b4790`.
- Firmware SHA-256: `5dadf691ad812e952ef58e07a0f5cc9b183a30adf9de11e2ffc0473056a81654`.
- Builder stored in recovered browser environment: `build_xgo_tv_label_left24.py`. Artifact lives in conversation file storage; **not yet uploaded as Git binary**.

## Separate open PAL issue
**No change to the PAL submenu compositor** in this candidate. Refresh and Handle visible/interactive in NTSC, invisible after entering PAL. The custom underline renderer assumes row stride 1280 (640 RGB565) and is not proven causal. Investigate PAL transition and framebuffer ownership/stride for shared submenu renderer before claiming a fix. Avoid hardware prompts claiming this candidate repairs PAL.
