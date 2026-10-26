# HW: spontaneous P2 input is reproducibly connection-dependent on current Frankie/GP2040

**Observation date:** 2026-10-26. **Branch:** `research-gp2040ce-xgo-integration`.
**Evidence classification:** [HW] direct owner report; [SRC] transparent RP2040/Caveman code; [BIN] original XGO input scanner; [INF] connection-dependence; [OPEN] specific electrical component, host-decoded word, and voltage. This is an executed hardware experiment. **No new firmware or wiring change.**

## Owner's actual result [HW]

This is the RESULT of [2026-10-26 powered-down external-Handle presence experiment](2026-10-26-HANDLE-CONNECTION-PRESENCE-NO-FLASH-DISCRIMINATOR.md), not another proposed test. User reported, verbatim:

> 1. Connected: Observed spontaneous P2 actions while leaving the controller untouched.
> 2. Disconnected: Did Not Observe spontaneous P2 actions without an external controller.
> 3. Reconnected: Observed spontaneous P2 inputs return.

The previous experiment protocol specified **GOLD Handle=P2**, the *same observable two-player P2 situation*, physically idle RP2040/Frankie V2 Jr, and powering off before each disconnect/reconnect. The user reported each comparison above. Do not invent numeric event counts or rates, precise time windows, electrical measurements, video evidence, or absolute equivalence between the sessions. The user did not explicitly separately reconfirm that P2 remained enabled/displayed while disconnected; that is an assumption of the executed protocol and a residual interpretive limit.

| Condition | RP2040 + Frankie connection to XGO | Owner's observation |
|---|---|---|
| A1 | Attached; GP2040 untouched | Spontaneous logical P2 actions |
| B | Removed from external Handle port | No spontaneous P2 actions observed |
| A2 | Original assembly reattached | Spontaneous P2 inputs returned |

**Most important finding:** In this reproducible comparison, the observed ghost-input behavior **coincided with the presence of the RP2040+Frankie electrical connection** and disappeared when absent. This is stronger causal discrimination than the prior **negative** native-R short/long P2 first-sample-path test, which did not affect P2 ghost action frequency. It rules against an **always-present, connection-independent** software/game fault being sufficient for this symptom in these comparable sessions.

**Not proved:** Which physical contact, DATA-high bias, CLOCK loading, RP firmware state, RP output-enable, physical GP2040 button scan, or XGO port-detect behavior caused the action. Disconnection changes **several variables together**, including cable capacitance/leakage, Pico PHY power/termination, any physical button response, and possible XGO's P2 recognition. Do not say "we proved the resistor is missing" or "the RP transmitter injected a jump bit."

## Strong connection to previous independent experiments [HW/SRC]

1. Earlier receive-only **P3 native RP USB-PHY** test with ordinary cable caused unsolicited P2 jumps even while P3 never called DATA sink [HW]. The current Frankie cable and current A firmware are different; this strongly raises the plausibility of PHY electrical loading without *requiring* active button serialization but does **not** verify passive loading as the cause of the current A2 ghost.
2. In protected approved transparent A [SRC], RP2040 `data_release()` disables DP output-enable, `phy_direct=0` plus DP pull-up override forces RP DP pull-up OFF, `data_sink()` only sources a LOW when a physical bit is present. Thus when actual `published_mask=0`, the source intends no RP-driven press bits. **Current runtime `published_mask` during a ghost is not measured**; software-generated or electrically noisy physical input is not excluded by source intention.
3. XGO original host [BIN] drives external L0 DATA LOW during LOAD and changes L0 to input before reading the first serial bit, then clocks 12 slots. Original/HC15xx code audits do not establish an explicit pull-up or its analog strength. Some HIGH bias exists in previous digital captures, but unknown rise under current Frankie.
4. The user's **native built-in R A–B–A test was negative**; holding native R and executing four extra XGO instructions before external R sample did not change apparent P2 ghost rate. This is a real narrowing, but does not exclude slowly recovering DATA in both branches.

## Revised controller-only fault isolation [INF/OPEN]

**Now deprioritized:** Contra/ROM-specific mapping theories, native-R-dependent four-instruction read timing as the primary lever, and general P1 merge (Handle=P2 already shows ghost).

**Priority 1 — external electrical load and receiver bias:** With the **same RP2040 firmware**, attached USB PHY/cable may change DATA or CLOCK voltage/timing even when no buttons pressed. Inspect cable leakage, bridged pad layout and actual DP RX loading only with verified reference and a measurement that does not itself cause ghost inputs. Existing untouched hardware source doesn't establish the voltage.

**Priority 2 — unwanted transmission while physically idle:** One or more physical/processed buttons might intermittently appear pressed to Core0, or a corrupted RP snapshot / output driver could sink DATA. A future diagnostic that forces the RP DP transmitter *never enabled* while leaving identical Frankie and USB PHY connected would distinguish active transmitting errors from passive electrical presence, if built, compiled and tested as a **separate, reversible** UF2. This specific test has **not been built, flashed or owner-executed**. Historical P3 was an early comparator with a different cable and firmware; it does not supersede this same-cable test.

**Priority 3 — clock loading/edge loss:** RP SRAM loop waits for the XGO native CLOCK; if loaded DATA/CLK means shorter/missed edges, held-button corruption can occur. Do not modify CLOCK timeout blindly; fault class requires current electrical evidence.

**Separate contributor:** Blocking Core0 OLED I2C may miss short taps; paged OLED candidate B remains unflashed and does not address idle phantom input. Keep these as separate effects to avoid claiming a single proven root.

## Concrete next engineering gate

The highest-value single-variable experiment now is the **same Frankenstein cable and XGO setup, but a receive-only RP2040 USB-PHY firmware that never enables DP transmit during the active serial transaction**. If P2 ghost inputs continue even when the RP never drives DATA, the current-wire connection/receiver/line bias is implicated over spurious Core0 button-mask serialization. If ghosts disappear, active low-output behavior, RP frame synchronization and/or source physical-input state become stronger leads. Because the XGO expects 12 encoded slots, this test is about **idle ghost action only**, not validating playable controls; no exact host decoded word is available.

**Safety gate before any UF2:** build receive-only mode as a separately named experimental candidate preserving the same `phy_direct` init as A and same linked Core1 schedule, with actual linked/disassembly evidence that no path can set `TX_DP_OE`. Keep A original UF2 immediately available for rollback. Do **not** modify the XGO GOLD firmware or Frankie pad bridge, enable DP/DM pullups, actively drive DATA HIGH, attach an arbitrary electrical probe, or conflate a subsequent nonresponsive controller with a usable firmware fix.

**Protection:** GP2040 transparent A source Git blob `cccb985a05baa8bb9078b6e336eb5f991c1a7a8f` / user-flashed UF2 SHA256 `94ea7228c774a67e8252e7e09d94938530e5d74572d985332e6840ae09fe8b84`; protected XGO GOLD `bios/bisrv.asd` SHA256 `75f858b6d9a1eb81235ae9e9c9b449a6a3052ad4365e5411b8ce041075e99d6b`. Paged OLED B not flashed.

**Decision:** Connection dependency now **hardware observed**. The electronic source (Pico PHY, cable, physical RP input, or XGO port side) remains **OPEN**. Universal controller reliability stays the goal; **no ROM/keymap investigation**.
