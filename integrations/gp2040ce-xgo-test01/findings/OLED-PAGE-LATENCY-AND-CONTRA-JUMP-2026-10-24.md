# XGO controller Test — SFII missed inputs and Contra ghost jump (offline deep dive, 2026-10-24)

## Field evidence — HW

The user tested the **new transparent GP2040-CE controller** (UF2 SHA-256 `94ea7228c774a67e8252e7e09d94938530e5d74572d985332e6840ae09fe8b84`), source driver blob `cccb985a05baa8bb9078b6e336eb5f991c1a7a8f`. Observations, with no inferred additional tests:

- Physical taps are now sent as taps, physical holds as holds; gameplay works in Street Fighter II and Contra, including holding X/Y for XGO-native turbo or playing Contra without turbo; user defeated Dhalsim.
- **Contra still produces intermittent unexpected JUMPs**.
- **SFII is not entirely reliable:** while holding LP once the game produced approximately three fast punches; on another held LP press nothing was recognized. User suspects some inputs are missing.
- No other observations have been supplied. Do not invent a frame-failure counter or actual electrical capture for THIS build.

**Disposition:** the transparent state machine is now HW-positive for fundamental button semantics and protected as the new baseline. The remaining defects are observable but **not uniquely localized** by those gameplay symptoms alone. No button-specific hacks, pulse extension, turbo synthesis or input suppression are permitted.

## Source/BIN finding 1 — Core0 OLED blocks physical input sampling (high-confidence contributor to missed taps)

The actual pinned upstream GP2040-CE commit `3d1f32f7d02d418826b725b60208278d3be878c3`, plus the XGO `integrations/gp2040ce-xgo-test01/apply.py` overlay, gives this path:

```
GP2040::run() on Core0
    debounceGpioGetAll(); gamepad->read();
    USBHostManager::process(); GP2040 add-ons + SOCD / hotkeys;
    XGODriver::process(gamepad) -> published_mask.store(exact 12-bit mask);
    addons.PostprocessAddons(processed);
    xgo_aux_tick()                                [XGO overlay]
      GP2040Aux::processOnce()                      [moved off Core1]
        addons.ProcessAddons()
          DisplayAddon::process()
            gpScreen->update(); gpScreen->draw();
              GPScreen::draw()
                GPGFX::render()
                  GPGFX_TinySSD1306::drawBuffer()
                    _options.i2c->write(1025 B)    [SSD1306]
                      i2c_write_blocking()          [Pico SDK]
```

Core1 is rightly reserved for the time-critical proprietary XGO DATA/CLOCK serial responder, but the moved Core0 auxiliary call has **no display frame-rate limiter**. The OLED performs a **full 1025-byte synchronous I2C transfer on *every* Core0 update**; the SH1106 branch instead performs eight 131-byte synchronous page writes. Both occupy Core0 until transmission completes, and the next `gamepad->read()` cannot run during these calls.

The Pico board enables I2C0 but does not override the `PeripheralI2C` default of **400 kHz**. Actual saved settings can override that speed. The **calculated wire transmission only** (9 bits per byte including ACK) is:

| Case | I2C data transfer | 400kHz nominal time | At 1MHz |
| --- | ---: | ---: | ---: |
| Legacy SSD1306 full frame | 1025 bytes | 23.063 ms | 9.225 ms |
| Legacy SH1106 8 pages | 8 × 131 bytes | 23.580 ms | 9.432 ms |
| Proposed SSD1306 one page | 129 bytes | 2.903 ms | 1.161 ms |
| Proposed SH1106 one page | 131 bytes | 2.948 ms | 1.179 ms |

I2C commands, software overhead, start/stop and clock stretching add time: **these are not measured end-to-end button scan rates.** Nevertheless the full-frame blocking transfer is comparable to or exceeds XGO's measured approximately **16.03 ms** controller-poll cadence and can miss a tap that occurs and releases entirely while Core0 is drawing. It can also delay recognition of a newly held input. A firmware source-level reproduction and real extracted C++ display-driver mock test are provided.

**Important limit:** OLED blocking alone does not invent an input or force a held bit to oscillate. Once Core0 has published a held LP state, Core1 retains that value across subsequent scans. Thus OLED latency is a strong explanation for **missed short/recent presses**, but the *three repeated LP punches* and the *Contra ghost jump* require additional explanation or XGO game behavior. Never claim all three observations have one established cause.

## Source/BIN finding 2 — first button sampled before CLOCK (ghost R/JUMP credible)

