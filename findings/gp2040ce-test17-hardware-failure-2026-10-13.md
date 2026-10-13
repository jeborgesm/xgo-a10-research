# Test17 hardware failure — 2026-10-13 (HW)

**FAIL / DO NOT RETEST TEST17.** User reports: LP rapid-fire with occasional MP; MP repeats approximately every second with occasional LP; LB generates HK every second and sometimes MP; LK and MK generate MK every second and occasionally coin; RB/RT do nothing; LT generates HK with occasional HP. Previous controller mapping behavior regressed.

**SRC difference:** Test14 `runResponder()` uses `published_mask` from `map_mask(Gamepad*)` (processed gamepad state); Test17 `runResponder()` calls `emit_frame()`, which calls `read_xgo_direct_mask()` after LOAD goes low. This reads raw SIO GPIO and hardcodes host-slot pins `{12,11,10,13,6,7,16,17,2,3,5,4}`. Thus the GP2040 processed button assignment is no longer used to select serial slots; `process()` still computes a processed snapshot but Test17 does not transmit it. Test17 additionally performs `gpio_init`, `gpio_set_dir(GPIO_IN)`, `gpio_pull_up` on the twelve pins in `initialize()`, which may conflict with input configuration ownership.

**Inference, not yet proven:** cross-button activity and periodic repeat may involve serial clock/LOAD synchronization or physical GPIO ownership, in addition to the mapping bypass. Do not claim an exact cause until offline timing and mapping audits are completed.

**Release gate:** Test17 is rejected despite CI success; CI validates compilation and structural source invariants, not host-observed behavior. Preserve golden Test14, the user's requested physical GPIO wiring, and the previous controller mapping behavior. Do not substitute the unwired DIY GPIO2..13 proof mapping. Next candidate must address both input-contract preservation and serial timing; no hardware test until reviewed.
