# XGO frame acquisition — Test02 design decision (offline)

Evidence: `tools/rp2040-xgo-native-contra/main.c` (hardware-proven loose-wire Contra P2 responder), `integrations/gp2040ce-xgo-test01/src/drivers/xgo/XGODriver.cpp`, pinned upstream `src/gp2040.cpp` at `3d1f32f7d02d418826b725b60208278d3be878c3`. **No GP2040-CE XGO hardware validation yet.**

## Verified protocol contract

Caveman and Test01 share: wait for host DATA LOW (load/reset), then DATA HIGH within 12 us; immediately drive slot 0 (R); for slots 1–11 wait DM falling, update DP sink/release, then wait DM rising; consume trailing falling edge and release DP to high impedance. Slot order: R, Y, X, L, A, B, SELECT, START, UP, DOWN, LEFT, RIGHT. Edge timeout 12 us; acquisition timeout 20,000 us. Caveman's 20 ms wait was appropriate in a dedicated tight responder loop, **not evidence that 20 ms per call is acceptable in GP2040-CE's shared main loop**.

## Why a short polling timeout is unsafe

A shorter `wait_data(false)` limits one stall but creates blind intervals while GP2040-CE processes buttons, OLED and add-ons. Since slot 0 is sampled immediately after DATA rises, catching an arbitrary subsequent clock edge cannot recover the frame. The source evidence does not provide a measured host poll interval, DATA-low pulse width, or margin between DATA release and slot 0. No safe timeout or sampling cadence can be computed from the current source alone.

## Candidate mechanisms

| Strategy | Main-loop latency | Acquisition confidence | Risks / gate |
| --- | --- | --- | --- |
| Shorten 20 ms timeout in `process()` | Bounded per call | **Unproven** | May miss load pulses; do not ship as Test02 fix |
| Main-loop cooperative state machine | Low | **Unproven** | Main loop may not run during load edge or slot-0 deadline |
| Dedicated core | Low | Potentially strong | GP2040-CE already uses core1; must map ownership, data exchange and scheduling first |
| RP2040 PIO edge capture/response | Low | Potentially strong | USB DP/DM are native USB PHY signals, not ordinary GPIO; no evidence PIO can sample this PHY path directly |
| USB PHY interrupt/event capture + tightly timed responder | Low outside frame | **Research needed** | Must prove accessible native PHY interrupt/event mechanism and latency; no assumptions |

## Decision

**Do not implement a speculative Test02 timeout reduction.** First find measured XGO host load/clock timing in existing artifacts or instrument the hardware-proven responder in an isolated test (without altering GP2040-CE), and inspect GP2040-CE core1 and USB host ownership. If an independent edge-capture mechanism is unavailable, an architecture that blocks only while an actual load is pending must still prove it can detect that load with no blind spot.

## Proposed acceptance gates

1. Capture/derive min/max load pulse width, load period, DATA-release-to-slot0 delay, and DM edge interval (with provenance).
2. Prove no loss of valid 12-slot frames under simultaneous GP2040-CE OLED/add-on/profile activity.
3. Establish bounded no-console behavior, without busy-waiting for 20 ms on every main-loop pass.
4. Preserve XGO PHY sink/release semantics and all 12 mappings.
5. Confirm Web Config and BOOTSEL recovery with XGO mode selected; retain rollback UF2.
6. Keep Test01 as reference and build a separately named **Test02-UNTESTED** only after design evidence closes.

## Open question

Source alone cannot prove whether native USB PHY offers a usable interrupt for the XGO load signal, nor whether GP2040-CE core1 can be repurposed safely. Those are explicit investigation tasks, not assumed capabilities.
