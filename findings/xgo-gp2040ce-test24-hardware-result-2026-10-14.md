# GP2040-CE XGO Test24 hardware result — 2026-10-14

## HW — direct user report
- HK quick tap is not immediately recognized; repeated tapping eventually produces HK.
- Holding HK first produces MP, then repeatedly produces HK.
- Other buttons are fine for ordinary gameplay and special moves except when held.
- Special moves requiring HK remain difficult/impractical.

## SRC — candidate under test
`integrations/gp2040ce-xgo-test01/candidates/test24-test16-slot0-fast-release/XGODriver.cpp`: Test16 derivative replacing `wait_data(true)` call/return with inline polling that asserts slot0 immediately upon detecting DATA-high; leaves slot1–11 loop and mask mapping intact.

## Conclusion
**HW FAILED** HK acceptance. Neither Test23 (post-detection write reorder) nor Test24 (inline LOAD-release polling) corrected HK. Further speculative reductions of the same path are not justified without measuring waveform timing.

## Open alternatives
1. Slot0 is electrically sampled incorrectly or frame alignment is unstable.
2. Host receives correct slot0 but game/frontend mapping or another input source produces MP.
3. GP2040-CE input publication is delayed or button transitions missed at polling rate, independently of serial response.
4. Held-button repetition and substitution require independent diagnosis; do not attribute to game repeat without evidence.

## Next evidence gates
- Establish whether GP2040-CE `published_mask` registers brief HK taps, preferably from existing diagnostics or non-invasive instrumentation.
- Establish physical slot0-to-arcade HK mapping with known native XGO input path or original controller, if available.
- Inspect host input aggregation and CPS1 action mapping.
- Compare responder timing with actual host capture or disassembly before another candidate.

Protected Test16 unchanged; Test24 rejected.
