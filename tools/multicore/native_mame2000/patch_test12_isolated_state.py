#!/usr/bin/env python3
from pathlib import Path

p = Path("/tmp/mame2000/src/libretro/libretro.c")
s = p.read_text()

old = 'sprintf(core_save_directory,"%s%cmame2000",retro_save_directory,slash);'
new = 'sprintf(core_save_directory,"%s%cmame2000_xgo_t12",retro_save_directory,slash);'
if old not in s:
    raise SystemExit("core_save_directory pattern not found")
s = s.replace(old, new, 1)

old2 = 'sprintf(core_sys_directory,"%s%cmame2000",retro_system_directory,slash);'
new2 = 'sprintf(core_sys_directory,"%s%cmame2000_xgo_t12",retro_system_directory,slash);'
if old2 not in s:
    raise SystemExit("core_sys_directory pattern not found")
s = s.replace(old2, new2, 1)

p.write_text(s)
print("patched MAME2000: isolated Test12 state namespace mame2000_xgo_t12")
