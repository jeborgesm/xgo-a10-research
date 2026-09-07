#!/usr/bin/env python3
"""
Build XGO Game-List Test04: on-device staged SFC catalog replacement.

Inputs:
  --v8-zip     exact hardware-confirmed Audio OSD v8 golden ZIP
  --test03-zip exact hardware-confirmed generated-wrapper Test03 golden ZIP

The resulting package intentionally isolates one question:
Can XGO itself rewrite a synchronized built-in catalog triplet from a stock UI action?

Test04 is NOT the final scanner. It installs:
  - stock/original SFC catalogs (929 entries);
  - SFC/XGO Import Test.zsf physically present but unindexed;
  - Resources/refresh.bin containing the known-good 930-entry triplet;
  - a firmware hook on User Menu -> User Games.

When User Games is confirmed, the device reads refresh.bin into the native scanner
scratch arena, rewrites the three SFC catalogs using stock stdio, calls fs_sync,
invalidates the SFC cached count, and then continues to the untouched stock
User Games path.

This proof is intentionally non-transactional. Use only on a disposable SD clone.
"""

from __future__ import annotations
import argparse, hashlib, struct, zipfile
from pathlib import Path

V8_ZIP_SHA = "ba3dad99471c6144fd8f6e9f5891bc88d44b955c5de8a21df905d0d396cdb83a"
V8_FW_SHA  = "4b8f7af994d16371a2664a3d46c983e52ffd1aefbebc5b5a4a9ae63dc6cbe954"
TEST03_ZIP_SHA = "bfef6f95adaf7cd986061154d20e500580135930426994b5ed3b44c822987320"
TEST03_WRAPPER_SHA = "f600c45d37a77d9af80ecb1ad136e1dbcfbb7e22fd9afc91531f82cfd2fb03b1"

ORIGINAL = {
    "urefs.tax": ("ba65a0e993772dc7654449f10402be7536f7d8c7fca768c2db0174fc4b863dc0", 26993),
    "adsnt.nec": ("ffc96b0a4efc8177766ef7dafeb519a761bdfff2552d3cb8dbab2be465a7231c", 21082),
    "xvb6c.bvs": ("0a83d27343dd894802d64c8fbc68d8d9a6181d70446a443b9e9209e69a11bb24", 10290),
}
UPDATED = {
    "urefs.tax": ("f2cbc51c08689229216fab1024d7acd7c62480d96812d97c2efe984f1fe63916", 27017),
    "adsnt.nec": ("c010fca8f276bd73f34b7c01357979d94680961d4238fbb55521d589228ba2cb", 21102),
    "xvb6c.bvs": ("ccc7339310b785dce8537014af408b7e0aa09e9025dc2584ebac49bd159c032b", 10310),
}

POLY = 0x04C11DB7
BASE = 0x80000000
CAVE = 0x807DAB98
CAVE_LIMIT = 0x807DBBA0
HOOK = 0x80359E98
HOOK_OFF = HOOK - BASE
EXPECTED_HOOK = 0x1060F573
EXPECTED_DELAY = 0x240E0001

STOCK_USER_GAMES=0x80357468
STOCK_LANG=0x8035AE28
STOCK_OTHER=0x80356BFC
STOCK_TV=0x80359EB0
SPRINTF=0x802946D8
FOPEN=0x802B3524
FREAD=0x802B3698
FWRITE=0x802B42AC
FCLOSE=0x802B2F40
FS_SYNC_WRAP=0x807D40A8
PATHBUF=0x8109F65C
ROOT=0x8109F25C
PATHFMT=0x809A33DC
MODE_RB=0x809A6687
MODE_WB=0x809A3404
SFC_NAMES=0x80A3C344
COUNT_SFC=0x80D28954
SIZES=[UPDATED[n][1] for n in ("urefs.tax","adsnt.nec","xvb6c.bvs")]
TOTAL=sum(SIZES)

R={'zero':0,'at':1,'v0':2,'v1':3,'a0':4,'a1':5,'a2':6,'a3':7,'t0':8,'t1':9,'t2':10,'t3':11,'t4':12,'t5':13,'t6':14,'t7':15,'s0':16,'s1':17,'s2':18,'s3':19,'s4':20,'s5':21,'s6':22,'s7':23,'t8':24,'t9':25,'k0':26,'k1':27,'gp':28,'sp':29,'fp':30,'ra':31}

