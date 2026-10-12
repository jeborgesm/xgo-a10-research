# Test15 hardware validation — negative result (2026-10-12)

## HW — user-reported results (authoritative)

| Test | Result |
|---|---|
| HK short taps register consistently | FAIL |
| HK/HP holds avoid unexpected repeated attacks | FAIL |
| HK does not introduce unintended LP | FAIL |
| HP does not introduce unintended LK | FAIL |
| Rapid taps followed by holds avoid mixed attacks | FAIL |
| OLED continues showing correct inputs | PASS |
| Web Config remains accessible | PASS |

User's summary: **"no actual improvement over test 14"**.

## Candidate and provenance

Test15 candidate source: `integrations/gp2040ce-xgo-test01/candidates/test15-offline/XGODriver.cpp`. GitHub Actions run `38274789992` compiled successfully; artifact `11757969447`. Candidate moved Core1 mask snapshot to after LOAD-low detection and deferred diagnostic atomics until after IRQ restoration. Golden Test14 untouched.

## Conclusion and constraints

**HW:** Test15 did not resolve any of the five reported Street Fighter faults. The offline freshness model demonstrated a real *possible* stale-state behavior, but it did **not** establish the cause of these hardware symptoms. No claim that Test15 is a fix survives this hardware test.

**HW:** Correct OLED state and accessible Web Config indicate the input display and configuration access remained functional; they do not prove the XGO serialized frame was correct.

**INF/OPEN:** Investigation should pivot to the boundary between processed mask, PHY waveform, and XGO host/game decoding, including sustained-press repetition and history-dependent cross-button contamination. Do not assume a clock-shift explanation without measured evidence. Need distinguish host/game key-repeat behavior from serialized release/repress; physical button-to-game action mapping remains unestablished.

**Decision:** Test15 is **REJECTED for the gameplay objective**. Preserve Test14 as rollback; no Test16 firmware or further user testing until an independently justified mechanism and discriminating validation plan exist.
