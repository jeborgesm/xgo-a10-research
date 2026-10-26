# XGO universal controller transport: HC15xx GPIO startup and RP2040 DP-pullup engineering gate

**Research date:** 2026-10-26. **Branch:** `research-gp2040ce-xgo-integration`. **Task:** reliable wired GP2040-CE physical button transport in all games; not ROM/keymap investigation. **Outcome:** original XGO binary startup verification plus HC15xx vendor-family GPIO code and original RP2040 USB PHY reference. **Status:** DATA released-HIGH bias strength, board resistor and analog sample timing still OPEN. No new firmware, UF2, XGO BIOS or cable modification.

## 1. What is now confirmed directly in the exact XGO binary [BIN]

On mounted original `XGoAnalisis.zip/bios/bisrv.asd`, SHA256 `869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf`, locally checked **eleven exact little-endian MIPS words** in the stock controller **startup** routine, additionally to the previously verified per-frame LOAD:

- `0x8035DEB8: lui s2,0xb880`; `0x8035DEC0: ori s1,s2,0x0058` sets `s1=0xb8800058` (L GPIO direction register).
- `0x8035DF2C: lw s6,0(s1)`; `0x8035DF30: addiu ra,zero,-2`; `0x8035DF38: and s3,s6,ra`; `0x8035DF3C: sw s3,0(s1)` explicitly clears **L0 direction bit**, making the external Handle channel an INPUT at initialization.
- Separate `0x8035DF08` to `0x8035DF18` clears **B15** direction for native P1.
- Per-poll scan is separate: it temporarily sets L0 OUTPUT, drives OUTPUT latch LOW to establish LOAD, then returns L0 to INPUT at `0x8035D864` and reads L0 at `0x8035D890`, before first CLOCK.

The new [hash-locked read-only startup verifier](../tests/verify_original_l0_startup_ownership.py) pins these eleven words; its underlying original image/opcode comparisons were run locally and passed. This verifies **output ownership and direction**, not GPIO pad-level pull configuration. Neither startup nor scanning instructions alone prove an internal pull-up is disabled, or that no external resistor exists.

## 2. Strongest obtainable sibling source evidence [UP/SRC]

Read live **HC15xx HCRtos source** from `bnister/sf2000_hcrtos`, branch `retroarch` (SF2000 family comparator, NOT exact XGO board design):

