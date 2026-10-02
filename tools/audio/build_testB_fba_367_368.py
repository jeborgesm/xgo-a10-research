#!/usr/bin/env python3
"""Build XGO gameplay-audio Test B from the exact HW-PASS Test A firmware.

Test B preserves Test A and changes one additional variable: stock FBA's fixed
367-sample producer length. It uses the already-existing per-retro_run frame
counter parity to select 367/368 before BurnDrvFrame, averaging exactly 367.5
source frames per 60-Hz emulated frame = 22050 frames/s.

No new persistent state is allocated. The shim tail-jumps to the original
BurnDrvFrame target so the caller's return address and FBA $gp remain intact.
"""
from __future__ import annotations
import argparse, hashlib, struct
from pathlib import Path

BASE=0x80000000
EXPECTED_INPUT_SHA256="060093e8fd2a3fa559c9b43e207c4bb495de82e87519b672a799d19b304b20b7"
EXPECTED_SIZE=12_768_452
LCFG_HEADER=0x200
LCFG_SIZE_OFF=0x184
LCFG_CRC_OFF=0x18C

CALL_VA=0x8036C320
OLD_CALL=0x0C0DBFFD                 # jal 0x8036FFF4
CAVE_VA=0x807DBB08
CAVE_LEN=24
ORIGINAL_BURNDRVFRAME=0x8036FFF4

def sha256(b:bytes)->str:return hashlib.sha256(b).hexdigest()

def crc32_mpeg2(data:bytes)->int:
    crc=0xFFFFFFFF; poly=0x04C11DB7
    for byte in data:
        crc ^= byte<<24
        for _ in range(8):
            crc=((crc<<1)^poly)&0xFFFFFFFF if crc&0x80000000 else (crc<<1)&0xFFFFFFFF
    return crc

def j(addr:int)->int:return 0x08000000|((addr>>2)&0x03FFFFFF)
def jal(addr:int)->int:return 0x0C000000|((addr>>2)&0x03FFFFFF)

# Runtime contract at CALL_VA:
#   gp = stock FBA gp
#   GP-24072 = existing per-retro_run counter, incremented/stored at 0x8036C314
#   GP-24104 = nBurnSoundLen-like global
#
# Shim:
#   lw    t0,-24072(gp)
#   andi  t0,t0,1
#   addiu t0,t0,367
#   sw    t0,-24104(gp)
#   j     0x8036FFF4
#   nop
SHIM=struct.pack("<6I",
    0x8F88A1F8,
    0x31080001,
    0x2508016F,
    0xAF88A1D8,
    j(ORIGINAL_BURNDRVFRAME),
    0x00000000,
)

def main()->None:
    ap=argparse.ArgumentParser()
    ap.add_argument("input",type=Path,help="exact HW-PASS Test A bios/bisrv.asd")
    ap.add_argument("output",type=Path,help="new Test B bisrv.asd")
    args=ap.parse_args()
    original=args.input.read_bytes()
    if len(original)!=EXPECTED_SIZE: raise SystemExit(f"REFUSE: size {len(original)} != {EXPECTED_SIZE}")
    got=sha256(original)
    if got!=EXPECTED_INPUT_SHA256: raise SystemExit(f"REFUSE: input SHA256 {got} != Test A {EXPECTED_INPUT_SHA256}")
    if original[:4]!=b"LCFG": raise SystemExit("REFUSE: missing LCFG header")
    payload_size=struct.unpack_from("<I",original,LCFG_SIZE_OFF)[0]
    if payload_size!=len(original)-LCFG_HEADER: raise SystemExit("REFUSE: inconsistent LCFG payload size")

    fw=bytearray(original)
    call_off=CALL_VA-BASE
    if struct.unpack_from("<I",fw,call_off)[0]!=OLD_CALL:
        raise SystemExit("REFUSE: BurnDrvFrame call site no longer matches Test A")

    cave_off=CAVE_VA-BASE
    if fw[cave_off:cave_off+CAVE_LEN] != b"\x00"*CAVE_LEN:
        raise SystemExit("REFUSE: selected executable padding is not zero in exact Test A")

    # The preceding word is the delay-slot NOP of an existing jump. Do not use it.
    if struct.unpack_from("<I",fw,cave_off-4)[0] != 0:
        raise SystemExit("REFUSE: cave boundary/delay-slot contract changed")
    # Following bytes begin the existing space-filled data block.
    if fw[cave_off+CAVE_LEN:cave_off+CAVE_LEN+8] != b"\x00"*8:
        raise SystemExit("REFUSE: expected remaining zero padding after shim changed")

    struct.pack_into("<I",fw,call_off,jal(CAVE_VA))
    fw[cave_off:cave_off+CAVE_LEN]=SHIM

    new_crc=crc32_mpeg2(fw[LCFG_HEADER:])
    struct.pack_into("<I",fw,LCFG_CRC_OFF,new_crc)

    allowed=set(range(LCFG_CRC_OFF,LCFG_CRC_OFF+4))
    allowed.update(range(call_off,call_off+4))
    allowed.update(range(cave_off,cave_off+CAVE_LEN))
    changed=[i for i,(a,b) in enumerate(zip(original,fw)) if a!=b]
    unexpected=[i for i in changed if i not in allowed]
    if unexpected: raise SystemExit(f"REFUSE: unexpected changes {unexpected[:16]}")
    if crc32_mpeg2(fw[LCFG_HEADER:])!=new_crc: raise SystemExit("REFUSE: CRC self-check failed")

    args.output.write_bytes(fw)
    print(f"input_sha256={got}")
    print(f"output_sha256={sha256(fw)}")
    print(f"lcfg_crc32_mpeg2=0x{new_crc:08X}")
    print(f"changed_bytes={len(changed)}")
    print(f"call_patch={CALL_VA:#010x}: {OLD_CALL:#010x} -> {jal(CAVE_VA):#010x}")
    print(f"shim={CAVE_VA:#010x}..{CAVE_VA+CAVE_LEN-1:#010x}")
    print("producer_schedule=367/368 alternating from existing frame-counter parity")

if __name__=="__main__":main()
