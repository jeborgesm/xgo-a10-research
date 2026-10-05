# P3 native-USB-PHY passive probe

## Question

Can an ordinary cable deliver the proprietary XGO Player-2 CLOCK/DATA bus to the original Pico's native D+/D- pins while the same connector powers the Pico?

## Baseline signatures [HW]

Compare against P0:

- CLOCK: exactly 12 pulses per transaction, about 250 kHz, about 2 us low / 2 us high.
- poll cadence: about 16.03 ms.
- DATA/load: host-low interval about 7-8 us followed by release roughly 1 us before first clock-low.
- P2 idle DATA remains high after release.

## Candidate

`tools/rp2040-xgo-p3-usbphy/`

The candidate is passive by construction. It does not initialize TinyUSB or USB stdio and explicitly overrides local DP/DM pulls and TX output enables to OFF before sampling RX_DP/RX_DM.

## Hardware procedure

1. Flash P3 while Pico is connected normally to the PC.
2. Disconnect the Pico from the PC.
3. Do not attach the old RED/YELLOW/GREEN GP26/GP27 harness.
4. Connect only the ordinary micro-USB cable between XGO Handle Interface and Pico onboard micro-USB.
5. Observe whether XGO and Pico power/boot normally. Do not interpret protocol success from this smoke test alone.
6. For waveform/data proof, use UART GPIO0/1 or an external passive instrument without changing DP/DM loading.

No active DP/DM drive is authorized by this experiment.

## Pass criteria

PASS requires observing the P0 timing fingerprint on native RX_DP/RX_DM. If one line carries the 12-clock burst and the other carries P2 DATA/load behavior, record the assignment and proceed to a separately audited fixed-R native-PHY responder.

If the fingerprint is absent, do not infer a pin assignment from connector convention.

## Build audit

CI run 37177156201 at branch commit `390d84109148606bbc90570bc89181da063f2dd8` completed successfully with Pico SDK 1.5.1.

- configure: PASS
- compile/link: PASS
- linker-map negative audit for `tud_init`, `tusb_init`, and `stdio_usb_init`: PASS (none linked)
- UF2 SHA-256: `d30c4a7a409701876cb16583d8c75f1b949d82949bb5106331d4e0fe768e089d`
- CI artifact: `xgo-p3-usbphy-passive` (artifact id 11293663562)

This promotes P3 from source-only candidate to build-audited passive hardware-test candidate. It does not promote the native USB transport hypothesis to HW proof.

## Hardware result — direct-cable smoke test [HW]

P3 UF2 `d30c4a7a409701876cb16583d8c75f1b949d82949bb5106331d4e0fe768e089d` was flashed to the original Raspberry Pi Pico. The old GP26/GP27 harness was not part of this test; the Pico was connected to the XGO Handle Interface through its onboard Micro-USB connector and an ordinary cable.

Observed on XGO hardware:

- Pico powers from the XGO Handle Interface.
- XGO remains running normally; no freeze.
- Player 2 intermittently performs JUMP without user input.

Interpretation discipline:

- [HW] The direct ordinary cable provides Pico power and does not reproduce the severe freeze seen with normal GP2040-CE/TinyUSB firmware.
- [HW] Merely attaching the native USB-PHY P3 candidate can still perturb the Player-2 input path enough to produce intermittent JUMP.
- [INF] Because the XGO mapper maps raw R/slot0 to the FC/Contra jump action, this resembles the previously observed first-bit/R sensitivity, but this smoke test alone does not identify which native DP/DM line is DATA or CLOCK.
- [OPEN] The source of the residual loading/perturbation must be isolated before any active native-PHY responder is authorized. Possible causes include PHY analog loading/mux state, an incompletely disabled bias, or cable/receiver interaction. Do not call P3 electrically transparent merely because TX OE is disabled in firmware.

Result: **PARTIAL PASS / IMPORTANT POSITIVE TRANSPORT EVIDENCE, but not yet P3 protocol PASS.** The single-cable electrical path is alive enough to affect the real P2 scanner, while the device remains stable.

## Hardware result — P3 onboard-LED classifier [HW]

LED-classifier candidate UF2 SHA-256 `be198f4b9ee66ac166e2f354e9c945f2f0c7b262097b3c09edf14bac708c3772` was tested through the Pico onboard Micro-USB connection to the XGO Handle Interface.

Observed result: **3 blinks repeating (ambiguous/no dominant line).**

