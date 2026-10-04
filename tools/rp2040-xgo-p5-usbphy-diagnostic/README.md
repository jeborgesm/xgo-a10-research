# P5 native-Micro-USB diagnostic responder
One-flash diagnostic replacing fixed-button probes. Passive phase independently classifies DP and DM for repeated 12-edge frames separated by >100 us. LED: 1=boot, 2=DP clock classified, 3=DM clock classified, 4=no unique 12-pulse clock. Only a DP-clock classification enters active mode, cycling RIGHT, LEFT, DOWN, R/jump, idle for about one second each. During successful frame emission the LED toggles at frame cadence. No TinyUSB; no active-high bus drive.

## Hardware result [HW]
P5 UF2 SHA-256 `9145fdeedfa2af63dd4618d3e045ebe92001e9a02cfb1474192bfb1b91a04656`: LED reports 4 blinks (neither native PHY RX_DP nor RX_DM classified the known repeated 12-edge XGO clock structure); no scripted movement; only the previously observed intermittent jump artifact.

Interpretation: this is a receive-path failure before responder timing/serialization. It does not contradict the GP26/GP27 Contra-bot proof: that proof used ordinary GPIO pads physically wired to the Handle conductors, whereas P5 observes the Pico Micro-USB pads through `USBPHY_DIRECT.RX_*`. The next investigation must explain why the native USB receive path does not expose the already hardware-proven Handle clock waveform; do not issue further responder binaries until that electrical/PHY routing gap is resolved offline.
