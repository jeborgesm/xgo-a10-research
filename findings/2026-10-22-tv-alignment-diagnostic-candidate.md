# TV System lower-left alignment candidate (2026-10-22)

## Scope
Hardware photographs conclusively show PAL/NTSC overlay in the **legacy bottom-left tile**, while the TV image was relocated to top-right. This experimental candidate **moves TV icon/caption back to lower-left** so runtime PAL/NTSC text should land within TV screen; it does **not** claim to fix PAL submenu invisibility. Selection highlight for TV row2 (index 2) adjusted with sltiu threshold 3→2.

## Artifact
- ZIP: `XGO_TV_BottomLeft_NTSC_Underline_Restored_PAL_Diagnostic.zip`
- SHA-256: `b1d185686ebe2585113944e7fa2fc11e808fd04d1e04a9e1c86447d0bd9bd00e`
- firmware SHA-256: `853031610cec4103c89d9d8c66e68dfa89f9e5c49ef7f7ca4a607f339ea746bb`
- source native-toggle ZIP SHA-256: `aa45f549eca9c58aad93b5804aa44b40857c87418cf0d80ccc81e169b5f058a2`
- LCFG CRC32/MPEG-2: `2e78e431`

## Independent checks (BIN)
- ZIP CRC integrity passed.
- Firmware length unchanged.
- Exactly five firmware bytes changed versus original native toggle: CRC four bytes at `0x18C..0x18F` and low immediate byte of `sltiu ra,a1,3`→`sltiu ra,a1,2` at `0xA37F68`.
- Original P1/P2 underline jump hook `0x1120FD3B` at `0xA38AB4` remains active, reversing the isolated/failed bypass.
- Six 640×480 RGB565 resources modified, with old TV tile removed from top-right and TV icon/caption shifted to bottom-left.
- All controller routing and Refresh firmware bytes unchanged apart from highlight placement.
- Reproducible construction algorithm committed at `tools/build_tv_bottom_left_diagnostic.py`. Script may not create byte-identical package metadata ZIP due to manifest/readme serialization; verify **functional payload** byte differences first.

## OPEN, critical
**PAL-specific Refresh and Handle submenu failure is hardware-confirmed and remains unresolved**. This candidate is only an alignment/underline A/B diagnostic, not a final fix. Need inspect actual PAL rendering pipeline, framebuffer source/stride and switch callbacks. Do not claim all three bugs fixed.

## Hardware action
On backed-up test SD install `bios/` and `Resources/` only. Check NTSC TV label position inside TV image, TV tile selection highlight, P1/P2 underline; then switch PAL and check whether Refresh and Handle still fail. Preserve outcome in GitHub.
