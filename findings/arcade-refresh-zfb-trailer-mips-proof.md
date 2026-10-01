# Arcade ZFB trailer routine — freestanding MIPS proof

Date: 2026-09-25
Status: SOURCE + TOOLCHAIN PROOF COMPLETE

The first actual Arcade-only executable routine is now implemented:
tools/arcade_refresh/arcade_zfb_trailer.c

Target ABI:
- link/runtime address 0x87002000
- a0 = already-open destination ZFB handle
- a1 = NUL-terminated driver stem
- stock fwrite callback 0x802B42AC
- return 0 success / -1 failure

Output is exactly:
4 zero bytes + driver stem + ".zip" + 2 zero bytes.

Local cross-build proof used clang 17 target mipsel-none-elf, MIPS32/o32,
-mno-abicalls, -fno-pic, freestanding. The first build exposed GP-relative
references caused by static constants. That version was rejected.

The routine was rewritten so constants are stack/immediate based. The rebuilt
disassembly contains NO $gp references. The '.zip' bytes are materialized from
immediate 0x70697A2E and stored little-endian, producing bytes 2E 7A 69 70.

This directly matches the four-family stock ZFB byte proof:
preview[0xEA00] + 00000000 + ASCII driver.zip + 0000.

Next binary splice must pass the open ZFB handle and golden stem workspace to
0x87002000 at the proven +0x09B4 boundary, check v0, and preserve the Test75
cleanup/error paths.