This is a valid negative result for the simple edge-count classifier. It does **not** prove that DP/DM lack the XGO transaction. The classifier only compares total falling-edge counts across the entire 65.536 ms capture; DATA transitions and CLOCK bursts, residual PHY loading, sampling aliasing at 1 MHz versus ~2 us half-periods, or line-state behavior can defeat that coarse discriminator. Do not infer a connector mapping from this result.

Next step: replace total-edge dominance with transaction-shape classification against the already hardware-proven P0 signature (12 clock pulses, ~16 ms cadence, DATA/load low preceding the burst). Keep the native PHY receive-only and perform classification only after capture.

## Hardware result — P3 transaction-shape classifier [HW]

Transaction-shape classifier candidate from source commit `0023e9ac73032206492f7d9be529203d819a6c4b`, UF2 SHA-256 `ae34b93f52d05df9a82af937d857e6097feb15ac6a438f6075efa8814c3ceaa0`, was tested through the Pico onboard Micro-USB connection to the XGO Handle Interface.

Observed result: **3 blinks repeating (ambiguous)**. P2 also continued the previously observed intermittent unsolicited jump behavior.

This is stronger evidence that the failure is not merely the first total-edge classifier. Even a classifier looking for the P0-proven ~12-pulse burst / ~16 ms cadence cannot distinguish DP from DM from the native-PHY sampled states as presently configured. The persistent P2 jump simultaneously shows that this PHY configuration is electrically perturbing the real P2 path.

Do not proceed directly to active native-PHY drive. The next offline target is the PHY configuration itself: audit all RP2040 direct-PHY bias/override controls (especially DM pull-up ownership, which P3 has not explicitly overridden), SOFTCON/mux effects, and receive-state behavior. Build a quieter passive candidate before asking for another active-response hardware test.

## Hardware result — P3-v3 explicit DM pull-up override [HW]

Candidate source commit `fe5ab287e090b6b5089b411238d4cf4572a335a8`, UF2 SHA-256 `c3bf7a2fba2b800d37332fcc7c04f9661d33215bb6d8f76eb12067a8cbaafc9f`, added `USB_USBPHY_DIRECT_OVERRIDE_DM_PULLUP_OVERRIDE_EN_BITS` while leaving the requested DM pull-up value zero.

**Observed on hardware: connecting this candidate through the Pico onboard Micro-USB to the XGO Handle Interface froze the XGO.** No blink-classification result is valid from this candidate because the host froze.

This is a decisive regression relative to the immediately preceding P3 classifier, which left XGO running but caused intermittent P2 jumps. Therefore explicit DM-pull-up override is not a safe passive refinement in this configuration. Reject P3-v3 for further hardware use and restore the preceding non-freezing candidate/state before any additional experiment.

The result also means the native USB PHY's DM pull-up ownership/override interacts materially with the XGO Handle bus. Do not infer ordinary USB semantics from that interaction; exact electrical mechanism remains OPEN.

## Hardware result — P3-v4 restored non-freezing PHY baseline [HW]

Candidate source commit `cc2e2003c1d16e8558a9020f145a862f4effe345`, UF2 SHA-256 `db82e7d07a66c725b5bdc7c98df6a916eff977d0ee6f463a8aec73f4dab413bd`, restored the pre-v3 electrical configuration by removing the explicit DM-pull-up override while retaining the transaction classifier and added SIE telemetry.

Hardware observation: **XGO remained running; LED classifier repeated 3 blinks (ambiguous); P2 continued intermittent unsolicited jumping.**

This reproduces the earlier non-freezing P3 behavior and strengthens the controlled A/B result: adding the DM-pull-up override-enable caused the v3 freeze, while removing it restores operation, but the native-PHY receive configuration itself remains non-transparent enough to perturb P2 and does not yet yield a clean DP-vs-DM clock classification.

Do not proceed to active native-PHY drive from this state. The next experiment should target the source of receive-path loading/first-slot disturbance rather than classifier thresholds.

## Hardware result — P3-v5 explicit SIE neutralization [HW]

Candidate source commit `87cb8c2010dbc4e539149e05ed824022bea780e0`, UF2 SHA-256 `412bc244dd1b9353f2a5b14c0e35f3c9004e47957e050a7c758e76057daa6872`, added an explicit `usb_hw->sie_ctrl = 0` while otherwise retaining the non-freezing v4 native-PHY configuration.

Hardware observation: **XGO remained responsive; LED classifier repeated 3 blinks (ambiguous); P2 continued intermittent unsolicited jumping.** Behavior was materially unchanged from P3-v4.