- [`components/kernel/source/drivers/gpio/gpio.c`](https://github.com/bnister/sf2000_hcrtos/blob/retroarch/components/kernel/source/drivers/gpio/gpio.c), Git blob `8b73fe1b0bc7866140928345ccdc6223e90829b5`, `gpio_configure()` calls `pinmux_configure(padctl,0)` and changes the GPIO DIR register to input/output. It does NOT invoke or expose a pull-up API there.
- [`components/kernel/source/drivers/pinmux/pinmux.c`](https://github.com/bnister/sf2000_hcrtos/blob/retroarch/components/kernel/source/drivers/pinmux/pinmux.c), Git blob `1203c5c9f6158603bdf77a1d0779cb202472fc14`, writes an **8-bit mux value per pin** into `PINMUXL/B/R/T`; this is pin-function selection and possible pad control, but bits other than the documented mux selectors were NOT fully audited, so do not assert it cannot influence electrical bias.
- [`components/kernel/source/include/uapi/hcuapi/gpio.h`](https://github.com/bnister/sf2000_hcrtos/blob/retroarch/components/kernel/source/include/uapi/hcuapi/gpio.h), exposes GPIO direction and IRQ edge modes but no named GPIO pull-up configuration.
- [`components/kernel/source/include/uapi/hcuapi/pinmux/hc15xx_pinmux.h`](https://github.com/bnister/sf2000_hcrtos/blob/retroarch/components/kernel/source/include/uapi/hcuapi/pinmux/hc15xx_pinmux.h), Git blob `56800f26a21cabddec97ef511a3654eae5ea737d`, declares `PINMUX_L00_GPIO = PINMUX_FUNCTION_SEL0`.

**Interpretation boundary:** The common-family GPIO driver supports **no explicit pull request in ordinary GPIO configuration**. This still does NOT prove the XGO lacks an on-board pull-up or any chip-default pad bias. It does NOT prove XGO uses this exact HCRtos GPIO driver at runtime: the XGO original firmware performs its own register operations. The user's existing chassis photos show outer device and partial internals through the shell but not a board-specific continuity trace or a readable pull-up resistor connection.

## 3. RP2040 PHY pull-up is not a harmless weak GPIO input bias [UP/SRC]

The actual protected `offline-test44-transparent-controller/XGODriver.cpp` has `usb_hw->phy_direct=0` with `USB_USBPHY_DIRECT_OVERRIDE_DP_PULLUP_EN_OVERRIDE_EN_BITS` set, deliberately requesting **DP internal pull-up OFF**. With `TX_DP=0` and OE toggled between disabled and enabled, the controller puts LOW for pressed and leaves DATA Hi-Z for released. The RP does not provide released-HIGH voltage.

Raspberry Pi [SDK 2.3.1 USBPHY_DIRECT definitions](https://github.com/raspberrypi/pico-sdk/blob/2.3.1/src/rp2040/hardware_regs/include/hardware/regs/usb.h) confirm `DP_PULLUP_EN`, `DP_PULLUP_HISEL` and separate override enables. RP2040 datasheet USB SIE also specifies **USB pull-up resistances of approximately 1.2 kΩ or 2.3 kΩ**, depending on selection. It is therefore **NOT** a weak tens-of-kilohms GPIO pull-up intended for arbitrary proprietary shift buses.

**Illustrative design calculation only:** At the earlier measured ~3.15V XGO supply and an ideal 0V LOAD driver, an ideal 2.3kΩ pull-up would demand ~1.37 mA, and a 1.2kΩ pull-up ~2.63 mA, while XGO actively asserts its LOAD LOW. Those are R/V bounds for example nominal resistances **not measured actual RP pull-up current, actual pad voltage or XGO L0 sink capability**. Host GPIO electrical absolute limits, resistor network topology, protection diode paths and Frankie's special two-pad bridge remain unknown. The historical forced **DM** pull-up override affected CLOCK and actually froze XGO; this does **not** demonstrate that a **DP** pull-up would do the same, nor does it authorize blindly changing DP.

## 4. Three separate failure mechanisms, and today's prioritization

**Ghost button with zero real input:** The host-side L0 DATA line might not reach reliable digital HIGH by the *actual MIPS early read* after LOAD release. This is a viable direct mechanism even if GP2040's published mask is zero and no CLOCK timeout is recorded. Both software sources show that the two connected ends do not actively drive the released level. Historical P3 native PHY receiver-only and probe-loading induced ghost actions, although this was with a different cable.

**Wrong or held buttons:** A missing RP-observed CLOCK edge (or host-stretched phase) can move a truly held bit into another slot and fail at terminal S12; actual current Frankie edge corruption is not measured.

**Dropped taps:** A long Core0 OLED full-frame synchronous I2C write can exceed XGO host poll cadence and delay physical-button sampling. Isolated short one-page OLED candidate B is already compiled but never flashed or hardware-proven; it would address scheduling, NOT idle phantom inputs.

**Negative user HW:** Native XGO R RELEASED → HELD → RELEASED changed the scanner's path but **spontaneous P2 jumps continued at about the same rate**, so four MIPS instructions of sample-window difference is **not a supported repair lever**.

## 5. Actionable controlled repair gate, without gambling with working hardware

Do **NOT** (a) change XGO GOLD BIOS or pinmux based on a sibling register, (b) enable strong RP USB DP pull-up without board load/supply evidence, (c) actively drive DATA HIGH against XGO's LOAD LOW, (d) alter Frankie pad-2/pad-4 bridge, (e) change CLOCK wait timeout in hopes of fixing idle ghost, or (f) suppress button maps as a workaround.

A valid **single-variable electrical remediation** must first have:

1. **Pin/supply ownership:** verify which physical Frankie conductor reaches XGO L0 DATA and the true electrical reference/supply. Existing photo's pad numbers are physical observations, NOT canonical USB signal IDs.
2. **Bias source measurement:** obtain a DC high voltage/reference under controller idle, and with a high-input-impedance instrument compare rise/recovery on a host LOAD transition at an access point that has been qualified not to alter jumping. Critical proof is analog DATA HIGH relative to XGO input read, **not merely high by first CLOCK falling**.
3. **Electrical ceiling:** establish supply rail, current the XGO LOW driver is specified/can safely sink, RP PHY pull-up equivalent under proposed setting, and backfeed/ESD routes through Frankie bridge.
4. **One isolation at a time:** if weak/insufficient HIGH return verified, compare an appropriately limited external pull-up/buffer or explicit DP pull-up variant while keeping all twelve raw slots and current CLK serializer identical, plus known-good rollback. If CLK itself is corrupt while DATA is clean, that is a separate controller/host-timing fix.
5. **Acceptance:** idle produces zero false bits across long scans, all physical buttons/holds transmit their own bit without ghost or phase substitution, P1/P2 physical routing reliable, startup/power cycles safe; no visual game-specific hacks.

**This is an engineering gate, not a request for the owner to attach a new scope or perform an unsafe short now.** Earlier 10MHz P0 digital data did return HIGH with 0.9–1.3µs margin before CLOCK, confirming some source of HIGH under the *earlier* loose-wire setup, but first-bit voltage on *current* Frankie V2 Jr is not proven. We must not label the line floating based solely on code.

## 6. Protected state

XGO GOLD `bios/bisrv.asd` SHA256 `75f858b6d9a1eb81235ae9e9c9b449a6a3052ad4365e5411b8ce041075e99d6b`. Transparent A GP2040 source Git blob `cccb985a05baa8bb9078b6e336eb5f991c1a7a8f`, UF2 SHA256 `94ea7228c774a67e8252e7e09d94938530e5d74572d985332e6840ae09fe8b84`. Paged OLED B UF2 SHA256 `5dcc28132ca54293a3d27dc2a452269bc47a1e7f141bd49c2c7e296918071b5b` unflashed. **No changes** to their underlying binaries or Frankie cable. Owner goal remains **all-game controller reliability**, not Contra-specific behavior.
