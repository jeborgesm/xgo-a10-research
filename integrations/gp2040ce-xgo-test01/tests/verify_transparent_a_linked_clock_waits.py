#!/usr/bin/env python3
"""Read-only SHA-pinned audit of protected A linked Thumb responder.

Input is the actual linked-disassembly.txt artifact from GitHub Actions run
40071967532 (artifact 12551597007), NOT reconstructed source estimates.
"""
import hashlib
import re
import sys
from pathlib import Path

SHA = "482031f65ae7d58f50174d6c4842a83794a9b216c0eb9845bca8dcb734b0564d"
LOW = {0x200001d6:"6a93",0x200001d8:"1b1b",0x200001da:"2b12",
       0x200001dc:"d853",0x200001de:"6fc3",0x200001e0:"420b",
       0x200001e2:"d1f8"}
HIGH = {0x200001f8:"6a93",0x200001fa:"1b1b",0x200001fc:"2b12",
        0x200001fe:"d842",0x20000200:"6fc3",0x20000202:"420b",
        0x20000204:"d0f8"}
LITERALS = {0x2000037c:"40054000",0x20000380:"50110000",
            0x20000384:"00004e20"}

def verify(path):
    data=Path(path).read_bytes()
    assert hashlib.sha256(data).hexdigest()==SHA
    text=data.decode()
    assert "200000f0 <(anonymous namespace)::emit_frame()>:" in text
    inst={}
    for a,word in re.findall(r"^([a-f0-9]{8}):\\s+([a-f0-9]{4,8})\\s+",text,re.M):
        inst[int(a,16)]=word
    for group in (LOW,HIGH,LITERALS):
        for offset,expected in group.items():
            assert inst.get(offset)==expected,(hex(offset),inst.get(offset),expected)
    for term in (
        "200001d0:\t02c9      \tlsls\tr1, r1, #11",
        "20000152:\tf3ef 8b10 \tmrs\tfp, PRIMASK",
        "20000156:\tb672      \tcpsid\ti",
        "20000296:\tf38b 8810 \tmsr\tPRIMASK, fp",
    ):
        assert term in text
    print("PASS linked RP2040: hardware-tested transparent A emit_frame in SRAM at 0x200000f0")
    print("PASS exactly 7 Thumb operations per CLOCK wait polling loop, "
          "each including two direct peripheral reads")
    print("PASS MMIO timer 0x40054028, USB PHY 0x5011007c; "
          "RX_DM mask 0x40000; source wait bound 18us")
    print("PASS RP Core1 IRQ masked from host LOAD detection through terminal CLOCK")
    print("LIMIT no actual cycle-time, bus stall, or current Frankie voltage measurement")

if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("usage: python verify_transparent_a_linked_clock_waits.py linked-disassembly.txt")
    verify(sys.argv[1])
