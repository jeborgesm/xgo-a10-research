# XGO processAux() feasibility — source review

Baseline: GP2040-CE pinned SHA `3d1f32f7d02d418826b725b60208278d3be878c3`. Sources `src/main.cpp`, `src/gp2040aux.cpp`, `src/addons/display.cpp`, and XGO Test01 driver header and implementation.

## Confirmed

- Core1 is launched once from `main.cpp` and runs `GP2040Aux::run()`.
- Every iteration runs `addons.PreprocessAddons()`, `addons.ProcessAddons()`, then `inputDriver->processAux()`.
- DisplayAddon is among core1 add-ons. Its `process()` updates and draws a screen; execution time is not bounded by a source-level deadline.
- XGO Test01 implements `processAux()` as a no-op and runs blocking `emit_frame()` in core0 `process()`.
- A GP2040-CE driver has access to `processAux()`, so XGO-specific auxiliary logic can be added without creating a second core1 loop.

## Timing conclusion

Merely moving `emit_frame()` into `processAux()` does not solve the timing problem: a 20 ms load wait would block subsequent display/add-on updates, while a short cooperative poll would have blind windows whenever the core1 loop processes display or other work. The Caveman protocol samples slot0 immediately after DATA release, with 12 us edge timeouts. Source does not establish sufficient scheduling margin for cooperative polling.

## Engineering decision

Do not produce a Test02 UF2 based solely on a processAux relocation. Required before implementation: measured load-pulse width, inter-frame interval and slot0 deadline from XGO hardware; worst-case core1 add-on execution under OLED activity; and a verified event-capture/interrupt mechanism or a proven scheduling model. Preserve Test01 unchanged.

## Safe next work

Create an **instrumentation-only Caveman derivative** (separate from the hardware-proven binary) that collects timing statistics with no printf, heap allocations, or OLED calls in the 12-slot critical section. Expose statistics only outside frame handling (e.g. after a bounded sample run) and confirm instrumentation overhead does not alter timing. Do not claim timing results without hardware measurements.