def sha(b: bytes) -> str: return hashlib.sha256(b).hexdigest()
def rtype(rs,rt,rd,sh,fn): return (R[rs]<<21)|(R[rt]<<16)|(R[rd]<<11)|(sh<<6)|fn
def iop(op,rs,rt,imm): return (op<<26)|(R[rs]<<21)|(R[rt]<<16)|(imm&0xffff)
def jop(op,addr): return (op<<26)|((addr>>2)&0x03ffffff)
def lui(rt,imm): return iop(15,'zero',rt,imm)
def ori(rt,rs,imm): return iop(13,rs,rt,imm)
def addiu(rt,rs,imm): return iop(9,rs,rt,imm)
def lw(rt,off,rs): return iop(35,rs,rt,off)
def sw(rt,off,rs): return iop(43,rs,rt,off)
def beq(rs,rt,off): return iop(4,rs,rt,off)
def bne(rs,rt,off): return iop(5,rs,rt,off)
def addu(rd,rs,rt): return rtype(rs,rt,rd,0,0x21)
def mfhi(rd): return rtype('zero','zero',rd,0,0x10)
def mflo(rd): return rtype('zero','zero',rd,0,0x12)
def mthi(rs): return rtype(rs,'zero','zero',0,0x11)
def mtlo(rs): return rtype(rs,'zero','zero',0,0x13)
def jal(addr): return jop(3,addr)
def j(addr): return jop(2,addr)
def nop(): return 0

def split_addr(addr):
    lo=addr&0xffff; hi=(addr>>16)&0xffff
    if lo&0x8000: hi=(hi+1)&0xffff
    return hi,(lo-0x10000 if lo&0x8000 else lo)

class Asm:
    def __init__(self,base): self.base=base; self.items=[]; self.labels={}
    def size(self):
        return sum(8 if t=='la' else 4 if t in ('i','b') else len(v) for t,v in self.items)
    @property
    def pc(self): return self.base+self.size()
    def label(self,n): self.labels[n]=self.pc
    def ins(self,w): self.items.append(('i',w))
    def branch(self,k,rs,rt,label): self.items.append(('b',(k,rs,rt,label)))
    def loadaddr(self,r,addr):
        hi,lo=split_addr(addr); self.ins(lui(r,hi)); self.ins(addiu(r,r,lo))
    def loadlabel(self,r,label): self.items.append(('la',(r,label)))
    def data(self,b): self.items.append(('d',bytes(b)))
    def emit(self):
        out=bytearray(); pc=self.base
        for typ,val in self.items:
            if typ=='i': out += struct.pack('<I',val); pc += 4
            elif typ=='b':
                kind,rs,rt,label=val; delta=self.labels[label]-(pc+4)
                assert delta%4==0
                off=delta//4; assert -32768<=off<=32767
                out += struct.pack('<I',beq(rs,rt,off) if kind=='beq' else bne(rs,rt,off)); pc += 4
            elif typ=='la':
                reg,label=val; hi,lo=split_addr(self.labels[label])
                out += struct.pack('<II',lui(reg,hi),addiu(reg,reg,lo)); pc += 8
            else: out += val; pc += len(val)
        return bytes(out)

