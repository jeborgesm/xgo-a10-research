#!/usr/bin/env python3
"""Assemble *unplaced* Handle P1/P2 conditional routing code.

No firmware is written. The mode address must be proven writable and the code
address executable before either is supplied to a production patch builder.
"""
import struct

def ins(op, rs, rt, imm):
    return (op << 26) | (rs << 21) | (rt << 16) | (imm & 0xffff)

def j(addr):
    assert addr & 3 == 0
    return 0x08000000 | ((addr >> 2) & 0x03ffffff)

def assemble(*, mode_address, code_address, resume=0x8035d544):
    """Uses t9 as temporary; caller MUST independently prove t9 dead at hook."""
    assert mode_address % 4 == 0 and code_address % 4 == 0
    assert (mode_address >> 28) == 0x8 and (code_address >> 28) == 0x8
    assert (code_address >> 28) == (resume >> 28)
    # lui t9, upper(mode); lw t9, lower(t9) with sign-adjusted upper.
    upper = ((mode_address + 0x8000) >> 16) & 0xffff
    lower = mode_address & 0xffff
    # mode==0 -> stock path; nonzero -> fixed-P1 path.
    code = [
        ins(0x0f, 0, 25, upper),       # lui t9,hi
        ins(0x23, 25, 25, lower),      # lw t9,lo(t9)
        ins(0x04, 25, 0, 12),         # beq t9,zero,stock
        0,                             # delay slot
        ins(0x05, 7, 0, 5),           # bne a3,zero,p2
        0,
        0x8f89f2d8,                   # lw t1,-0xd28(gp) [HW-positive]
        0x0289a025,                   # or s4,s4,t1
        ins(0x04, 0, 0, 2),           # b to merge
        0,
        0x0000a021,                   # p2: move s4,zero
        0x00d43025,                   # merge: or a2,a2,s4
        0x30d20020,                   # andi s2,a2,0x20
        j(resume), 0,
        0x00d43025,                   # stock: or a2,a2,s4
        0x30d20020,                   # andi s2,a2,0x20
        j(resume), 0,
    ]
    # Branch at index 2 targets index 16: PC-relative 16-3=13,
    # not 11. Reject silently wrong branch encodings.
    code[2] = ins(0x04,25,0,13)
    assert (2 + 1 + (code[2] & 0xffff)) == 16
    assert (4 + 1 + (code[4] & 0xffff)) == 10
    assert (8 + 1 + (code[8] & 0xffff)) == 11
    return struct.pack('<'+'I'*len(code), *code)

if __name__ == '__main__':
    # Deliberately no address guesses or flashable output.
    print('Conditional MIPS helper source ready; mode RAM, t9 liveness, and code placement UNPROVEN')
