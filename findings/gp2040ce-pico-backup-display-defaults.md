# GP2040-CE Pico 0.7.12 backup: display defaults evidence and plan

Date: 2026-10-09. Input artifacts provided by user: `gp2040ce_backup_20261004012055472.gp2040` (JSON configuration backup) and `GP2040-CE_0.7.12_Pico.uf2` (reference firmware). No binary artifact copied into this repository.

## User decision

The existing splash image is the standard/default splash; **do not embed or customize it for Test01**. A future optional XGO-branded splash can be designed separately. Prioritize replicating the user's working display and preserving all GP2040-CE capabilities.

## Direct backup evidence (HW-user-backup; not integrated-hardware proof)

```json
{
  "enabled": 1,
  "flipDisplay": 0,
  "invertDisplay": 0,
  "buttonLayout": 0,
  "buttonLayoutRight": 14,
  "splashMode": 1,
  "splashChoice": 0,
  "splashDuration": 5,
  "displaySaverTimeout": 1,
  "turnOffWhenSuspended": 0,
  "buttonLayoutCustomOptions": {
    "params": {"layout": 1, "startX": 8, "startY": 28, "buttonRadius": 8, "buttonPadding": 2},
    "paramsRight": {"layout": 1, "startX": 8, "startY": 28, "buttonRadius": 8, "buttonPadding": 2}
  }
}
```

The backup contains a 1024-byte `splash.splashImage` (SHA256 `04d3c72322118fb98e06565a5720d8471ae044b2827d36b0d66b1a6f98705ee3`). User states this is a stock/default splash, so no need to vendor the bytes. Backup `gamepad.inputMode=2` is **not** the target XGO mode and must not be copied as the firmware default.

## Integration approach

- Preserve the stock `configs/Pico/BoardConfig.h` physical GPIO mapping, GP0/GP1 I2C OLED, turbo and LED.
- Translate the display backup's saved fields into the **pinned newer GP2040-CE** configuration model, verifying enum meanings before translating numeric layouts, saver timeout units or splash modes.
- Implement firmware **unset-property defaults** rather than hardcoded overrides; saved user settings must remain editable through Web Config.
- Use stock/default splash in Test01; custom XGO splash is deferred.
- Preserve XGO default input mode and a recoverable Web Config/bootloader path.
- Existing VBUS-powered OLED wiring is user hardware-confirmed; do not reopen this issue.

## Status / gates

- [x] Source backup read and display fields inventoried.
- [x] Stock splash decision recorded.
- [x] Exact upstream insertion anchors and Pico OLED board config checked.
- [ ] Compare backup 0.7.12 enum definitions with pinned upstream.
- [ ] Implement verified default mappings into integration overlay.
- [ ] Execute overlay and compile a firmware.
- [ ] Verify Web Config, display, remapping, add-ons and XGO transport on hardware.

No integrated UF2 or hardware validation yet.