This falsifies the working hypothesis that residual SIE direct-drive/pull/transceiver-control state was responsible for the P2 disturbance. With SIE controls explicitly zero and the documented PHY output enables/pulls already neutralized (except the unsafe DM-pullup override experiment rejected in v3), the remaining disturbance is more likely associated with attaching/enabling the native USB PHY receive path itself or another analog/mux-side effect. Exact mechanism remains OPEN.

## Offline mux-path finding after P3-v5 [SRC/INF]

RP2040 SDK register definitions close an important ambiguity in the native-connector escape-hatch investigation. GPIO15 function-select value 8 is explicitly named `usb_muxing_digital_dp`; GPIO16 function-select value 8 is explicitly named `usb_muxing_digital_dm`. Raspberry Pi's B0/B1 USB enumeration workaround uses GPIO15 function 8 together with `USB_MUXING_TO_DIGITAL_PAD | SOFTCON` to inject a forced DP input state while switched away from the normal PHY. This proves a digital-pad bridge exists for both DP and DM in the RP2040 mux fabric [SRC].

However, the documented workaround demonstrates the bridge in the direction **GPIO15/16 digital logic -> USB controller line-state input**, not the reverse direction **physical USB D+/D- connector -> GPIO15/16 SIO input**. Therefore it does **not** establish a passive way to sample the connector while disconnecting the analog USB receiver [INF/OPEN]. Treating GPIO15/16 function 8 as a connector-input escape hatch would currently be an unsupported direction reversal.

Consequence: do not issue a hardware candidate based on `TO_DIGITAL_PAD` merely to test that assumption. The next safe research step is to establish mux directionality from RP2040 silicon/documentation or a known implementation before another XGO hardware test.

## Native connector receive-path closure [SRC/INF]

A further RP2040 register audit strengthens the conclusion that the direct USB-PHY receive bits are the documented physical-pad observation path: `USBPHY_DIRECT.RX_DP` is described as **DPP pin state** and `USBPHY_DIRECT.RX_DM` as **DPM pin state**, both read-only [SRC]. The same block exposes `RX_PD` specifically as an RX power-down override when its override-enable is asserted [SRC]. No SDK evidence was found for a reverse physical-USB-pad -> GPIO15/16 SIO path; the documented GPIO15/16 function-8 names are `usb_muxing_digital_dp/dm`, and Raspberry Pi's usage demonstrates digital-pad injection into USB line-state logic, not connector sampling [SRC].

This makes the analog/native receiver the strongest documented route for observing physical D+/D- on RP2040 [INF]. Powering that receiver down would defeat the very `RX_DP/RX_DM` observations needed by the current classifier, so `RX_PD` is not a useful passive-sampling fix [INF].

Engineering consequence: stop searching for an undocumented GPIO escape hatch unless new silicon evidence appears. The next experiment should characterize the known receive-path disturbance rather than blindly changing PHY ownership. In particular, exploit the already-proven XGO slot-0 sensitivity and compare physical bus behavior with the native PHY disconnected versus attached before authorizing active native-PHY drive.

## P3-T timing-discriminator experiment design [INF]

The next hardware discriminator should test the emerging slot-0 recovery hypothesis without changing RP2040 USB-PHY register ownership again.

Known timing baseline from P0 [HW]: XGO P2 DATA/load goes low for about 6.8-7.8 us, releases only about 0.9-1.3 us before the first CLOCK low, then presents exactly 12 clock positions. Known behavioral correlation [HW]: both an empty OTG adapter and the passive RP2040 native-PHY attachment preferentially produce an R/slot-0 symptom (the RP2040 case intermittently appears as Contra P2 jump through the established mapper).

Proposed P3-T measurement keeps the proven non-freezing v4/v5 firmware unchanged and uses the already-proven external scope/harness only as a measurement instrument. Observe GREEN (hardware timing-correlated P2 DATA/load) relative to RED reference while the Pico remains connected through its ordinary Micro-USB cable. Capture the load-release -> first-clock region and compare it with the P0 no-native-PHY baseline. Because the DSO-TC3 is single-channel, DATA and CLOCK cannot be captured simultaneously on that instrument; use the known YELLOW CLOCK timing/cadence as the transaction locator and measure GREEN pulse/recovery shape in repeated captures. Do not short conductors and do not connect BROWN to Pico 3V3.

Pass/fail logic: if Pico attachment measurably delays GREEN's return high, produces a slow/partial recovery, or adds a low-going transient specifically in the ~1 us slot-0 aperture, that directly supports receiver loading as the R/jump mechanism [HW]. If GREEN recovery remains indistinguishable from P0 despite reproducible jumping, the hypothesis is weakened and attention should shift to clock-line loading or receiver threshold/classification effects [INF].
