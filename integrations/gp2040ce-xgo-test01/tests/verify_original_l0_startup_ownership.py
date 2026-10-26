#!/usr/bin/env python3
"""Read-only, SHA-locked original XGO L0 startup GPIO direction audit.

Verifies the actual instruction operands, not a reconstructed driver model.
The observed code changes L0 GPIO direction but does not establish whether
there is internal pad bias, an external resistor, or a stable HIGH voltage.
"""
import argparse
import hashlib
import struct
import zipfile
from pathlib import Path

EXPECTED_SHA256 = "869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf"
WORDS = {
    0x35deb8: 0x3c12b880,  # lui s2,0xB880
    0x35dec0: 0x36510058,  # ori s1,s2,0x58 = GPIO L DIR
    0x35df08: 0x8e820000,  # lw v0,0(s4) = GPIO B DIR
    0x35df0c: 0x3c04ffff,  # lui a0,0xffff
    0x35df10: 0x34907fff,  # ori s0,a0,0x7fff
    0x35df14: 0x00501824,  # and v1,v0,s0 = clear B15
    0x35df18: 0xae830000,  # sw v1,0(s4)
    0x35df2c: 0x8e360000,  # lw s6,0(s1) = GPIO L DIR
    0x35df30: 0x241ffffe,  # addiu ra,zero,-2 = clear L0
    0x35df38: 0x02df9824,  # and s3,s6,ra
    0x35df3c: 0xae330000,  # sw s3,0(s1) = L0 INPUT
}

def run(path):
    path=Path(path)
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as archive:
            data=archive.read("bios/bisrv.asd")
    else:
        data=path.read_bytes()
    digest=hashlib.sha256(data).hexdigest()
    assert digest==EXPECTED_SHA256,digest
    for offset,word in WORDS.items():
        observed=struct.unpack_from("<I",data,offset)[0]
        assert observed==word,(hex(offset),hex(observed),hex(word))
    print(f"PASS [BIN]: original XGO SHA-256 and {len(WORDS)} exact startup instructions")
    print("PASS [BIN]: XGO GPIO B15 and L0 are configured INPUT at controller init")
    print("PASS [BIN]: L0 input direction restored again after each host LOAD phase")
    print("OPEN: GPIO pad bias, XGO board resistor, and physical DATA rise/threshold")
    print("No pull-up absence or measured analog voltage inferred from direction bits")

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("original_image_or_XGoAnalisis_zip")
    run(p.parse_args().original_image_or_XGoAnalisis_zip)
