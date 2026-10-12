# Exact game target for GP2040-CE XGO input fault — 2026-10-12

## HW — user clarification

**Street Fighter II: The World Warrior, original CPS-1 arcade release (1991)**. Not Champion Edition, Hyper Fighting, Super Street Fighter II, or a modern Street Fighter. This is the version exhibiting Test14 and Test15 faults.

User reports LP/LK deliberate inputs generally work, while slower/higher-strength moves reveal missed HK short taps, held HP/HK repetitions, and wrong LP/LK appearing after heavy attacks. OLED is correct; Test15 did not improve gameplay.

## Investigation implications

- Use World Warrior CPS-1/MAME game input semantics, button wiring, and emulation behavior, not SFII Turbo, SF6, or generic modern fighting-game input-buffer rules.
- Confirm XGO game's specific CPS-1 ROM set and emulator core before asserting frame timings, negative-edge behavior, or per-move held-button retrigger.
- Six-button mapping must be traced through physical GP2040 button -> published XGO slot -> XGO console controller decoding -> CPS-1 input mapping -> game's attack logic.
- Game startup/active/recovery periods can defer when a phantom input becomes visible. **Inference**, not yet proof of electrical corruption.
- Distinguish intended single heavy attack on held button from game-specific retrigger logic; verify from original World Warrior behavior before declaring either normal.
- No further user testing required just to reconfirm game title; exact variant is established by user.
