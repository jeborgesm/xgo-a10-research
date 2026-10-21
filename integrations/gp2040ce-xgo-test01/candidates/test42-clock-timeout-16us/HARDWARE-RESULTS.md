# Test42 hardware results — 2026-10-20

## Candidate
Test36-derived GP2040-CE XGO controller responder with only EDGE_TIMEOUT_US changed from 12 to 16 microseconds. Attack pulse remains 18 ms. No XGO device, emulator, or mapping changes.

## User-observed hardware result
- Movement looks very good; while holding crouch + direction, Ken no longer faces the opposite direction.
- Residual movement artifact: Ken appears to try to rise briefly, then immediately resumes the correct crouch.
- All attacks responsive, no mixed attacks observed, and no repeats during holds.
- OLED readings reported in sequence: OK ~13700 and rising rapidly; ERR 355, CLK 307, REL 46, LAST SLOT changing (5,11,5,9); later CLK 340, REL 51; one 'FAIL 32' reading. These are cumulative, not simultaneous snapshots; do not calculate a precise interval failure rate from them.
- CLOCK/release failures persist; no claim of perfect serial synchronization.

## Status
**Best hardware-observed gameplay candidate, not fully resolved.** Preserve Test36 as rollback; Test42 as best tested candidate. Do not change the XGO-side firmware. Investigate intermittent crouch-release artifact and remaining CLOCK timeouts before claiming final resolution. Avoid the strict phase guard from rejected Test35.

## Build provenance
GitHub Actions run 39526930281 succeeded; artifact 12313413278. Hardware testing was performed by user after this build.
