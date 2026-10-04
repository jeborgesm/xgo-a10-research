# RP2040 native connector raw-pad audit

## Scope
Software-only stock Raspberry Pi Pico. The onboard Micro-USB connector is treated only as conductors. No USB protocol, TinyUSB, HID, external PCB, or connector modification is in scope.

## Hardware-proven reference
The GP26/GP27 P2 Contra responder proves the XGO contract: observe host CLOCK; DATA is LOW when asserted and Hi-Z when released; serialize 12 positions at the host cadence.

## RP2040 raw PHY primitives [SRC]
Pinned pico-sdk commit 079c6f39023649b154152db30f1d781e884879bc defines:
- RX_DP / RX_DM as DPP/DPM pin state.
- TX_DIFFMODE=0 as single-ended mode.
- TX_DP/TX_DM as independent single-ended values.
- TX_DP_OE/TX_DM_OE: 0 Hi-Z, 1 driving.
- Each TX value and OE has a distinct override-enable bit.
- RX_PD and TX_PD each have explicit power-down override controls.
- DP/DM pull controls are independently overrideable.

Therefore a stock RP2040 exposes the necessary raw electrical primitives in principle. This is not USB protocol operation.

## Concrete defect in P3-P5 [BIN/SRC]
P3-P5 asserted TX_DP_OE_OVERRIDE_EN / TX_DM_OE_OVERRIDE_EN and wrote TX OE, but did not assert TX_DP_OVERRIDE_EN / TX_DM_OVERRIDE_EN. Thus the intended LOW/high-Z DATA primitive did not take complete manual ownership of both output value and output-enable. These tests cannot be treated as a faithful raw-pad equivalent of the proven GPIO responder.

## Muxing audit [SRC]
Raspberry Pi's own RP2040 B0/B1 enumeration workaround demonstrates two distinct low-level routes:
- TO_PHY: physical USB PHY path.
- TO_DIGITAL_PAD: GPIO15/16 debug/digital-pad injection path into the USB controller.
The workaround explicitly says GPIO15 is used because there is no other way to force the input path for that erratum. It demonstrates digital-pad -> controller injection, not physical connector -> GPIO SIO/PIO. Do not assume GPIO15/16 can read the connector contacts.

## Required raw-pad invariant
Before another hardware candidate is issued, its initialization must establish and document:
1. USB protocol/SIE does not own transmission.
2. TO_PHY selects the physical pads.
3. RX powered.
4. TX powered.
5. TX_DIFFMODE=0 and override enabled.
6. TX_DP=0 and TX_DM=0 with BOTH value overrides enabled.
7. TX_DP_OE=0 and TX_DM_OE=0 with BOTH OE overrides enabled.
8. PHY pullups/pulldowns disabled under explicit overrides.
9. CLOCK candidate is never driven.
10. DATA assertion changes only its OE: 0=Hi-Z, 1=drive preloaded LOW.

This is the dedicated-pad analogue of gpio_put(DATA,0) followed by direction/OE switching used by the hardware-proven responder.

## P5 result [HW]
P5 returned four blinks, no scripted movement, only intermittent slot-0/jump artifact. Because P5 did not satisfy the complete raw-pad invariant above, this is evidence that P5's configuration failed to observe/classify the bus, not proof that the stock Pico cannot expose the proprietary XGO signals.

## Next candidate gate
Do not create another fixed-button probe. The next hardware image, if offline audit closes cleanly, must:
- establish the complete raw-pad invariant;
- passively characterize both physical receivers first;
- retain a multi-state LED diagnostic;
- only activate output after a valid repeated XGO frame structure is recognized;
- then run the proven multi-button Contra sequence using LOW/Hi-Z DATA semantics.
