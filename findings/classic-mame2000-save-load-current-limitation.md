# CLASSIC save/load-state audit — current MAME2000 limitation, not Refresh regression

Date: 2026-09-09
Branch: research-game-list-arcade-expansion

User reports CLASSIC pause-menu Save/Load does not function and notes this predates Test45.

Repository-authoritative audit of the exact Test12 core used by Test33/CLASSIC:

- Test33 relocates the exact hardware-working Test12 loader and preserves its external core path:
  /mnt/sda1/cores/fbalpha2012_cps1/core.xgc
- Despite that historical directory name, strings in the exact core.xgc identify it as the custom XGO MAME2000 build (mame2000-* options and mame2000_xgo_t12 namespace).
- The Test12 build workflow explicitly records:
  serialize_note=MAME2000 exposes size-0 libretro state stubs
- xgo_mame2000_frontend.c comments the same limitation and installs xgo_core_state_save/load only so failure is graceful instead of falling into stale embedded-FBA handlers.
- xgo_libretro_state.c requires retro_serialize_size() > 0. With MAME2000 returning 0, stock pause-menu Save cannot produce a state and Load cannot restore one.

Conclusion:
CLASSIC Save/Load failure is NOT introduced by Test44/Test45 Refresh work. It is a pre-existing limitation of the MAME2000 core currently used by the hardware-proven Test33 CLASSIC path.

Future fix is a separate emulator-runtime task:
- either implement working libretro retro_serialize_size/retro_serialize/retro_unserialize for this MAME2000 fork using its internal state system,
- or add an XGO-specific state adapter around MAME's internal state machinery while preserving the stock XGO .saN bundle callbacks.

Do not mix this with the current Refresh stabilization unless necessary.