We revisited the **user-supplied original XGO `bios/bisrv.asd`**, SHA-256 `869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf`, at host scanner file offset `0x35D770` (MIPS virtual `0x8035D770`) and decoded it with a MIPS32 little-endian disassembler:

- `0x8035D834..0x8035D868`: switches controller DATA GPIO direction back to inputs after host-driven LOAD.
- `0x8035D870`: reads B15 serial channel 0 before first clock.
- `0x8035D890`: reads L0 serial channel 1 before first clock; `andi ..,0x1` and branches to OR its first raw state bit when LOW.
- `0x8035D8B0..0x8035D8E8`: switches shared B7 CLOCK low, delays with call argument 2, returns HIGH.
- `0x8035D8F0..0x8035D920`: reads the NEXT serial DATA states; 12 positions are explicitly unrolled in original firmware.

This verifies from **actual XGO BIN**, not just the RP2040 model: **slot0 R is sampled shortly after host releases its own DATA LOW drive, without any preceding CLOCK edge**. The passive P0 measurement documented a 7.8µs LOAD LOW followed by ~1.2µs until the first CLOCK FALL, and observed repeatable unexpected P2 JUMPs specifically when adding GREEN/DATA probe loading. A separate P3 passive direct USB-PHY test saw ghost jumps without active Pico serial DATA output (but used a different cable). These are strong convergence on *DATA/slot0 electrical sampling sensitivity*.

The current transparent controller correctly reports released R when physical R is not held; it releases its DP sink at frame start. **Releasing to high impedance cannot force the shared DATA wire to valid HIGH if host output/cable/PHY settling remains slow.** Changing the serializer's button mapping or masking R would violate the permanent physical-transparency rule and hide an actual physical press. There is **no measured connected-Frankie analog DATA rise curve**, so stronger pull-up, push-pull HIGH, clock budget tuning or cable modifications are **NOT authorized** from this evidence. The host's first-sample error remains a plausible source of ghost JUMP, not a proven electrical cause.

## Source/BIN finding 3 — CLOCK frame errors and ambiguous OLED-visible LP repetitions

The previous Test49 hardware session recorded many CLOCK/slot12 failures, but those numbers were collected on a **different diagnostic firmware**, not the newly approved transparent build. The transparent responder uses an 18µs CLOCK timeout, polls native USB-PHY RX_DM, drives pressed DATA bits LOW at CLOCK FALL, and releases after terminal falling pulse. Its IRQ-masked hot loop resides in RP2040 SRAM; the actual audited ELF has zero reachable calls into XIP under the critical interrupt mask. That excludes the *old* flash-backed atomic edge-queue failure from its critical path, not bus timing/glitch errors.

One source discrepancy remains: the older minimal *hardware-proven Caveman* responder ignored timeout from the **last CLOCK HIGH wait after all 12 bits**; GP2040-CE still treats that final HIGH timeout as a failed whole frame and demands DATA-HIGH rearming. A false terminal-tail error can therefore delay the next transaction and miss inputs, though it **cannot by itself create a false JUMP or LP**; Test49's terminal-slot statistics did not distinguish missing terminal FALL from missing final RISE. A separate offline-only one-line postamble candidate exists but is **not** promoted or mixed into the first OLED correction.

Under a correctly sequenced external CLOCK, the actual transparent `map_mask()+process()+emit_frame()` passes 4096/4096 masks and 22 injected abort/recoveries. Synthetic free-running tests show clock phase loss can contaminate later bits if artificially stalled, but **no actual post-Test49 phase loss or exact RP2040 PHY voltage threshold was observed**. SFII may also implement its own action behavior when a button is held; without an XGO input capture, three rapid punches cannot uniquely diagnose software-generated presses.

## Scoped correction: one OLED page per Core0 update, controller itself untouched

Prototype: `candidates/offline-transparent-page-oled/tiny_ssd1306.cpp`.

- For INPUT_MODE_XGO **only**, transfer one page (128 pixels × 8 rows) per `drawBuffer()` call and advance `framePage` modulo eight.
- Preserve existing SH1106 command+131-byte page layout, existing SSD1306 column/page addressing and 129-byte single-page data transfer.
- The full 128×64 display refreshes over eight passes; Core0 samples physical inputs between pages. No extra core, DMA, turbo generator, pulse queue, or serializer change.
- Non-XGO firmware display behavior stays exactly the pinned full-frame GP2040-CE implementation.
- Retain prediagnostic controller diagram and bottom row input history.
- This addresses **one grounded input-scan scheduling bottleneck**, NOT the unproven ghost-jump cause. Verification must compile the exact upstream-derived display code with both SSD1306/SH1106 mocks and compile/link the full pinned RP2040 firmware; hardware validation is a separate, single controlled trial.

