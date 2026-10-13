# Test17 surgical integration gate — 2026-10-12

## Verified source and executable evidence

- Existing GP2040-CE overlay `integrations/gp2040ce-xgo-test01/apply.py` explicitly retains the Pico board configuration, Web Config XGO input-mode option, OLED layout, and GP2040 auxiliary tick. It moves the responder to Core1 and auxiliary execution to Core0.
- Test16 `XGODriver.cpp` takes a single atomic `published_mask` snapshot after detecting LOAD-low, then waits for LOAD release and clocks twelve bits. The mask is computed from processed `Gamepad` state. Thus Core0's Gamepad processing is on the *data dependency* path, not on the Core1 responder's instruction path.
- Offline Test17 source changes the mask origin to a single active-low `sio_hw->gpio_in` read using the supplied Pico diagram. It retains the rest of the serial frame code and GP2040 overlay. This does not guarantee timing, wiring, or config compatibility.
- Diagram-derived GPIO slot mapping: `R=12, Y=11, X=10, L=13, A=6, B=7, Select=16, Start=17, Up=2, Down=3, Left=5, Right=4`. These are physical GP pins, **not** a verified mapping of arcade labels HK/HP/MP/MK.
- Local executable Python enumeration independently verified that an ideal active-low GPIO snapshot decodes all 4096 combinations into the intended 12-slot masks. This is a model, not a flashed hardware result.
- Uploaded `xgo_live_controller.elf` is a 32-bit ARM ELF with disassemblable `main`; the reference at `0x100004f2` polls PHY CLOCK and branches into bit selection at `0x100004f8`, then peripheral write at `0x10000504` for one branch. Other branch and clock-to-write paths still require complete analysis. This executable is a reference, not verified identical to archived native-PHY Contra UF2.

## Important implementation risk

The Test17 snapshot is taken after LOAD-low detection, **before** waiting for LOAD release. That is a coherent host-transaction snapshot, but does not literally sample each button at the host's eventual CLOCK read. This is an unavoidable sampling boundary; its latency must be measured against the physical-input contract. Replacing processed state with GPIO is a *targeted experiment*, not a demonstrated cure for wrong-slot contamination. Slot alignment/timing faults may remain.

## Preserve/stop gates

- Golden Test14 remains untouched. Test17 is OFFLINE ONLY; no firmware artifact built or hardware test requested.
- Do not rewrite Web Config or settings storage. Audit which XGO settings are purely display/mode vs actually modify button behavior before bypassing Gamepad semantics.
- Do not assume the original direct-GPIO DIY firmware uses the same Pico pinout; verify the uploaded ELF GPIO masks against the user diagram.
- Obtain disassembly of Test16 compiled responder (ELF with symbols preferable) and reference; establish actual clock-fall-to-DATA-write path before release.
- Audit the GPIO ownership: GP2040 must leave pins in input mode with pull-ups, and must not reassign them to conflicting peripherals.
