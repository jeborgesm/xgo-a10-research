#!/usr/bin/env python3
from pathlib import Path

p=Path("/tmp/cps1/src/burn/drv/capcom/d_cps1.cpp")
s=p.read_text()

repls=[
(
'\tCps1LoadRoms(1);\n\t\n\tif (AmendProgRomCallback) AmendProgRomCallback();',
'\txgo_a68k_trace("D12 before Cps1LoadRoms load pass");\n\tCps1LoadRoms(1);\n\txgo_a68k_trace("D13 after Cps1LoadRoms load pass");\n\t\n\txgo_a68k_trace("D14 before AmendProgRomCallback");\n\tif (AmendProgRomCallback) AmendProgRomCallback();\n\txgo_a68k_trace("D15 after AmendProgRomCallback");'
),
(
'\tSetGameConfig();\n\t\n\tif (Cps1Qs) {',
'\txgo_a68k_trace("D16 before second SetGameConfig");\n\tSetGameConfig();\n\txgo_a68k_trace("D17 after second SetGameConfig");\n\t\n\tif (Cps1Qs) {'
),
(
'\tif (bLoad) {\n\t\tINT32 Offset = 0;',
'\tif (bLoad) {\n\t\txgo_a68k_trace("P00 Cps1LoadRoms load enter");\n\t\tINT32 Offset = 0;'
),
(
'\t\ti = 0;\n\t\twhile (i < nCps68KByteswapRomNum + nCps68KNoByteswapRomNum) {',
'\t\txgo_a68k_trace("P10 program ROM phase");\n\t\ti = 0;\n\t\twhile (i < nCps68KByteswapRomNum + nCps68KNoByteswapRomNum) {'
),
(
'\t\t\tif ((ri.nType & 0xff) == CPS1_68K_PROGRAM_BYTESWAP) {\n\t\t\t\tnRet = BurnLoadRom(CpsRom + Offset + 1, i + 0, 2); if (nRet) return 1;\n\t\t\t\tnRet = BurnLoadRom(CpsRom + Offset + 0, i + 1, 2); if (nRet) return 1;',
'\t\t\tif ((ri.nType & 0xff) == CPS1_68K_PROGRAM_BYTESWAP) {\n\t\t\t\txgo_a68k_trace("P11 before program pair");\n\t\t\t\tnRet = BurnLoadRom(CpsRom + Offset + 1, i + 0, 2); if (nRet) return 1;\n\t\t\t\txgo_a68k_trace("P12 after program rom even");\n\t\t\t\tnRet = BurnLoadRom(CpsRom + Offset + 0, i + 1, 2); if (nRet) return 1;\n\t\t\t\txgo_a68k_trace("P13 after program rom odd");'
),
(
'\t\t\tif ((ri.nType & 0xff) == CPS1_68K_PROGRAM_NO_BYTESWAP) {\n\t\t\t\tnRet = BurnLoadRom(CpsRom + Offset, i, 1); if (nRet) return 1;',
'\t\t\tif ((ri.nType & 0xff) == CPS1_68K_PROGRAM_NO_BYTESWAP) {\n\t\t\t\txgo_a68k_trace("P14 before program linear");\n\t\t\t\tnRet = BurnLoadRom(CpsRom + Offset, i, 1); if (nRet) return 1;\n\t\t\t\txgo_a68k_trace("P15 after program linear");'
),
(
'\t\t// Graphics\n\t\tif (nCpsGfxLen) {',
'\t\txgo_a68k_trace("P19 program phase done");\n\t\t// Graphics\n\t\txgo_a68k_trace("G00 graphics phase");\n\t\tif (nCpsGfxLen) {'
),
(
'\t\t\t\t\t\tCpsLoadTilesByte(CpsGfx + Offset, i);',
'\t\t\t\t\t\txgo_a68k_trace("G10 before CpsLoadTilesByte");\n\t\t\t\t\t\tCpsLoadTilesByte(CpsGfx + Offset, i);\n\t\t\t\t\t\txgo_a68k_trace("G11 after CpsLoadTilesByte");'
),
(
'\t\t\t\t\t\t\t\tCpsLoadTiles(CpsGfx + Offset, i);',
'\t\t\t\t\t\t\t\txgo_a68k_trace("G20 before CpsLoadTiles");\n\t\t\t\t\t\t\t\tCpsLoadTiles(CpsGfx + Offset, i);\n\t\t\t\t\t\t\t\txgo_a68k_trace("G21 after CpsLoadTiles");'
),
(
'\t\t// Z80 Program\n\t\tif (nCpsZRomLen) {',
'\t\txgo_a68k_trace("G99 graphics phase done");\n\t\t// Z80 Program\n\t\txgo_a68k_trace("Z00 Z80 phase");\n\t\tif (nCpsZRomLen) {'
),
(
'\t\t// OKIM6295 Samples\n\t\tif (nCpsAdLen) {',
'\t\txgo_a68k_trace("Z99 Z80 phase done");\n\t\t// OKIM6295 Samples\n\t\txgo_a68k_trace("S00 OKI phase");\n\t\tif (nCpsAdLen) {'
),
(
'\t\t// QSound Samples\n\t\tif (nCpsQSamLen) {',
'\t\txgo_a68k_trace("S19 OKI phase done");\n\t\t// QSound Samples\n\t\txgo_a68k_trace("S20 QSound phase");\n\t\tif (nCpsQSamLen) {'
),
(
'\t\t// Extra Tile Roms\n\t\tif (nCpsExtraGfxLen) {',
'\t\txgo_a68k_trace("S39 QSound phase done");\n\t\t// Extra Tile Roms\n\t\txgo_a68k_trace("E00 extra tiles phase");\n\t\tif (nCpsExtraGfxLen) {'
),
(
'\t}\n\n\treturn nRet;\n}',
'\t\txgo_a68k_trace("P99 Cps1LoadRoms load exit");\n\t}\n\n\treturn nRet;\n}'
)
]

for old,new in repls:
    if old not in s:
        raise SystemExit("anchor not found: "+old[:100])
    s=s.replace(old,new,1)

p.write_text(s)
print("Test17 deep CPS1 ROM-load tracing applied")
