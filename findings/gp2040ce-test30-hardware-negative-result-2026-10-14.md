# Test30 hardware failure — pre-CLOCK DATA setup rejected (2026-10-14)

## HW — user observation

Test30 hardware-tested and **failed**:
- Held-button repeats are **much faster** than Test28.
- HK does **not respond to taps** reliably.
- Held attacks still **mix**.

These are qualitative hardware observations; no numeric cadence measured. Test30 must **not** replace the hardware-proven Test28 baseline.

## SRC — controlled difference

Test30 was copied from Test28. Its one intended responder change moves `if (mask & (1u << slot)) data_sink(); else data_release();` **before** `wait_clock(false, EDGE_TIMEOUT_US)` for slots 1–11, rather than after the falling edge. Test28's slot-0 HK special case is otherwise unchanged. The slot-1 early DATA write can affect the electrical value during the remaining slot-0 clock-high phase, consistent with the observed HK tap regression. This is a plausible timing explanation, **not an instrumented proof**.

## Decision

- **REJECT Test30**; never promote its early-preclock DATA approach as-is.
- **PROTECT Test28** (HK reliable, LED menu restored, remaining held-action issues).
- Test29 also hardware-negative (held repetition slowed, mixing persisted).
- Work only on GP2040-CE controller communication; no XGO BIOS, game, emulator, keymap, or turbo investigations.
- Any future experiment must preserve DATA throughout the preceding slot's sample interval and identify a non-overlapping slot-update window. Do not build another guess without explicit timing rationale.

Test30 source and CI remain archived for negative evidence, not as a candidate to flash.
