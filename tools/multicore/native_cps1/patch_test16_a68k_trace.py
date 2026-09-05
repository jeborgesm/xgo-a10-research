#!/usr/bin/env python3
from pathlib import Path

def inject(path, replacements):
    p=Path(path); s=p.read_text()
    for old,new in replacements:
        if old not in s:
            raise SystemExit(f"anchor not found in {path}: {old[:80]}")
        s=s.replace(old,new,1)
    p.write_text(s)

# libretro load boundary
inject("/tmp/cps1/src/burner/libretro/libretro.cpp",[
('bool retro_load_game(const struct retro_game_info *info)\n{',
 'extern "C" void xgo_a68k_trace(const char *);\n\nbool retro_load_game(const struct retro_game_info *info)\n{\n   xgo_a68k_trace("L00 retro_load_game enter");'),
('      if (!fba_init(i, basename))\n         return false;',
 '      xgo_a68k_trace("L10 before fba_init");\n      if (!fba_init(i, basename)) { xgo_a68k_trace("L11 fba_init failed"); return false; }\n      xgo_a68k_trace("L12 after fba_init");')
])

# CPS driver init
inject("/tmp/cps1/src/burn/drv/capcom/d_cps1.cpp",[
('static INT32 DrvInit()\n{',
 'extern "C" void xgo_a68k_trace(const char *);\n\nstatic INT32 DrvInit()\n{\n\txgo_a68k_trace("D00 DrvInit enter");'),
('\tnRet = CpsInit(); if (nRet != 0) return 1;',
 '\txgo_a68k_trace("D10 before CpsInit");\n\tnRet = CpsInit(); if (nRet != 0) return 1;\n\txgo_a68k_trace("D11 after CpsInit");'),
('\tnRet = CpsRunInit(); if (nRet != 0) return 1;',
 '\txgo_a68k_trace("D20 before CpsRunInit");\n\tnRet = CpsRunInit(); if (nRet != 0) return 1;\n\txgo_a68k_trace("D21 after CpsRunInit");')
])

# CPS runtime init/reset
inject("/tmp/cps1/src/burn/drv/capcom/cps_run.cpp",[
('INT32 CpsRunInit()\n{',
 'extern "C" void xgo_a68k_trace(const char *);\n\nINT32 CpsRunInit()\n{\n\txgo_a68k_trace("R00 CpsRunInit enter");'),
('\tSekInit(0, 0x68000);\t\t\t\t\t// Allocate 68000',
 '\txgo_a68k_trace("R10 before SekInit");\n\tSekInit(0, 0x68000);\n\txgo_a68k_trace("R11 after SekInit");'),
('\tif (CpsMemInit()) {',
 '\txgo_a68k_trace("R20 before CpsMemInit");\n\tif (CpsMemInit()) {'),
('\tCpsRwInit();\t\t\t\t\t\t\t// Registers setup',
 '\txgo_a68k_trace("R21 after CpsMemInit");\n\txgo_a68k_trace("R30 before CpsRwInit");\n\tCpsRwInit();\n\txgo_a68k_trace("R31 after CpsRwInit");'),
('\tDrvReset();',
 '\txgo_a68k_trace("R40 before DrvReset");\n\tDrvReset();\n\txgo_a68k_trace("R41 after DrvReset");')
])

# A68K CPU init/reset boundary
inject("/tmp/cps1/src/cpu/m68000_intf.cpp",[
('static INT32 SekInitCPUA68K(INT32 nCount, INT32 nCPUType)\n{',
 'extern "C" void xgo_a68k_trace(const char *);\n\nstatic INT32 SekInitCPUA68K(INT32 nCount, INT32 nCPUType)\n{\n\txgo_a68k_trace("A00 SekInitCPUA68K enter");'),
('\tM68000_RESET();',
 '\txgo_a68k_trace("A10 before M68000_RESET");\n\tM68000_RESET();\n\txgo_a68k_trace("A11 after M68000_RESET");'),
('void SekReset(void)\n{',
 'void SekReset(void)\n{\n\txgo_a68k_trace("A20 SekReset enter");'),
('\t\tM68000_regs.a[7] = FetchLong(0);\t// Get initial stackpointer (register A7)',
 '\t\txgo_a68k_trace("A21 before FetchLong vectors");\n\t\tM68000_regs.a[7] = FetchLong(0);'),
('\t\tA68KChangePC(M68000_regs.pc);',
 '\t\txgo_a68k_trace("A22 before A68KChangePC");\n\t\tA68KChangePC(M68000_regs.pc);\n\t\txgo_a68k_trace("A23 after A68KChangePC");')
])

print("Test16 trace instrumentation applied")
