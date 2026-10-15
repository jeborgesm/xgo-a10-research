# Test28/29/30 controller-only instruction-path audit (2026-10-14)

## SRC: exact responder paths

**Test28** uses `wait_clock(false, EDGE_TIMEOUT_US)` before each slot1–11 DATA write. The helper initializes `uint32_t t = time_us_32()` and repeatedly tests `clock_level() != level`, with a `time_us_32()` timeout call **only while the requested level has not been reached**. Therefore, on the successful falling-edge iteration, the C++ expression can exit without calling `time_us_32()` again.

**Test29** replaces this with:

```cpp
const uint32_t fall_start = time_us_32();
while (clock_level()) {
 if ((uint32_t)(time_us_32() - fall_start) > EDGE_TIMEOUT_US) break;
}
if (clock_level()) { clock_timeout = true; failed_slot = slot; complete = false; break; }
if (mask & (1u << slot)) data_sink(); else data_release();
```

This adds a **second explicit `clock_level()` read after the edge-detection loop**, before the DATA update. It is not a pure removal of timekeeping overhead: Test28 already short-circuits the timeout check on the successful edge. Test29's additional GPIO read may increase the edge-to-DATA delay or observe a different phase if CLOCK is narrow. The source alone cannot establish the compiled instruction count or causality; the earlier claim that Test29 necessarily drives faster is **not supported**.

**Test30** writes next-slot DATA **before** waiting for CLOCK low. This can overwrite previous-slot DATA while CLOCK is high, consistent with HK tap regression. HW rejects it.

## Specific follow-up (controller only)

1. Audit compiled disassembly for Test28 and Test29 (if accessible) to count actual RX_DM reads between observed falling edge and TX_DP_OE write. The compiler may inline or reorder reads; source-level count is a clue, not final proof.
2. A prospective Test31 may replace Test28's wait with a *single-read, edge-confirming loop* that never re-reads CLOCK between loop exit and DATA write, preserving the timeout/failure contract. This is a narrowly testable change, **not yet shown to fix mixing**, and must be compared against Test28 compiled output before building.
3. Preserve slot0 HK, mapping, LED menu, all other controller behavior. Never modify XGO firmware/emulator/game mapping/turbo.

**HW:** Test28 protected; Test29 (slow repeat, mixing persists) and Test30 (fast repeat, HK taps fail, mixing persists) rejected.
