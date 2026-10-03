#!/usr/bin/env python3
"""Build XGO Test A-derived left/right channel-isolation diagnostics.

These are diagnostic artifacts, not mono-policy candidates.  They preserve the
HW-PASS native-22050 Test A transport and zero exactly one S16 channel before
run_sound_advance(), leaving stereo frame geometry unchanged.

Usage:
  build_mono_channel_probe.py testA.asd output.asd --keep left
  build_mono_channel_probe.py testA.asd output.asd --keep right
"""
from __future__ import annotations
import argparse,hashlib,struct
from pathlib import Path

BASE=0x80000000
EXPECTED_SHA="060093e8fd2a3fa559c9b43e207c4bb495de82e87519b672a799d19b304b20b7"
EXPECTED_SIZE=12_768_452
CALL_VA=0x8035E800
OLD_CALL=0x0C0D72E8 # jal 0x8035CBA0
CAVE_VA=0x807DBB08
CAVE_LEN=40
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
    p=argparse.ArgumentParser()
    p.add_argument("input",type=Path)
    p.add_argument("output",type=Path)
    p.add_argument("--keep",choices=("left","right"),required=True)
    a=p.parse_args()
    old=a.input.read_bytes()
    if len(old)!=EXPECTED_SIZE: raise SystemExit("REFUSE: wrong Test A size")
    if hashlib.sha256(old).hexdigest()!=EXPECTED_SHA: raise SystemExit("REFUSE: input is not exact HW-PASS Test A")
    b=bytearray(old)
    co=CALL_VA-BASE; cave=CAVE_VA-BASE
    if struct.unpack_from("<I",b,co)[0]!=OLD_CALL: raise SystemExit("REFUSE: callback call site changed")
    if b[cave:cave+CAVE_LEN]!=b"\0"*CAVE_LEN: raise SystemExit("REFUSE: diagnostic cave not zero")
    if struct.unpack_from("<I",b,cave-4)[0]!=0: raise SystemExit("REFUSE: preceding jump delay slot changed")

    # Keep left => zero R halfword at +2. Keep right => zero L at +0.
    zero_off=2 if a.keep=="left" else 0
    sh_zero=(0x29<<26)|(8<<21)|zero_off
    words=[
      0x00804021,             # addu t0,a0,zero
      0x00A04821,             # addu t1,a1,zero
      0x11200005,             # beq  t1,zero,done
      0x00000000,             # nop
      sh_zero,                # sh zero,channel_offset(t0)
      0x2529FFFF,             # addiu t1,t1,-1
      0x1520FFFD,             # bne t1,zero,loop
      0x25080004,             # addiu t0,t0,4
      j(RUN_SOUND),           # tail-jump original writer
      0x00000000,
    ]
    struct.pack_into("<I",b,co,jal(CAVE_VA))
    struct.pack_into("<10I",b,cave,*words)
    crc=crc32_mpeg2(b[0x200:])
    struct.pack_into("<I",b,CRC_OFF,crc)

    allowed=set(range(CRC_OFF,CRC_OFF+4))|set(range(co,co+4))|set(range(cave,cave+CAVE_LEN))
    changed=[i for i,(x,y) in enumerate(zip(old,b)) if x!=y]
    unexpected=[i for i in changed if i not in allowed]
    if unexpected: raise SystemExit(f"REFUSE: unexpected changed offsets {unexpected[:16]}")
    if crc32_mpeg2(b[0x200:])!=crc: raise SystemExit("REFUSE: CRC verification failed")
    a.output.write_bytes(b)
    print("keep="+a.keep)
    print("sha256="+hashlib.sha256(b).hexdigest())
    print(f"crc32_mpeg2=0x{crc:08X}")
    print("changed_bytes="+str(len(changed)))

if __name__=="__main__": main()
