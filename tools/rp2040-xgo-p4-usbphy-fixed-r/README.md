# XGO P4 native-USB fixed-R responder

Purpose: transplant the hardware-proven P1 fixed-R responder from external
GP26/GP27 wiring onto the Raspberry Pi Pico's own Micro-USB D+/D- PHY.

Evidence-backed first assignment:
- DPM / Micro-USB D-: XGO CLOCK, receive-only.
- DPP / Micro-USB D+: XGO P2 DATA.
- DATA is never driven high. TX_DP remains LOW and only TX_DP_OE changes:
  OE=1 sinks LOW; OE=0 is Hi-Z.
- R is XGO slot 0, asserted immediately after host DATA load/release and released
  on the first CLOCK falling edge.
- 20 us timeout always releases DATA if the expected CLOCK edge is absent.

This candidate intentionally retains the P3-v4/v5 non-freezing PHY ownership
baseline and does not enable the DM pull-up override that froze XGO in P3-v3.

Hardware success criterion: with no GP26/GP27 wiring and one ordinary Micro-USB
cable Pico -> XGO Handle Interface, XGO remains responsive and Contra Player 2
continuously performs the mapped R action (jump).

This is a bounded active experiment, not yet a compatibility claim.

## Hardware result — P4 v1 [HW]

UF2 SHA-256 `5de5f7a05902439f49d0ccd63df213a1547be796641bc120001bebc052cc65be` was tested with **only one ordinary Micro-USB cable** between the Pico's native connector and the XGO Handle Interface; no GP26/GP27 instrumentation was present.

Observed: Pico LED remained solid; XGO remained operational; Contra Player 2 performed the mapped jump action **intermittently, not continuously**.

Interpretation: this is not the fixed-R success criterion. It also does not demonstrate that active native-PHY serialization is absent, because the symptom is indistinguishable at behavioral level from the passive P3 intermittent slot-0 jump. P4 v1 therefore remains inconclusive for active DATA control. The next candidate must make active drive distinguishable from the passive baseline rather than simply repeating slot 0.

## Hardware result — P4 v2 fixed-RIGHT [HW]

UF2 SHA-256 `28bfd9c607fffa8195c13f1a689f355a51ba20def4f1739110de9e023561153a`, size 20,992 bytes, was tested through only the Pico native Micro-USB connector and ordinary cable.

Observed: solid Pico LED; XGO remains responsive; Contra P2 still performs only the same occasional jump seen under passive P3/P4-v1; **no RIGHT movement**.

Conclusion: the DPM-as-CLOCK / DPP-as-DATA active assignment did not produce the requested non-slot-zero action. Because the passive slot-zero artifact remains unchanged, proceed to the controlled reciprocal native-PHY assignment: DPP as CLOCK input and DPM as DATA LOW-sink/Hi-Z. Do not interpret the occasional jump as active responder success.

## Hardware result — P4 v3 reciprocal fixed-RIGHT [HW]

UF2 SHA-256 `fe58d4811fdd557a32e9492503d40a26eedbf86d638911cef8e9811fcb763692`, size 20,992 bytes, tested through only the Pico native Micro-USB connector and ordinary cable.

Observed: no RIGHT movement. XGO/P2 continues to show only the same occasional jump behavior seen in passive P3 and P4 v1/v2.

Conclusion: swapping the assumed native PHY roles (DPP=CLOCK, DPM=DATA) also fails to produce active non-slot-zero input. Therefore the simple DP/DM assignment question is closed: neither direct USBPHY TX_OE assignment, as currently configured, reproduces the proven external-GPIO responder. The persistent occasional slot-0 jump is a passive/native-PHY coupling artifact and must not be counted as active transport.

Next direction: investigate the RP2040 native USB PHY's direct-drive ownership/mux requirements for single-ended TX/OE. Do not continue blind DP/DM swapping and do not return to Frankenstein connector work.

## Hardware result — P4 v4 explicit PHY-power ownership [HW]

UF2 SHA-256 `436b1e758df9e080f60afd84480eb03aa59c62bc65fdd43770531e70b92c42b5`, size 20,992 bytes. Source `0bf3dd2e053e7e4d0b669be866e0e4175bf09816`.

Observed through only the Pico native Micro-USB connector and ordinary cable: no RIGHT movement; behavior remains the same occasional P2 jump seen in passive P3 and P4 v1-v3.

Conclusion: explicitly overriding TX_PD=0 and RX_PD=0 does not make the USBPHY_DIRECT single-ended TX/OE path produce commanded XGO input. Reject PHY power ownership as the missing condition. The repeated unchanged slot-0 jump remains a passive/native-PHY coupling artifact, not active responder proof.

Next: audit/test the separate SIE direct-bus-drive path (SIE_CTRL.DIRECT_EN/DIRECT_DP/DIRECT_DM) as a controlled electrical primitive rather than continuing USBPHY_DIRECT configuration permutations.

## Offline audit correction — P4 v3/v4 reciprocal tests invalidated [SRC]

Full source review found a material implementation error: v3/v4 documentation/banner claimed DPP= CLOCK and DPM=DATA, but the clock wait path still called `dm()` / read `RX_DM`. At the same time those versions drove DPM through `TX_DM_OE`. Thus v3/v4 attempted to observe CLOCK and drive DATA on the same DPM conductor. Their negative hardware results remain real observations but do **not** test the intended reciprocal DP/DM assignment and must not be used to reject DPP=CLOCK / DPM=DATA.

P4 v5 commit `81c929e4af9c072771269b8ae1452825a0f6c59f` corrects the clock read to `RX_DP` while retaining DPM LOW/Hi-Z DATA drive and the slot-11 RIGHT discriminator. This is the first valid reciprocal active-native-PHY candidate.
