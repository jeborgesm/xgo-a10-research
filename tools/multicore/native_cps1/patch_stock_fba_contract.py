#!/usr/bin/env python3
"""Patch pinned madcock/fbalpha2012_cps1 into a stock-contract C68K build.

Inputs:
  argv[1] = pinned CPS1 source tree
  argv[2] = libretro/fbalpha2012_cps2 sibling tree containing working C68K layer

This deliberately does NOT import CPS2 drivers or libretro code. It copies only:
  - src/cpu/c68k/
  - src/cpu/m68000_intf.c
  - src/cpu/m68000_intf.h

Then it applies the family-proven XGO/SF2000/GB300 arcade runtime contract:
  - build-time C68K backend
  - 22050 Hz / 367 sample audio
  - external stock-scheduler frameskip flag
"""
from pathlib import Path
import shutil
import sys

if len(sys.argv) != 3:
    raise SystemExit("usage: patch_stock_fba_contract.py CPS1_TREE CPS2_TREE")

cps1 = Path(sys.argv[1]).resolve()
cps2 = Path(sys.argv[2]).resolve()

def require(path: Path):
    if not path.exists():
        raise SystemExit(f"missing required path: {path}")

require(cps1 / "makefile.libretro")
require(cps1 / "src/burner/libretro/libretro.cpp")
require(cps1 / "src/cpu/m68000_intf.cpp")
require(cps2 / "src/cpu/c68k")
require(cps2 / "src/cpu/m68000_intf.c")
require(cps2 / "src/cpu/m68000_intf.h")

# Import only the known working C68K CPU implementation + interface layer.
dst_c68k = cps1 / "src/cpu/c68k"
if dst_c68k.exists():
    shutil.rmtree(dst_c68k)
shutil.copytree(cps2 / "src/cpu/c68k", dst_c68k)

old_cpp = cps1 / "src/cpu/m68000_intf.cpp"
old_cpp.unlink()
shutil.copy2(cps2 / "src/cpu/m68000_intf.c", cps1 / "src/cpu/m68000_intf.c")
shutil.copy2(cps2 / "src/cpu/m68000_intf.h", cps1 / "src/cpu/m68000_intf.h")

# The CPS1 makefile already has a C68K switch, but its original source tree
# never shipped the implementation/interface needed to make it real.
mk = (cps1 / "makefile.libretro").read_text()
old = "EMU_C68K = 0"
if old not in mk:
    raise SystemExit("expected EMU_C68K default not found")
mk = mk.replace(old, "EMU_C68K = 1", 1)
(cps1 / "makefile.libretro").write_text(mk)

lrp = cps1 / "src/burner/libretro/libretro.cpp"
lr = lrp.read_text()

old_audio = """#define AUDIO_SAMPLERATE 11025
#define AUDIO_SEGMENT_LENGTH 184 // <-- Hardcoded value that corresponds well to 32kHz audio."""
new_audio = """#define AUDIO_SAMPLERATE 22050
#define AUDIO_SEGMENT_LENGTH 367 // HC15xx stock-FBA family contract"""
if old_audio not in lr:
    raise SystemExit("expected SF2000 audio constants not found")
lr = lr.replace(old_audio, new_audio, 1)

# Add a simple private hook for XGO stock run_emulator(). The frontend owns
# lateness detection; the core only consumes the render/no-render decision.
anchor = """static bool input_rotated           = false;
"""
inject = """static bool input_rotated           = false;

#if defined(SF2000)
static int xgo_stock_frameskip_flag = 0;
extern "C" void xgo_fba_stock_frameskip(int flag)
{
   xgo_stock_frameskip_flag = flag ? 1 : 0;
}
#endif
"""
if anchor not in lr:
    raise SystemExit("libretro globals anchor not found")
lr = lr.replace(anchor, inject, 1)

# Reset the private state during core initialization.
anchor = """   update_audio_latency       = false;

   low_pass_enabled"""
inject = """   update_audio_latency       = false;
#if defined(SF2000)
   xgo_stock_frameskip_flag  = 0;
#endif

   low_pass_enabled"""
if anchor not in lr:
    raise SystemExit("retro_init frameskip reset anchor not found")
lr = lr.replace(anchor, inject, 1)

# FBA2012's native frameskip derives nSkipFrame from libretro audio-buffer
# monitoring. XGO stock firmware has its own scheduler feedback path, so force
# the final draw decision from that private callback immediately before frame
# execution. This preserves normal emulation/audio while Cps1Frame() skips
# CpsDraw() when late.
anchor = """   nCurrentFrame++;
   BurnDrvFrame();
"""
inject = """#if defined(SF2000)
   nSkipFrame = xgo_stock_frameskip_flag;
#endif

   nCurrentFrame++;
   BurnDrvFrame();
"""
if anchor not in lr:
    raise SystemExit("retro_run BurnDrvFrame anchor not found")
lr = lr.replace(anchor, inject, 1)

lrp.write_text(lr)

print("stock-contract patch applied")
print("backend=C68K")
print("audio_rate=22050")
print("audio_segment=367")
print("frameskip_bridge=xgo_fba_stock_frameskip")
