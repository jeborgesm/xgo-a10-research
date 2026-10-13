# Test17 release-blocker audit — 2026-10-12

## Results (source and local execution)

- Reviewed `integrations/gp2040ce-xgo-test01/apply.py`: it copies **only** `src/drivers/xgo/XGODriver.cpp` from the overlay root. The Test17 candidate at `candidates/test17-direct-gpio-offline/XGODriver.cpp` is **not selected by the build overlay**. Building with the unchanged apply script would produce the old driver, not Test17. Do not label a resulting UF2 as Test17 until the build path explicitly selects the candidate and confirms its source hash.
- The existing overlay retains Pico board defaults and adds XGO Web Config input-mode selection. The Test17 direct GPIO snapshot bypasses processed Gamepad mappings. This means any configurable button remapping, SOCD or turbo processing that should affect XGO output would be bypassed. Audit intended semantics before integrating.
- Test17 direct GPIO source samples once after detecting LOAD low, while interrupts are disabled, then emits twelve slots. This is coherent per frame. It has not been measured against host sampling or compiled to disassembly.
- Executed local Python `test_gpio_contract.py` (committed to `integrations/gp2040ce-xgo-test01/tests/test17_direct_gpio_contract.py`): 3 tests passed, including all 4096 input combinations and unrelated-pin isolation. These tests validate the mapping *model only*.
- The local pre-existing `xgo-gp2040ce-test16-offline.zip` explicitly contains `README-DO-NOT-FLASH.txt`; do not mistake it for a validated golden image.
- No local Pico SDK found; no Test17 UF2 compiled, no actual GPIO electrical behavior measured.

## Blocking checks before build or hardware test

1. Explicitly select Test17 source in a separate, reproducible build overlay (do not overwrite golden Test14).
2. Verify board GPIO direction/pull-up and peripheral ownership for all 12 input pins; identify conflicts with user-configured pins and GP2040 add-ons.
3. Audit XGO Web Config controls for actual input behavior vs mode/display-only controls. Preserve or intentionally define which mappings/turbo/SOCD settings affect XGO.
4. Inspect compiled CLOCK-fall-to-DATA-write and LOAD-release-to-slot0 path against the working DIY ELF.
5. Ensure no regression to Web Config recovery, OLED, or USB PHY ownership; then produce a separately labeled **untested** candidate.

**Disposition:** Test17 remains offline research; no hardware test requested.
