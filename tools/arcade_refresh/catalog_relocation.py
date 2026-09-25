#!/usr/bin/env python3
"""Static relocation planner for Arcade catalog helpers.

All addresses are helper-relative offsets.  The emitted helper is loaded at
0x87000000 by the golden generic runner.
"""
from __future__ import annotations

LOAD_BASE=0x87000000
GBA_LITERALS={
 "slot0":0x09E4,
 "slot1":0x0A02,
 "slot2":0x0A20,
 "root": 0x0A3E,
}
# Runtime address construction for any relocated string must be audited as
# MIPS hi16/lo16.  This helper centralizes the carry rule.
def hi16(addr:int)->int:
    return ((addr+0x8000)>>16)&0xffff
def lo16(addr:int)->int:
    return addr&0xffff

def runtime(off:int)->int: return LOAD_BASE+off

def encode_lui(rt:int,imm:int)->int:
    return (0x0f<<26)|(rt<<16)|(imm&0xffff)

def encode_addiu(rt:int,rs:int,imm:int)->int:
    return (0x09<<26)|(rs<<21)|(rt<<16)|(imm&0xffff)

def address_pair(rt:int,off:int):
    a=runtime(off)
    return encode_lui(rt,hi16(a)),encode_addiu(rt,rt,lo16(a))

if __name__=="__main__":
    for k,o in GBA_LITERALS.items():
        a=runtime(o)
        print(k,hex(o),hex(a),hex(hi16(a)),hex(lo16(a)))
