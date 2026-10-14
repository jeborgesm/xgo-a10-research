# Test16 HK slot-0 host binary audit — 2026-10-13

## Evidence
BIN: supplied `XGoAnalisis.zip`, `bios/bisrv.asd`, little-endian MIPS32 at file offsets 0x35D804–0x35D920.
SRC: `integrations/gp2040ce-xgo-test01/candidates/test16-offline/XGODriver.cpp`.
HW: Test16 user report: HK quick tap becomes MP; held HK eventually appears, repeats; directions relatively smooth. Test23 moved slot-0 write ahead of diagnostics but did not fix tap.

## BIN — exact host slot-0 sequence
- 0x35D808: `lw a1,0(s8)` where s8 is GPIO register base+0x54.
- 0x35D810–0x35D818: clear bit0 and write to GPIO +0x54: host drives DATA low for LOAD.
- 0x35D824: `jal 0x30fed0`, argument 4 in delay slot.
- 0x35D834–0x35D844: clear GPIO bit15 at DATA stream 1 output-enable register, releasing LOAD.
- 0x35D858–0x35D864: clear bit0 at DATA stream 2 output-enable register, releasing LOAD.
- 0x35D870–0x35D874: **read DATA stream 1 bit15 (slot 0)**.
- 0x35D890–0x35D894: **read DATA stream 2 bit0 (slot 0)**.
- 0x35D8B0–0x35D8BC: drive shared CLOCK bit7 low for the **next** slot.
- 0x35D8C8: call counter delay with argument 2.
- 0x35D8D8–0x35D8E4: drive CLOCK high.
- 0x35D8F0–0x35D8F4: read stream 1 bit15 (slot 1).
- 0x35D908–0x35D90C: read stream 2 bit0 (slot 1).

## Consequences
**BIN confirmed:** slot 0 is sampled after the host releases both LOAD data lines and **before any CLOCK-low transition**. Slots 1+ are sampled after the corresponding CLOCK-high transition. The physical 3P/R1/RB button maps to GP2040 mask bit 0 in Test16.

**SRC confirmed:** Test16 waits for DATA-high on the same line before asserting an active-low slot-0 bit. This leaves only the host's post-release instruction window for RP2040 to observe the line high, assert DATA low and settle before the host reads it. Test23 removes a timestamp read after detection but did not fix HK in HW.

**INF:** first-bit timing margin and/or LOAD-edge observation are credible causes of unreliable HK. Host may sample slot0 before RP2040 asserts it; this is not yet a measured waveform or a proven mapping of the reported MP action.

**OPEN:** measured timing margin from LOAD release to first read, GP2040 responder assembly and physical electrical capture; game attack-to-serial-slot mapping.

## Safety
Do not pre-assert DATA while waiting for LOAD-high: the responder uses the same DATA line for LOAD detection and could prevent the high transition. Do not alter slot1–11 clock train or mappings to compensate for the slot0 problem. Test16 is protected playable fallback. No new UF2 from this audit.