## Remaining OPEN gates and decision rule

1. Verify the user’s actual configured I2C speed and whether the display is SSD1306 or SH1106 only if that would change implementation; both branches receive the one-page XGO correction. No user action needed now.
2. Verify the exact binary and source diff of the display patch; one-page C++ host-verified transmission and original 12-slot controller untouched.
3. Do not distribute a speculative `USB_DP_PULLUP`/active-HIGH or Frankie wiring tweak. A first-slot physical false LOW cannot be corrected by a software debounce in the button mapper without suppressing genuine presses.
4. Do not claim OLED pagination fixed ghost JUMP or all held LP behavior. A future separate electrical-timing experiment must distinguish host-side first-sample false LOW from malformed later serial slots.

**Evidence classification:** HW = user observations and historical captures; BIN = original MIPS scanner + RP2040 linked disassembly; SRC = pinned C++ code; MODEL = calculated I2C transfer times and synthetic timing; OPEN = actual current cable voltage, root of remaining ghost JUMP, whether the LP triple action was game-native or serial.

## Verified completion — fast C++ regression and full linked ARM firmware

The isolated OLED scheduling patch is now compiled and packaged, **but not yet hardware accepted**.

**Fast CI PASS:** [run 40107598212](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40107598212), source commit `cce1b948d1af9b7cbf0138c802ec63426155bbe2`, compiled *actual modified* `drawBuffer()` as host C++ and verified SSD1306 24 sequential page transfers, SH1106 16, address/data/page order, 129/131 byte transaction limit in XGO, original 1025/8×131 byte behavior in non-XGO modes. Also all previous 4096-mask physical GP2040-to-serial tests PASS.

**Full linked Cortex-M0+ CI PASS:** [run 40107598214](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40107598214). Exact protected transparent source `cccb985a05baa8bb9078b6e336eb5f991c1a7a8f`, exact OLED user layout `d15cfdc4953647c9d67e7467e244bf5da7233d76`, pinned upstream original SSD1306 `ecc750d00324a6da368f6d78d9afa40c4eb0e632`, new paged OLED `e441ecc441a1d495413fbd56171a9a72e7321883`. Linked `emit_frame()` still at SRAM `0x200000F0`, 728 bytes; audit traversed 161 IRQ-masked instructions, **zero calls and zero XIP** in reachable masked paths.

**Additional byte-level disassembly comparison:** downloaded *both* original transparent and paged-OLED linked ELF disassembly artifacts. The critical ARM Thumb instruction encoding sequence from `0x20000156` through `0x20000260` (133 instructions) is **byte-for-byte identical**. The code outside the masked interval contains expected relocated `____atomic_fetch_add_4` diagnostic veneers (the new OLED modifies unrelated ELF layout), not a change to the 12-slot responder. Treat this as strong BIN preservation of the timing-critical logic, not physical waveforms.

**New standalone UF2:** `XGO-Transparent-Controller-PAGED-OLED-HARDWARE-UNVERIFIED.uf2`, **2,515,968 bytes**, SHA-256 **`5dcc28132ca54293a3d27dc2a452269bc47a1e7f141bd49c2c7e296918071b5b`**, 4,914 UF2 blocks. Actual GitHub artifact ZIP was downloaded and opened in the execution container; UF2 magic, SHA-256 checksum vs `SHA256SUMS.txt` and `PROVENANCE.json`, source/UI Git blobs, and file count all checked. [GitHub packaging artifact 12565735941](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40107598214) and separate ELF artifact ID `12565402520`. Source commit from manifest is pinned to `cce1b948d1af9b7cbf0138c802ec63426155bbe2`.

**User-facing evidence discipline:** New firmware is a focused remedy for Core0's long synchronous OLED stall. It is not demonstrated on the user's device, and its ability to prevent new missed punches is a hypothesis grounded in SRC/time bounds but not HW proven. It does NOT establish a fix for the observed intermittent Contra ghost JUMP or an explanation for precisely three SFII rapid LP attacks. Preserve the already successful transparent-controller UF2 (`94ea7228c774a67e8252e7e09d94938530e5d74572d985332e6840ae09fe8b84`) as the primary rollback. Do not revert to Test44 pulse semantics.
