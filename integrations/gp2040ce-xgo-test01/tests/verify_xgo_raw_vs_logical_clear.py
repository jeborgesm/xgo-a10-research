#!/usr/bin/env python3
"""Read-only original XGO MIPS pointer-provenance verification.

Corrects historical note that 0x8035D54C clears raw serial input:
it clears logical destination after a0 is REASSIGNED at 0x8035D534.
"""
import hashlib
import struct
import sys
import zipfile
from pathlib import Path

ORIG_SHA = "869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf"
WORDS = {
    0x35D4FC: 0x2795F2D4, # s5 = gp - 0xd2c (raw serial base)
    0x35D508: 0x279EF2E8, # fp = gp - 0xd18 (logical base)
    0x35D520: 0x00074080, # t0 = player index * 4
    0x35D524: 0x01152021, # a0 = t0 + s5 ; raw
    0x35D52C: 0x8C940000, # s4 = *a0 (raw)
    0x35D534: 0x011E2021, # a0 = t0 + fp ; REPOINT logical
    0x35D548: 0x12400003, # beq s2,zero,0x8035D558
    0x35D54C: 0xAC800000, # sw zero,0(a0) ; LOGICAL, delay slot
    0x35D764: 0x1500FF6D, # alternate normalization loop
    0x35D768: 0xAF80F2F8, # clears auxiliary scratch, NOT serial
    0x35D780: 0xAF80F2D4, # scanner resets raw P1
    0x35D788: 0xAF80F2D8, # scanner resets raw P2
    0x35DE10: 0x1000FDC3, # scan tail back to normalizer
}

def main(path):
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z:
            blob = z.read("bios/bisrv.asd")
    else:
        blob = Path(path).read_bytes()
    assert hashlib.sha256(blob).hexdigest() == ORIG_SHA
    for offset, word in WORDS.items():
        actual = struct.unpack_from("<I", blob, offset)[0]
        assert actual == word, (hex(offset), hex(actual), hex(word))
    assert 0x35D534 < 0x35D54C
    print("PASS original BIOS SHA and 13 opcode assertions")
    print("BIN: raw read d52c -> a0 repointed to LOGICAL d534 -> logical clear d54c")
    print("BIN: scanner clears raw P1/P2 at d780/d788 before new acquisition")
    print("LIMIT: other global writes/runtime paths remain unreviewed")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: verify_xgo_raw_vs_logical_clear.py XGoAnalisis.zip|bisrv.asd")
    main(sys.argv[1])
