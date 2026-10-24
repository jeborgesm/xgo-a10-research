#!/usr/bin/env python3
"""Read-only BIN assertion for XGO's P1-dependent P2 first-slot sample path.

Usage: python3 verify_original_xgo_slot0_p1_path.py /path/to/XGoAnalisis.zip
       python3 verify_original_xgo_slot0_p1_path.py /path/to/bios/bisrv.asd
Original vendor BIOS is not redistributed. No firmware modification.
"""
import hashlib
import json
import struct
import sys
import zipfile
from pathlib import Path

SHA256 = "869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf"
# MIPS32 little-endian words from precisely identified original vendor executable.
WORDS = {
    0x8035D870: 0x8E8A0000,  # lw t2,0(s4)       P1 serial GPIO
    0x8035D874: 0x31498000,  # andi t1,t2,0x8000
    0x8035D878: 0x15200005,  # bne t1,zero,+5   branch when P1 released
    0x8035D87C: 0x36710050,  # branch delay slot
    0x8035D880: 0x8F91F2D4,  # extra P1-pressed path
    0x8035D884: 0x36301000,
    0x8035D888: 0xAF90F2D4,
    0x8035D88C: 0x36710050,
    0x8035D890: 0x8E390000,  # lw t9,0(s1)       P2 serial GPIO
    0x8035D894: 0x33330001,  # andi s3,t9,1
    0x8035D898: 0x16600003,  # P2 bit evaluation
    0x8035D8B0: 0x8E490000,  # start shared CLOCK-low sequence
    0x8035D8BC: 0xAE480000,  # first shared CLOCK-low register write
}

def inspect(path):
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z:
            binary = z.read("bios/bisrv.asd")
    else:
        binary = Path(path).read_bytes()
    digest = hashlib.sha256(binary).hexdigest()
    if digest != SHA256:
        raise ValueError(f"Wrong BIOS hash: {digest}")
    for pc, expected in WORDS.items():
        word = struct.unpack_from("<I", binary, pc - 0x80000000)[0]
        if word != expected:
            raise ValueError(f"0x{pc:08x}: 0x{word:08x} != 0x{expected:08x}")
    branch = WORDS[0x8035D878]
    assert branch >> 26 == 5                            # MIPS BNE opcode
    assert (branch >> 21) & 31 == 9                     # rs=t1
    assert (branch >> 16) & 31 == 0                     # rt=zero
    disp = branch & 0xffff
    if disp & 0x8000: disp -= 65536
    assert 0x8035D878 + 4 + disp * 4 == 0x8035D890
    return {
        "BIN": "PASS (exact original firmware hash and opcode assertions)",
        "p1_slot0_sample": "0x8035D870",
        "p2_slot0_sample": "0x8035D890",
        "p1_released_high": "BNE taken; P2 read on shorter path",
        "p1_pressed_low": "BNE not taken; four extra instructions before P2 read",
        "shared_first_clock_low_write": "0x8035D8BC (after both reads)",
        "cycle_count_or_actual_voltages": "OPEN; not measured",
    }

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: verify_original_xgo_slot0_p1_path.py XGoAnalisis.zip|bisrv.asd")
    print(json.dumps(inspect(sys.argv[1]), indent=2))
