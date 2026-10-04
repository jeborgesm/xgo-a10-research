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