def build_blob():
    a=Asm(CAVE)
    # Recreate stock state-14 row dispatch. Hook delay slot still executes li t6,1.
    a.branch('beq','v1','zero','refresh'); a.ins(nop())
    a.ins(addiu('t1','zero',2))
    a.branch('beq','v1','t6','lang'); a.ins(nop())
    a.branch('bne','v1','t1','other'); a.ins(addiu('s2','zero',1))
    a.ins(j(STOCK_TV)); a.ins(nop())
    a.label('lang'); a.ins(j(STOCK_LANG)); a.ins(addiu('t1','zero',2))
    a.label('other'); a.ins(j(STOCK_OTHER)); a.ins(addiu('s2','zero',1))

    a.label('refresh')
    FRAME=160
    save_regs=['v0','v1','a0','a1','a2','a3','t0','t1','t2','t3','t4','t5','t6','t7','s0','s1','s2','s3','s4','s5','s6','s7','t8','t9','gp','fp','ra']
    a.ins(addiu('sp','sp',-FRAME))
    for idx,reg in enumerate(save_regs): a.ins(sw(reg,16+idx*4,'sp'))
    a.ins(mfhi('t0')); a.ins(sw('t0',124,'sp'))
    a.ins(mflo('t0')); a.ins(sw('t0',128,'sp'))

    # Native scanner's large scratch arena.
    a.ins(lw('s0',-3228,'gp')); a.ins(lui('t0',0x0210)); a.ins(addu('s0','s0','t0'))

    # Open Resources/refresh.bin.
    a.loadaddr('a0',PATHBUF); a.loadaddr('a1',PATHFMT); a.loadaddr('a2',ROOT); a.loadlabel('a3','srcname')
    a.ins(jal(SPRINTF)); a.ins(nop())
    a.loadaddr('a0',PATHBUF); a.loadaddr('a1',MODE_RB); a.ins(jal(FOPEN)); a.ins(nop())
    a.branch('beq','v0','zero','restore'); a.ins(nop()); a.ins(addu('s1','v0','zero'))

    # Read complete staged triplet before truncating any canonical resource.
    a.ins(addu('a0','s0','zero')); a.ins(addiu('a1','zero',1)); a.ins(ori('a2','zero',TOTAL)); a.ins(addu('a3','s1','zero'))
    a.ins(jal(FREAD)); a.ins(nop())
    a.ins(ori('t0','zero',TOTAL)); a.branch('bne','v0','t0','close_src_restore'); a.ins(nop())
    a.ins(addu('a0','s1','zero')); a.ins(jal(FCLOSE)); a.ins(nop())

    a.ins(addu('s1','s0','zero')); a.loadaddr('s2',SFC_NAMES); a.loadlabel('s3','sizes'); a.ins(addiu('s4','zero',3))
    a.label('copy_loop')
    a.ins(lw('s5',0,'s3'))
    a.loadaddr('a0',PATHBUF); a.loadaddr('a1',PATHFMT); a.loadaddr('a2',ROOT); a.ins(lw('a3',0,'s2'))
    a.ins(jal(SPRINTF)); a.ins(nop())
    a.loadaddr('a0',PATHBUF); a.loadaddr('a1',MODE_WB); a.ins(jal(FOPEN)); a.ins(nop())
    a.branch('beq','v0','zero','restore'); a.ins(nop()); a.ins(addu('s6','v0','zero'))
    a.ins(addu('a0','s1','zero')); a.ins(addiu('a1','zero',1)); a.ins(addu('a2','s5','zero')); a.ins(addu('a3','s6','zero'))
    a.ins(jal(FWRITE)); a.ins(nop()); a.ins(addu('s7','v0','zero'))
    a.ins(addu('a0','s6','zero')); a.ins(jal(FCLOSE)); a.ins(nop())
    a.branch('bne','s7','s5','restore'); a.ins(nop())
    a.ins(addu('s1','s1','s5')); a.ins(addiu('s2','s2',4)); a.ins(addiu('s3','s3',4)); a.ins(addiu('s4','s4',-1))
    a.branch('bne','s4','zero','copy_loop'); a.ins(nop())

    a.ins(jal(FS_SYNC_WRAP)); a.ins(nop())
    a.loadaddr('t0',COUNT_SFC); a.ins(sw('zero',0,'t0'))
    a.branch('beq','zero','zero','restore'); a.ins(nop())

    a.label('close_src_restore')
    a.ins(addu('a0','s1','zero')); a.ins(jal(FCLOSE)); a.ins(nop())

    a.label('restore')
    a.ins(lw('t0',124,'sp')); a.ins(mthi('t0')); a.ins(lw('t0',128,'sp')); a.ins(mtlo('t0'))
    for idx,reg in reversed(list(enumerate(save_regs))):
        if reg!='t0': a.ins(lw(reg,16+idx*4,'sp'))
    a.ins(lw('t0',16+save_regs.index('t0')*4,'sp'))
    a.ins(addiu('sp','sp',FRAME)); a.ins(j(STOCK_USER_GAMES)); a.ins(nop())

    while a.pc%4: a.data(b'\0')
    a.label('sizes'); a.data(struct.pack('<III',*SIZES))
    a.label('srcname'); a.data(b'refresh.bin\0')
    blob=a.emit()
    assert CAVE+len(blob) < CAVE_LIMIT
    return blob

def crc32_mpeg2(data):
    crc=0xffffffff
    for byte in data:
        crc ^= byte<<24
        for _ in range(8):
            crc=(((crc<<1)^POLY) if crc&0x80000000 else crc<<1)&0xffffffff
    return crc

def reverse_last_append(data: bytes) -> bytes:
    count=struct.unpack_from('<I',data,0)[0]
    assert count==930
    new_blob_start=4+count*4
    last_off=struct.unpack_from('<I',data,4+(count-1)*4)[0]
    old_offsets=data[4:4+(count-1)*4]
    old_blob=data[new_blob_start:new_blob_start+last_off]
    return struct.pack('<I',count-1)+old_offsets+old_blob

