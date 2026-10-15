# Test31 design gate: preserve preceding slot through CLOCK-low (2026-10-14)

## Controlled observations

- **HW** Test28: slot0 HK reliably works; held attacks on other slots repeat/mix.
- **HW** Test29: shortening the falling-edge wait slows repetition but does not eliminate mixing; HK still works.
- **HW** Test30: driving the next slot while CLOCK remains high speeds repetition, breaks HK taps, and leaves mixing. Reject Test30.
- **SRC** Test28 loops `wait_clock(false) -> data_sink/release(next slot) -> wait_clock(true)`.
- **SRC** Test30 loops `data_sink/release(next slot) -> wait_clock(false) -> wait_clock(true)`.

## Timing boundary and non-overlap invariant

Test30 can change slot1 DATA while slot0 is still being sampled; it violates the invariant that **DATA for ordinal n must not change until the host has finished sampling ordinal n-1**. Its HK regression is consistent with that violation, though not measured electrically.

Any Test31 should preserve Test28's **CLOCK-low first** ordering, with the lowest possible latency from observed low to DATA update, without moving the update into the preceding CLOCK-high interval. But Test29 already attempted a faster falling-edge poll and failed; therefore another speed-only variation without a distinct mechanism would be an unjustified repeat.

## Next actionable controller-only work

Use a read-only static audit of the RP2040 USB PHY `RX_DM` read and `TX_DP_OE` write path, including bus synchronization and actual instruction order from the compiled Test28/Test29 binaries. If a concrete source of jitter or delay emerges, create an isolated Test31 correction; otherwise do not manufacture a candidate. **Do not touch XGO device firmware, emulator, keymaps, or turbo settings.**
