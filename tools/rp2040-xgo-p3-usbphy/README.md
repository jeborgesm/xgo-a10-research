# XGO P3 — native USB PHY passive capture

Purpose: determine whether the XGO Handle Interface CLOCK/DATA transport reaches the original Raspberry Pi Pico's onboard micro-USB D+/D- contacts through an ordinary cable.

Safety properties of this candidate:

- USB controller disabled.
- USB stdio/TinyUSB not initialized.
- DP pull-up forced disabled.
- DP and DM pull-downs forced disabled.
- DP and DM TX output-enable forced disabled.
- TX differential mode forced disabled.
- firmware only reads RX_DP/RX_DM.
- no GP26/GP27 XGO harness is used.

The capture is intentionally self-starting because the Pico is expected to be powered from the XGO cable, so the onboard USB connector cannot simultaneously be the PC serial connection. Diagnostic output is UART-only and is optional for the first electrical/behavioral smoke test.

Capture encoding: each character is one 1-us sample. 0=DP0/DM0, 1=DP1/DM0, 2=DP0/DM1, 3=DP1/DM1. 65536 samples cover ~65.5 ms, enough for about four previously measured XGO ~16.03-ms polls.

Promotion gate: no active native-PHY responder until a passive capture identifies the known 12-pulse ~250-kHz transaction/cadence and DATA/load behavior on DP/DM.
