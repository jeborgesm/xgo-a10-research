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
