# CPS-1 turbo hypothesis — evidence correction (2026-10-12)

**HW (user):** No turbo feature observed in the CPS-1 emulator. The World Warrior issue affects heavy moves more strongly; LP/LK deliberate inputs are fine. Test15 gave no improvement, OLED remained correct.

**BIN:** XGO firmware set_keymap at 0x8035e83c understands a turbo flag (bit16) in optional per-ROM 48-byte .kmp files. This is an available firmware mechanism, not proof it is active for CPS-1 or this game. Captured original XGO SD inventory had no .kmp files (see findings/xgo-per-game-kmp-format-and-sf2000-branch-point.md).

**OPEN:** Whether the CPS-1 frontend invokes this feature, whether the user's SD has any .kmp override, whether any turbo bit is enabled, and whether game-specific mapping could explain wrong attack identities. User has not seen CPS-1 turbo implemented. Do not assert it is implemented or enabled.

**Priority decision:** Demote turbo as primary hypothesis. First resolve serial slot-to-World-Warrior action mapping and game input acceptance/recovery; independently verify host decoded input if possible. Cross-attack LP/LK during sole HP/HK remains the strongest unexplained signal. Do not ask user to hunt for turbo UI or repeat the existing tests.
