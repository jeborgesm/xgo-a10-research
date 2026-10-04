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
