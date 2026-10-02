#!/usr/bin/env python3
"""Build Test-A-derived conditional internal-speaker mono fold.

HW/BIN basis:
- XGO internal gameplay speaker consumes channel 0/left.
- GP-30360 is the cached GPIO L15 LCD/TV state.
- L15=1 follows the stock LCD branch; L15=0 follows TV/AV branch.
- maintained family policy folds L+R into channel 0 and preserves channel 1.

Policy:
  LCD/internal: L'=(L>>1)+(R>>1), R'=R
  TV/AV:       L'=L, R'=R

No rate/scheduler/ring/queue/OSD changes.
"""
from __future__ import annotations
import argparse,hashlib,struct
from pathlib import Path
BASE=0x80000000
EXPECTED_SHA="060093e8fd2a3fa559c9b43e207c4bb495de82e87519b672a799d19b304b20b7"
EXPECTED_SIZE=12_768_452
CALL_VA=0x8035E800
OLD_CALL=0x0C0D72E8
CAVE_VA=0x807DBB08
CAVE_LEN=56
RUN_SOUND=0x8035CBA0
CRC_OFF=0x18C

def j(a): return 0x08000000|((a>>2)&0x03ffffff)
def jal(a): return 0x0c000000|((a>>2)&0x03ffffff)
def crc32_mpeg2(data):
    crc=0xffffffff
    for byte in data:
        crc ^= byte<<24
        for _ in range(8):
            crc=((crc<<1)^0x04c11db7)&0xffffffff if crc&0x80000000 else (crc<<1)&0xffffffff
    return crc

def main():
    p=argparse.ArgumentParser(); p.add_argument("input",type=Path); p.add_argument("output",type=Path); a=p.parse_args()
    old=a.input.read_bytes()
    if len(old)!=EXPECTED_SIZE or hashlib.sha256(old).hexdigest()!=EXPECTED_SHA: raise SystemExit("REFUSE: input is not exact HW-PASS Test A")
    b=bytearray(old); co=CALL_VA-BASE; cave=CAVE_VA-BASE
    if struct.unpack_from("<I",b,co)[0]!=OLD_CALL: raise SystemExit("REFUSE: callback call site changed")
    if b[cave:cave+CAVE_LEN]!=b"\0"*CAVE_LEN: raise SystemExit("REFUSE: 56-byte cave not zero")
    # t0 = cached L15 state. 0 = TV/AV -> bypass fold.
    words=[
      0x8F888968, # lw    t0,-30360(gp)
      0x1100000A, # beq   t0,zero,tail
      0x00804021, # addu  t0,a0,zero
      0x85090000, # lh    t1,0(t0)
      0x850A0002, # lh    t2,2(t0)
      0x00094843, # sra   t1,t1,1
      0x000A5043, # sra   t2,t2,1
      0x012A4821, # addu  t1,t1,t2
      0xA5090000, # sh    t1,0(t0)
      0x24A5FFFF, # addiu a1,a1,-1
      0x14A0FFF8, # bne   a1,zero,loop
      0x25080004, # addiu t0,t0,4
      j(RUN_SOUND),
      0x02402821, # addu  a1,s2,zero (restore callback frame count)
    ]
    assert len(words)*4==CAVE_LEN
    struct.pack_into("<I",b,co,jal(CAVE_VA)); struct.pack_into("<14I",b,cave,*words)
    crc=crc32_mpeg2(b[0x200:]); struct.pack_into("<I",b,CRC_OFF,crc)
    allowed=set(range(CRC_OFF,CRC_OFF+4))|set(range(co,co+4))|set(range(cave,cave+CAVE_LEN))
    changed=[i for i,(x,y) in enumerate(zip(old,b)) if x!=y]
    unexpected=[i for i in changed if i not in allowed]
    if unexpected: raise SystemExit(f"REFUSE: unexpected changes {unexpected[:16]}")
    if crc32_mpeg2(b[0x200:])!=crc: raise SystemExit("REFUSE: CRC verify failed")
    a.output.write_bytes(b)
    print("sha256="+hashlib.sha256(b).hexdigest()); print(f"crc32_mpeg2=0x{crc:08X}"); print("changed_bytes="+str(len(changed)))

if __name__=="__main__": main()
