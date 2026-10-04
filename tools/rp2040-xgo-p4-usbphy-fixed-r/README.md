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
