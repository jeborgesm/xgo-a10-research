# Test25 HK sequencer integration gate

The host-side `HKSequencer.h` and `test_hk_sequencer.cpp` are committed under `diagnostics/`. Their existing assertions were compiled and executed locally using `g++ -std=c++17 -Wall -Wextra -pedantic` on 2026-10-14: **PASS**.

**Not a flashable candidate yet.** The next step is a separate Test25 driver based on Test16 with the scheduler called only from Core0 `process(Gamepad*)`, and the existing Core1 `emit_frame()` unchanged. Core0 should publish synthetic bit0 during a run, and neutral otherwise; no button processing or sleeps in the responder. A complete integration must address safe trigger, OLED phase visibility, abort, and ensure all other buttons remain neutral while the test runs. It must also validate the 10ms pulse relative to host scan cadence and compile with pinned upstream GP2040-CE. Do not flash or claim validation before this gate.

The design proposal is `findings/gp2040ce-hk-one-press-diagnostic-sequencer-design-2026-10-14.md`. Protected Test16 remains untouched.