def zi(name):
    z=zipfile.ZipInfo(name,(2026,9,6,12,0,0)); z.compress_type=zipfile.ZIP_DEFLATED
    z.create_system=3; z.external_attr=0o600<<16; return z

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--v8-zip',type=Path,required=True)
    ap.add_argument('--test03-zip',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()

    assert sha(args.v8_zip.read_bytes())==V8_ZIP_SHA
    assert sha(args.test03_zip.read_bytes())==TEST03_ZIP_SHA

    with zipfile.ZipFile(args.v8_zip) as z: fw=bytearray(z.read('bios/bisrv.asd'))
    assert sha(fw)==V8_FW_SHA

    with zipfile.ZipFile(args.test03_zip) as z:
        wrapper=z.read('SFC/XGO Import Test.zsf')
        updated={n:z.read('Resources/'+n) for n in UPDATED}
    assert sha(wrapper)==TEST03_WRAPPER_SHA
    for n,b in updated.items():
        assert (sha(b),len(b))==UPDATED[n]

    original={n:reverse_last_append(updated[n]) for n in updated}
    for n,b in original.items():
        assert (sha(b),len(b))==ORIGINAL[n]

    refresh=b''.join(updated[n] for n in ('urefs.tax','adsnt.nec','xvb6c.bvs'))
    assert len(refresh)==TOTAL

    blob=build_blob()
    cave_off=CAVE-BASE
    assert fw[cave_off:cave_off+len(blob)]==b'\0'*len(blob)
    assert struct.unpack_from('<I',fw,HOOK_OFF)[0]==EXPECTED_HOOK
    assert struct.unpack_from('<I',fw,HOOK_OFF+4)[0]==EXPECTED_DELAY
    fw[cave_off:cave_off+len(blob)]=blob
    struct.pack_into('<I',fw,HOOK_OFF,j(CAVE))
    crc=crc32_mpeg2(fw[0x200:])
    struct.pack_into('<I',fw,0x18c,crc)

    readme=f"""XGO GAME-LIST TEST04 — ON-DEVICE STAGED SFC CATALOG WRITE

PURPOSE
-------
Prove the XGO itself can rewrite a synchronized built-in catalog triplet from
a stock frontend action.

PROTECTED BASE
--------------
Audio OSD v8 firmware:
{V8_FW_SHA}

TRIGGER
-------
User Menu -> User Games

The stock row-0 action is intercepted, the staged SFC triplet is written by the
device itself, the SFC count cache is invalidated, then control continues to the
normal stock User Games path.

INSTALL STATE
-------------
The ZIP deliberately installs the ORIGINAL 929-entry SFC catalogs plus:
  SFC/XGO Import Test.zsf
  Resources/refresh.bin

Therefore XGO Import Test is physically present but initially unindexed.

EXPECTED TEST
-------------
1. Use a disposable SD clone.
2. Install this ZIP.
3. Boot.
4. BEFORE selecting User Menu -> User Games, open SFC:
     expected count = 929
     XGO Import Test should NOT be listed.
5. Return and select User Menu -> User Games once.
6. Return to SFC:
     expected count = 930
     final item = XGO Import Test.
7. Launch XGO Import Test; controller test should behave like Test03.
8. Reboot and confirm the 930-entry SFC list persists.
9. Confirm the existing Mega Man Favorite still opens normally.
10. Briefly verify Language and TV System User Menu rows still behave normally.

SAFETY
------
TEST04 IS INTENTIONALLY NON-TRANSACTIONAL.
It is a runtime-write proof only. A power loss during the three canonical writes
could leave the SFC triplet inconsistent. Use only a disposable clone.

Reinstalling this ZIP restores the original 929-entry SFC triplet before another
attempt.

PATCH
-----
hook runtime: 0x{HOOK:08x}
writer cave:  0x{CAVE:08x}
writer bytes: {len(blob)}
writer SHA-256: {sha(blob)}
refresh.bin bytes: {len(refresh)}
LCFG CRC-32/MPEG-2: 0x{crc:08x}

Candidate firmware SHA-256:
{sha(fw)}
""".encode()

    with zipfile.ZipFile(args.output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        z.writestr(zi('README-HARDWARE-TEST.txt'),readme)
        z.writestr(zi('bios/bisrv.asd'),bytes(fw))
        for n in ('urefs.tax','adsnt.nec','xvb6c.bvs'): z.writestr(zi('Resources/'+n),original[n])
        z.writestr(zi('Resources/refresh.bin'),refresh)
        z.writestr(zi('SFC/XGO Import Test.zsf'),wrapper)

    print('writer',len(blob),sha(blob))
    print('firmware',sha(fw))
    print('zip',sha(args.output.read_bytes()))

if __name__=='__main__': main()
