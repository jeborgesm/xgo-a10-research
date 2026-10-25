#!/usr/bin/env python3
"""BIN: original XGO MIPS scanner IRQ gating. Read-only SHA-pinned verification.

Run: python3 verify_xgo_irq_windows_original_bin.py XGoAnalisis.zip
Helper calls mean IRQ *can* be enabled; no timing or actual IRQ occurrence
is inferred from instructions alone.
"""
import hashlib
import struct
import sys
import zipfile
from pathlib import Path

ORIGINAL_SHA="869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf"
BEGIN,END=0x35d770,0x35de04
IRQ_DISABLE,IRQ_ENABLE,DELAY=0x2e0750,0x2e0778,0x30fed0

def verify(path):
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z: b=z.read("bios/bisrv.asd")
    else: b=Path(path).read_bytes()
    assert hashlib.sha256(b).hexdigest()==ORIGINAL_SHA
    op=lambda off:struct.unpack_from("<I",b,off)[0]
    def jal(at):
        word=op(at)
        assert word>>26==3
        return ((at+4)&0xf0000000)|((word&0x3ffffff)<<2)
    calls=[(a,jal(a)) for a in range(BEGIN,END,4) if op(a)>>26==3]
    on=[a for a,dest in calls if dest==IRQ_ENABLE]
    off=[a for a,dest in calls if dest==IRQ_DISABLE]
    delay=[a for a,dest in calls if dest==DELAY]
    assert len(on)==len(off)==30
    assert len(delay)==13

    assert [op(a) for a in (0x2e0758,0x2e0760,0x2e0764,0x2e0768)]==[
        0x0c012769,0x8f829b10,0x24420001,0xaf829b10]
    assert [op(a) for a in (0x2e0780,0x2e0784,0x2e0788,
                              0x2e078c,0x2e0790,0x2e0794)]==[
        0x8f829b10,0x2442ffff,0x1c400003,0xaf829b10,
        0x0c01277d,0xaf809b10]
    assert jal(0x2e0758)==0x49da4
    assert jal(0x2e0790)==0x49df4
    assert op(0x49da4)==op(0x49df4)==0x40086000 # mfc0 Status
    assert op(0x49dcc)==op(0x49e18)==0x40886000 # mtc0 Status
    assert op(0x49dc4)==0x2409fffe # mask IE bit0
    assert op(0x49e14)==0x35080001 # set IE bit0
    assert op(0x49db8)==op(0x49e08)==0x24090006 # EXL/ERL mask

    # Host P1 B15 and Handle L0 DATA output-enable release, then IRQ
    # re-enable helper immediately before sampling slot0.
    words={0x35d844:0xae2e0000,0x35d848:0x0c0b81de,
           0x35d850:0x0c0b81d4,0x35d864:0xae0b0000,
           0x35d868:0x0c0b81de,0x35d870:0x8e8a0000,
           0x35d878:0x15200005,0x35d890:0x8e390000,
           0x35d8a8:0x0c0b81d4}
    for a,w in words.items():assert op(a)==w,(hex(a),hex(op(a)),hex(w))
    assert 0x35d848 in on and 0x35d850 in off
    assert 0x35d868 in on and 0x35d8a8 in off
    assert 0x35d864<0x35d868<0x35d870<0x35d890<0x35d8a8

    # Three consecutive 2us CLOCK LOW windows: LOW store, IRQ-enable
    # helper, nominal delay, IRQ-disable helper, HIGH store.
    for low,on_addr,dly,off_addr,high in zip(
        (0x35d8bc,0x35d934,0x35d9ac),
        (0x35d8c0,0x35d938,0x35d9b0),
        (0x35d8c8,0x35d940,0x35d9b8),
        (0x35d8d0,0x35d948,0x35d9c0),
        (0x35d8e4,0x35d95c,0x35d9d4)):
        assert low<on_addr<dly<off_addr<high
        assert on_addr in on and dly in delay and off_addr in off
        assert op(dly+4)==0x24040002
        assert op(low)>>26==43 and op(high)>>26==43
    assert op(0x35d828)==0x24040004

    print("PASS BIN: 30 disable and 30 enable helper calls in host scanner")
    print("PASS BIN: nesting-counter helpers reach CP0 Status IE-clear/set")
    print("PASS BIN: physical Handle DATA release -> IRQ enable -> P1/P2 R sample")
    print("PASS BIN: CLOCK LOW windows include IRQ-enable + 2us delay + IRQ-disable")
    print("LIMIT: actual IRQ delivery, duration and bus waveform remain unmeasured")

if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("usage: python verify_xgo_irq_windows_original_bin.py XGoAnalisis.zip")
    verify(sys.argv[1])
