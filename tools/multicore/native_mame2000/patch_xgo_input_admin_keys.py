#!/usr/bin/env python3
from pathlib import Path

p = Path("/tmp/mame2000/src/libretro/libretro.c")
s = p.read_text()

old = """#if defined(SF2000)
		key[KEY_TAB] |= (JS(i, L) > 0) && (JS(i, START) > 0);	// config menu: L + START
		key[KEY_TILDE] |= (JS(i, R) > 0) && (JS(i, START) > 0);	//    OSD menu: R + START
		key[KEY_P] |= (JS(i, R) > 0) && (JS(i, L) > 0);			//       pause: R + L
		key[KEY_F3] |= (JS(i, R) > 0) && (JS(i, SELECT) > 0);	//  reset game: R + SELECT
		key[KEY_ESC]  |= (JS(i, A) > 0);						// menu cancel: A
#else
		key[KEY_TAB] |= JS(i, R2);
#endif
"""

new = """#if defined(SF2000)
		/* XGO: the stock frontend owns pause/menu/reset behavior.
		 * Do not translate gameplay buttons into MAME keyboard/admin keys.
		 * Ordinary B/A/Y/X/L/R joypad mappings above remain untouched. */
#else
		key[KEY_TAB] |= JS(i, R2);
#endif
"""

if old not in s:
    raise SystemExit("expected SF2000 admin-hotkey block not found")

p.write_text(s.replace(old, new, 1))
print("patched MAME2000: disabled SF2000 admin hotkeys for XGO")
