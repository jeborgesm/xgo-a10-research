#!/usr/bin/env python3
from pathlib import Path

p = Path("/tmp/cps1/src/burner/libretro/libretro.cpp")
s = p.read_text()
old = """   poll_input();

   nBurnLayer = 0xff;
"""
new = """   /* XGO diagnostic: isolate first-frame stall from libretro input polling.
    * Hardware Test 09 only. Do not promote to production behavior. */
   /* poll_input(); */

   nBurnLayer = 0xff;
"""
if old not in s:
    raise SystemExit("retro_run poll_input block not found")
p.write_text(s.replace(old, new, 1))
print("patched FBA2012 CPS1: poll_input disabled for Test 09")
