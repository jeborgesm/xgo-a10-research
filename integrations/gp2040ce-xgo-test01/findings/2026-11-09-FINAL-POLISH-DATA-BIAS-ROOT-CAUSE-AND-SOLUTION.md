# XGO GP2040-CE final-polish decision: correct the released-HIGH DATA bias at the RP2040 PHY

**Date:** 2026-11-09. **Branch:** `research-gp2040ce-xgo-integration`. **Objective:** complete an already usable native wired controller, without altering the XGO GOLD firmware, Frankie V2 Jr wiring, game keymaps or actual physical button holds.

**Evidence codes:** [HW] owner-tested XGO; [BIN] original XGO MIPS instructions; [SRC] protected/controller code; [UP] RP2040 datasheet/vendor register specification; [MODEL] calculated or synthetic expectation, **not** live measurement; [OPEN] not yet resolved.

## Decision in one sentence

The strongest directly actionable repair is to enable the **less-strong, built-in RP2040 USB DP/DATA pull-up (Rpu2; nominal ~2.3 kilohms)** while retaining **LOW / high-impedance** bit signaling, the hardware-accepted Polish01 **paged OLED**, the original twelve button slots, and the original 18us clock synchronization. **Only one hardware register value changes.** This adds **no physical resistor** or wiring. The on-console outcome remains [HW OPEN] until the owner's acceptance test.

Candidate: [Polish03 Rpu2 `XGODriver.cpp`](../candidates/offline-polish03-dp-rpu2/XGODriver.cpp), Git blob `fb56840992b44477ee671d34a508a68217d1674f`. Protected tested source: `cccb985a05baa8bb9078b6e336eb5f991c1a7a8f`.

## Why this is not another generic diagnostic

### A. Symptoms split into two actual engineering classes [HW]

- The original transparent controller already works; the user completed normal play. **Polish01 paged OLED** improved physical scan response during long Street Fighter II gameplay: no missed inputs noticed, made it through the opponents to the bonus car, destroyed the car with three seconds remaining. This was a genuine improvement, not mere model proof.
- On that **same installed Polish01**, Contra still shows **spontaneous P2 JUMP when no button is touched**. It also repeats JUMP during held A and repeats FIRE during held B **while equipped with the starting single-shot rifle**. The owner specifically corrected the false Machine Gun/auto-fire explanation. Those starting-rifle repeated shots **are defects**.
- Holding an RP GPIO button must remain **electrically held**, not forcibly transformed to a one-shot or timed pulse. XGO/game owns interpretation and can legitimately require continuous levels in many other contexts.

### B. The external connection is the necessary observed condition [HW]

The owner performed a powered-down, same-setup `connected → disconnected → reconnected` comparison:
1. RP2040 + original Frankie V2 Jr connected, GP2040 physically untouched: P2 spontaneous events.
2. External assembly disconnected: no P2 spontaneous events observed.
3. Same external assembly reconnected: spontaneous P2 events returned.

This is **a reproducible connection-dependent symptom**, not a game ROM or P1 merge defect. It does not independently measure DATA voltage, which device generates any false bit, or the RP PHY termination. Earlier **passive native USB-PHY P3** (TX OE OFF) through an ordinary cable also generated unsolicited P2 JUMPs [HW]. P3 cable and firmware are different from current Frankie, so treat it as independent evidence of possible *receiver/cable electrical loading*, not proof the present controller emits no false TX.

### C. Exact original XGO electrical protocol [BIN]

Read-only independently rechecked the original user-supplied `XGoAnalisis.zip/bios/bisrv.asd`, SHA256 `869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf`.

At stock XGO MIPS `0x8035D7C8/CC`, GPIO L0 becomes OUTPUT for LOAD; at `0x8035D818`, L0 is driven LOW; at `0x8035D864`, it switches back to INPUT; at `0x8035D890` it samples DATA **before first CLOCK** to decode the R/slot0 bit. During startup at `0x8035DF2C..3C`, it also clears L0 DIR to INPUT. The DATA line must therefore return to a valid HIGH after host LOAD **before that early read**; otherwise the host can manufacture an asserted first bit when the user did nothing.

The classic P0 digital capture showed eventual DATA HIGH and an approximately **0.9–1.3us interval until first CLOCK fall**; its real host DATA sample comes *earlier* still and is not precisely timestamped. Mean measured inter-clock HIGH from that older capture was only **~1.36us**. **Not a live Frankie analog trace**.

### D. Exact protected RP2040 contract [SRC] — missing local HIGH guarantee

Before Polish03, `raw_init()` sets `usb_hw->phy_direct = 0` then enables `DP_PULLUP_EN_OVERRIDE_EN`. Therefore the RP2040 PHY's internal **DP pull-up is forcibly OFF**. While no button is asserted, `data_release()` clears `TX_DP_OE` to **Hi-Z**; when a button is asserted, `data_sink()` enables its fixed **LOW** output. The XGO and RP both drive LOW when needed; neither actively drives HIGH. HIGH return is furnished by XGO circuitry, pad defaults, passive resistors or other board bias. Its source/strength are *unverified*, and we do **not** claim the original line is literally floating.

This is a valid unclosed **physical-interface contract**: the sender's receiver presence, cable loading and thresholds may degrade HIGH recovery at XGO's immediate read; failure can manifest as idle false presses and intermittent false release/repress when actual held bits are re-sampled.

### E. RP2040 provides the correction internally [UP + model]

