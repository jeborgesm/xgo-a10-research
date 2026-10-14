# Test16 slot-0 responder latency — source audit

## Evidence
SRC: `integrations/gp2040ce-xgo-test01/candidates/test16-offline/XGODriver.cpp`.
BIN: supplied `XGoAnalisis.zip`, `bios/bisrv.asd`, scanner offsets 0x35D824–0x35D894.
HW: Test23 did not fix quick HK tap -> MP.

## New SRC finding: latency *before* detecting LOAD release
Test16 enters `emit_frame()`, waits for LOAD low, disables interrupts, performs `published_mask.load(memory_order_acquire)`, samples `time_us_32()`, and calls `wait_data(true, EDGE_TIMEOUT_US)`. That function itself samples `time_us_32()` and loops reading `usb_hw->phy_direct` while calling `time_us_32()` for timeout checks. It does **not** immediately drive DP when RX_DP changes high; it returns to `emit_frame`, where Test16 calls `time_us_32()` once more, calculates `low_duration`, initializes diagnostic locals, and finally performs the DP OE write for slot0.

Test23 moves the DP OE write ahead of the *post-detection* timestamp/diagnostics, but leaves the entire `wait_data(true)` polling loop and return path unchanged. This makes its failed hardware result compatible with latency arising from the poll/return path, rather than disproving all slot0 timing hypotheses.

## Host BIN reminder
Stream 1 release at 0x35D844, first sample at 0x35D870. Stream 2 release at 0x35D864, first sample at 0x35D890. The latter release is later; intervening helper calls mean instruction counts alone cannot be converted to microseconds. Physical stream identification OPEN.

## Candidate direction (not implemented)
A bounded fast-path for *only slot0* could poll `usb_hw->phy_direct` directly with a precomputed absolute deadline and write DP OE immediately on observing RX_DP high, eliminating the `wait_data` call/return and per-iteration `time_us_32()` overhead. Such a change must preserve LOAD-low acquisition, failure rearm, mask snapshot, all slots1–11 and directions. Before firmware, compile/disassemble candidate and Test16 and check generated instructions, not just source-level intent.

## Evidence discipline
BIN: host sampling order verified.
SRC: responder poll/return/diagnostics ordering verified.
INF: responder detection latency may cause slot0 failures.
OPEN: physical stream, actual setup time, compiled cycle counts and cause of MP substitution.
No UF2 built; Test16 unchanged.