Per Raspberry Pi [SDK USB PHY direct register definitions](https://github.com/raspberrypi/pico-sdk/blob/2.3.1/src/rp2040/hardware_regs/include/hardware/regs/usb.h), `USBPHY_DIRECT.DP_PULLUP_EN` activates the DPP/DP pull-up when its corresponding override is enabled, while `DP_PULLUP_HISEL = 0` selects the **weaker Rpu2** branch, rather than the parallel-resistor higher-strength setting. [Official RP2040 datasheet](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf) describes the alternate USB pull-up strengths (~2.3k and ~1.2k).

**The only source change** is replacing `usb_hw->phy_direct = 0;` in the existing `raw_init()` with `usb_hw->phy_direct = USB_USBPHY_DIRECT_DP_PULLUP_EN_BITS;`. Importantly, it sets the desired value **before** assigning `phy_direct_override`. Thus unchanged `DP_PULLUP_EN_OVERRIDE_EN` owns the ON setting. `DP_PULLUP_HISEL = 0`; `DP_PULLDN = 0`; **DM/CLOCK pull-up override remains untouched** (a historical forced DM override froze the XGO), as do all 12 bit positions, TX output value/OE, DATA low-release semantics, CORE ownership and OLED pagination.

**Illustrative current, not a measurement:** 3.15V/2300Ω ≈ 1.37mA when XGO pulls DATA to ideal LOW. At RP 3.3V it is ≈1.43mA. This is *much less* than an active-HIGH push-pull output but is a real load on XGO's asserted LOAD/LOW. **Exact HC15xx L0 sink rating and the electrical details of Frankie's bridged micro-USB connector remain OPEN; avoid claiming absolute safety from an unmeasured circuit.** No arbitrary physical resistors or soldering; the RP2040 already contains this resistor.

**Illustrative RC, not measured timing:** if effective line C were 50–200 pF and the enabled branch were ideal 2.3kΩ, its RC constant is ~0.115–0.46us. Time to reach a hypothetical 70% logic HIGH is ~0.14–0.55us. The actual host threshold, equivalent cable capacitance, resistor tolerance and mixed bias network are unknown. This merely explains why local DP bias is *capable of improving* the exceptionally short read/clock windows, without guaranteeing it does.

## Why *not* choose previous proposals [engineering ranking]

| Approach | Status | Decision |
|---|---|---|
| Keep current Polish01 | HW-playable, no missed press noticed, but idle ghosts/held unexpected actions | **Protected rollback**, not perfect |
| Polish02 18→48us CLOCK timeout | Full offline ARM build + synthetic host IRQ cases pass; **never user-hardware tested**; no direct impact on idle false LOW | **Do NOT stack on new signal repair**; preserve as later separate fallback only if needed |
| RP input filtering / one-shot A/B pulses | Would hide normal physical holds and break other games | **Rejected** |
| XGO host GOLD BIOS GPIO or timing patch | Modifies a protected boot-critical known-good binary and still wouldn't guarantee DATA voltage | **Rejected** |
| Rewrite Frankie / solder resistor / arbitrary probe | Hardware risk, unnecessary before using available RP internal feature | **Rejected** |
| Turn RP DP USB pull-up on with HISEL = 0 | Directly addresses weak released-HIGH, one register value, low-sink/Hi-Z maintained, no physical modification | **Primary actionable solution, needs live HW pass** |
| Force RP DP actively HIGH | Risk of contention when XGO deliberately drives LOAD LOW | **Rejected** |
| Change RP DM/CLOCK pull-up override | Historical XGO freeze on different ordinary cable | **Rejected** |

## Verification gates and test acceptance

The code is pinned to the current hardware-accepted transparent source, not the untested Polish02. It is checked by [`test_polish03_dp_rpu2_source.py`](../tests/test_polish03_dp_rpu2_source.py), which token-compares original vs candidate after reversing **only** the DP value assignment. It requires the unchanged 18us DATA and CLOCK bound, unchanged `data_sink/data_release()`, published physical mask, all pull-up and pull-down override ownership flags, and no DM pull-up. The existing C++ 4096/4096 button mask and held/released tests, paged OLED I2C source test, full linked SRAM critical path audit, pinned GP2040-CE/Pico SDK revisions and UF2 SHA are required by [dedicated Polish03 workflow](../../../.github/workflows/gp2040ce-xgo-polish03-dp-rpu2-build.yml).

**One final real-game acceptance trial, not another diagnostic firmware:** On GOLD and the untouched Frankie V2 Jr, flash **Polish03 only on RP2040**; if any freeze/boot symptom occurs, power off immediately and restore **Polish01**. Verify (1) several minutes of physically idle P2 with zero spontaneous jumps, (2) initial Contra single-shot rifle, hold B through several seconds with **one** expected shot, then release/repress once and get one more shot, (3) hold A through landing without unintended fresh jump, (4) repeat normal extended SFII play with no missed LP/MP inputs, plus sane multi-button chords. Real game logic may react differently to a continuously held button under some contexts; judge the **starting rifle** and **idle events** as strong witnesses. Do not fabricate test durations or declare final status until owner reports.

**Rollback:** user HW-positive Polish01 paged OLED UF2 SHA256 `5dcc28132ca54293a3d27dc2a452269bc47a1e7f141bd49c2c7e296918071b5b`; transparent A original UF2 SHA256 `94ea7228c774a67e8252e7e09d94938530e5d74572d985332e6840ae09fe8b84`; XGO GOLD `bisrv.asd` SHA256 `75f858b6d9a1eb81235ae9e9c9b449a6a3052ad4365e5411b8ce041075e99d6b`; fixed Frankie 2/4 physical solder pad bridge preserved.

**Limitations / honest status:** This is a tangible transport-level firmware remedy, with a precise physical theory and a pre-existing hardware capability. The prior evidence makes it the strongest currently available direct solution but **does not establish** actual high-voltage rise time, HC15xx sink ceiling, or a measured ghost cause. A passing compiler and model cannot certify a real wired electrical circuit; only the user's XGO behavior can close it. If it is not demonstrably better, return to Polish01 and do not promote it.
