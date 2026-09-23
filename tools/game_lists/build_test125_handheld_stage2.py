#!/usr/bin/env python3
"""Build Test125 single-family handheld discovery Stage2 helpers.

Source lineage:
- readable Test07 stable-merge worker;
- HW-passed Test08 generalized discovery semantics;
- Test106 Stage2 execution address/size contract.

Each emitted helper is exactly 7000 bytes, executes at 0x87180000, scans ONE
physical handheld directory, stable-appends missing filenames to that stock
catalog triplet, invalidates only that frontend count cache, and returns:
  -1 failure, 0 no change, 1 changed.

No UI/status code and no firmware patching live here.
"""
from __future__ import annotations
import argparse, hashlib, struct
from pathlib import Path

BASE=0x87180000
OUT_SIZE=7000
SPRINTF=0x802946D8; MEMCPY=0x8029496C; STRCMP=0x80294DEC; STRLEN=0x80294E30
STRRCHR=0x801B0E38; STRCPY=0x80294DAC; UPPER_EXT=0x803526FC; EXT_CLASSIFY=0x80360A08
FOPEN=0x802B3524; FREAD=0x802B3698; FWRITE=0x802B42AC; FCLOSE=0x802B2F40
DIR_OPEN=0x807D40C4; DIR_NEXT=0x807D4124; DIR_CLOSE=0x807D41F4
TEST08_POST_WRITE_WRAP=0x807D40A8
PATHBUF=0x8109F65C; ROOT=0x8109F25C; PATHFMT=0x809A33DC
MODE_RB=0x809A6687; MODE_WB=0x809A3404

SYSTEMS={
 "gb":  dict(names=0x80A3C35C,count=0x80D28964,folder=b"GB", wrapper=6,native=(23,25)),
 "gbc": dict(names=0x80A3C368,count=0x80D2896C,folder=b"GBC",wrapper=6,native=(23,25)),
 "gba": dict(names=0x80A3C374,count=0x80D28974,folder=b"GBA",wrapper=6,native=(20,22)),
}
EXPECTED_SHA={
 "gb":"705198908eccb8e828bf4f121d1843bceef0e92a65a5e9a5d988a91e0f40209b",
 "gbc":"f31740039e53dbc051e37fa58347577762d1f9d6b27459c75cee5c0bbbb98246",
 "gba":"637c30ed10282e534704631e1261cc9fe9c25e051949271eaee15f9527137cbe",
}
CAT0=0x00000; CAT1=0x10000; CAT2=0x20000
OUT0=0x30000; OUT1=0x40000; OUT2=0x50000
ENTRY=0x60000; CANDS=0x61000; CAND_REC=0x240; MAX_CANDS=512
R={'zero':0,'at':1,'v0':2,'v1':3,'a0':4,'a1':5,'a2':6,'a3':7,'t0':8,'t1':9,'t2':10,'t3':11,'t4':12,'t5':13,'t6':14,'t7':15,'s0':16,'s1':17,'s2':18,'s3':19,'s4':20,'s5':21,'s6':22,'s7':23,'t8':24,'t9':25,'k0':26,'k1':27,'gp':28,'sp':29,'fp':30,'ra':31}
def sha(b): return hashlib.sha256(b).hexdigest()
def rtype(rs,rt,rd,sh,fn): return (R[rs]<<21)|(R[rt]<<16)|(R[rd]<<11)|(sh<<6)|fn
def iop(op,rs,rt,imm): return (op<<26)|(R[rs]<<21)|(R[rt]<<16)|(imm&0xffff)
def jop(op,addr): return (op<<26)|((addr>>2)&0x03ffffff)
def addiu(rt,rs,i): return iop(9,rs,rt,i)
def lui(rt,i): return iop(15,'zero',rt,i)
def ori(rt,rs,i): return iop(13,rs,rt,i)
def lw(rt,o,rs): return iop(35,rs,rt,o)
def sw(rt,o,rs): return iop(43,rs,rt,o)
def lbu(rt,o,rs): return iop(36,rs,rt,o)
def sb(rt,o,rs): return iop(40,rs,rt,o)
def beq(rs,rt,o): return iop(4,rs,rt,o)
def bne(rs,rt,o): return iop(5,rs,rt,o)
def sltiu(rt,rs,i): return iop(11,rs,rt,i)
def addu(rd,rs,rt): return rtype(rs,rt,rd,0,0x21)
def subu(rd,rs,rt): return rtype(rs,rt,rd,0,0x23)
def sltu(rd,rs,rt): return rtype(rs,rt,rd,0,0x2b)
def sll(rd,rt,sh): return rtype('zero',rt,rd,sh,0)
def jal(a): return jop(3,a)
def jalr(rd,rs): return rtype(rs,'zero',rd,0,9)
def jr(rs): return rtype(rs,'zero','zero',0,8)
def nop(): return 0
def bltz(rs,o): return (1<<26)|(R[rs]<<21)|(o&0xffff)
def split_addr(a):
 lo=a&0xffff; hi=(a>>16)&0xffff
 if lo&0x8000: hi=(hi+1)&0xffff
 return hi,lo-0x10000 if lo&0x8000 else lo

class Asm:
 def __init__(self,base): self.base=base; self.items=[]; self.labels={}
 def size(self): return sum(8 if t=='la' else 4 if t in ('i','b','bltz') else len(v) for t,v in self.items)
 @property
 def pc(self): return self.base+self.size()
 def label(self,n): self.labels[n]=self.pc
 def ins(self,w): self.items.append(('i',w))
 def branch(self,k,rs,rt,l): self.items.append(('b',(k,rs,rt,l)))
 def branch_bltz(self,rs,l): self.items.append(('bltz',(rs,l)))
 def loadaddr(self,r,a):
  hi,lo=split_addr(a); self.ins(lui(r,hi)); self.ins(addiu(r,r,lo))
 def loadlabel(self,r,l): self.items.append(('la',(r,l)))
 def data(self,b): self.items.append(('d',bytes(b)))
 def emit(self):
  out=bytearray(); pc=self.base
  for t,v in self.items:
   if t=='i': out+=struct.pack('<I',v); pc+=4
   elif t=='b':
    k,rs,rt,l=v; d=self.labels[l]-(pc+4); assert d%4==0; o=d//4; assert -32768<=o<=32767
    out+=struct.pack('<I',beq(rs,rt,o) if k=='beq' else bne(rs,rt,o)); pc+=4
   elif t=='bltz':
    rs,l=v; d=self.labels[l]-(pc+4); assert d%4==0; o=d//4; assert -32768<=o<=32767
    out+=struct.pack('<I',bltz(rs,o)); pc+=4
   elif t=='la':
    r,l=v; hi,lo=split_addr(self.labels[l]); out+=struct.pack('<II',lui(r,hi),addiu(r,r,lo)); pc+=8
   else: out+=v; pc+=len(v)
  return bytes(out)

def scratch(a,reg,off,tmp='t9'):
 high=off&~0xffff; low=off-high
 if high: a.ins(lui(tmp,high>>16)); a.ins(addu(reg,'s0',tmp))
 else: a.ins(addu(reg,'s0','zero'))
 if low: a.ins(addiu(reg,reg,low))

def candptr(a,dst,idx,shared=False):
 if shared: a.loadlabel('t8','cand_base'); a.ins(lw('t8',0,'t8'))
 else: scratch(a,'t8',CANDS,'t7')
 a.ins(sll('t6',idx,9)); a.ins(sll('t5',idx,6)); a.ins(addu('t6','t6','t5')); a.ins(addu(dst,'t8','t6'))

def build_slot(a):
 a.label('build_slot'); F=112; saved=['s0','s1','s2','s3','s4','s5','s6','s7','ra']
 a.ins(addiu('sp','sp',-F))
 for i,r in enumerate(saved): a.ins(sw(r,16+i*4,'sp'))
 a.ins(addu('s0','a0','zero')); a.ins(addu('s1','a1','zero')); a.ins(addu('s2','a2','zero')); a.ins(addu('s3','a3','zero'))
 a.ins(lw('s4',0,'s0')); a.ins(sll('s5','s4',2)); a.ins(addiu('s5','s5',4)); a.ins(sltu('t0','s1','s5')); a.branch('bne','t0','zero','bs_fail'); a.ins(nop())
 a.ins(subu('s6','s1','s5')); a.loadlabel('t0','cand_count'); a.ins(lw('s7',0,'t0')); a.ins(addu('t0','s4','s7')); a.ins(sw('t0',0,'s2')); a.ins(sw('s6',64,'sp'))
 a.ins(addiu('a0','s2',4)); a.ins(addiu('a1','s0',4)); a.ins(sll('a2','s4',2)); a.ins(jal(MEMCPY)); a.ins(nop())
 a.ins(sw('zero',68,'sp')); a.ins(sw('s6',72,'sp'))
 a.label('boff'); a.ins(lw('t0',68,'sp')); a.branch('beq','t0','s7','boff_done'); a.ins(nop())
 a.ins(sll('t1','s4',2)); a.ins(sll('t2','t0',2)); a.ins(addu('t1','t1','t2')); a.ins(addiu('t1','t1',4)); a.ins(addu('t1','s2','t1')); a.ins(lw('t2',72,'sp')); a.ins(sw('t2',0,'t1'))
 candptr(a,'t4','t0',True); a.ins(sw('t4',76,'sp')); a.branch('beq','s3','zero','boff_full'); a.ins(nop())
 a.ins(addu('a0','t4','zero')); a.ins(addiu('a1','zero',46)); a.ins(jal(STRRCHR)); a.ins(nop()); a.ins(lw('t4',76,'sp')); a.branch('beq','v0','zero','boff_full'); a.ins(nop()); a.ins(subu('t3','v0','t4')); a.branch('beq','zero','zero','boff_len'); a.ins(nop())
 a.label('boff_full'); a.ins(addu('a0','t4','zero')); a.ins(jal(STRLEN)); a.ins(nop()); a.ins(addu('t3','v0','zero'))
 a.label('boff_len'); a.ins(lw('t2',72,'sp')); a.ins(addiu('t3','t3',1)); a.ins(addu('t2','t2','t3')); a.ins(sw('t2',72,'sp')); a.ins(lw('t0',68,'sp')); a.ins(addiu('t0','t0',1)); a.ins(sw('t0',68,'sp')); a.branch('beq','zero','zero','boff'); a.ins(nop())
 a.label('boff_done'); a.ins(addu('t0','s4','s7')); a.ins(sll('t0','t0',2)); a.ins(addiu('t0','t0',4)); a.ins(addu('t1','s2','t0')); a.ins(sw('t1',80,'sp')); a.ins(addu('t2','s0','s5')); a.ins(addu('a0','t1','zero')); a.ins(addu('a1','t2','zero')); a.ins(addu('a2','s6','zero')); a.ins(jal(MEMCPY)); a.ins(nop()); a.ins(lw('t1',80,'sp')); a.ins(addu('t1','t1','s6')); a.ins(sw('t1',84,'sp')); a.ins(sw('zero',68,'sp'))
 a.label('bstr'); a.ins(lw('t0',68,'sp')); a.branch('beq','t0','s7','bs_done'); a.ins(nop()); candptr(a,'t4','t0',True); a.ins(sw('t4',76,'sp')); a.branch('beq','s3','zero','bstr_full'); a.ins(nop())
 a.ins(addu('a0','t4','zero')); a.ins(addiu('a1','zero',46)); a.ins(jal(STRRCHR)); a.ins(nop()); a.ins(lw('t4',76,'sp')); a.branch('beq','v0','zero','bstr_full'); a.ins(nop()); a.ins(subu('t3','v0','t4')); a.branch('beq','zero','zero','bstr_len'); a.ins(nop())
 a.label('bstr_full'); a.ins(addu('a0','t4','zero')); a.ins(jal(STRLEN)); a.ins(nop()); a.ins(addu('t3','v0','zero'))
 a.label('bstr_len'); a.ins(sw('t3',88,'sp')); a.ins(lw('t1',84,'sp')); a.ins(addu('a0','t1','zero')); a.ins(addu('a1','t4','zero')); a.ins(addu('a2','t3','zero')); a.ins(jal(MEMCPY)); a.ins(nop()); a.ins(lw('t1',84,'sp')); a.ins(lw('t3',88,'sp')); a.ins(addu('t1','t1','t3')); a.ins(sb('zero',0,'t1')); a.ins(addiu('t1','t1',1)); a.ins(sw('t1',84,'sp')); a.ins(lw('t0',68,'sp')); a.ins(addiu('t0','t0',1)); a.ins(sw('t0',68,'sp')); a.branch('beq','zero','zero','bstr'); a.ins(nop())
 a.label('bs_done'); a.ins(lw('t0',84,'sp')); a.ins(subu('v0','t0','s2')); a.ins(lui('t1',1)); a.ins(sltu('t2','v0','t1')); a.branch('bne','t2','zero','bs_ret'); a.ins(nop())
 a.label('bs_fail'); a.ins(addu('v0','zero','zero'))
 a.label('bs_ret')
 for i,r in reversed(list(enumerate(saved))): a.ins(lw(r,16+i*4,'sp'))
 a.ins(addiu('sp','sp',F)); a.ins(jr('ra')); a.ins(nop())

def build(system):
 cfg=SYSTEMS[system]; a=Asm(BASE)
 # Entry: preserve full callee state; helper owns no UI.
 F=192; saved=['s0','s1','s2','s3','s4','s5','s6','s7','ra']
 a.ins(addiu('sp','sp',-F))
 for i,r in enumerate(saved): a.ins(sw(r,16+i*4,'sp'))
 a.ins(lw('t0',-3236,'gp')); a.ins(sw('t0',64,'sp'))
 a.ins(lw('s0',-3228,'gp')); a.ins(lui('t0',0x0210)); a.ins(addu('s0','s0','t0'))
 scratch(a,'t0',CANDS); a.loadlabel('t1','cand_base'); a.ins(sw('t0',0,'t1'))
 # Read triplet.
 for off,ni,sz in [(CAT0,0,72),(CAT1,1,76),(CAT2,2,80)]:
  a.loadaddr('a0',PATHBUF); a.loadaddr('a1',PATHFMT); a.loadaddr('a2',ROOT); a.loadaddr('t0',cfg['names']); a.ins(lw('a3',ni*4,'t0')); a.ins(jal(SPRINTF)); a.ins(nop()); a.loadaddr('a0',PATHBUF); a.loadaddr('a1',MODE_RB); a.ins(jal(FOPEN)); a.ins(nop()); a.branch('beq','v0','zero','fail'); a.ins(nop()); a.ins(addu('s1','v0','zero')); scratch(a,'a0',off); a.ins(addiu('a1','zero',1)); a.ins(ori('a2','zero',0xffff)); a.ins(addu('a3','s1','zero')); a.ins(jal(FREAD)); a.ins(nop()); a.ins(addu('s2','v0','zero')); a.ins(addu('a0','s1','zero')); a.ins(jal(FCLOSE)); a.ins(nop()); a.ins(sw('s2',sz,'sp')); a.branch('beq','s2','zero','fail'); a.ins(nop())
 scratch(a,'t0',CAT0); scratch(a,'t1',CAT1); scratch(a,'t2',CAT2); a.ins(lw('t3',0,'t0')); a.ins(lw('t4',0,'t1')); a.ins(lw('t5',0,'t2')); a.branch('bne','t3','t4','fail'); a.ins(nop()); a.branch('bne','t3','t5','fail'); a.ins(nop()); a.branch('beq','t3','zero','fail'); a.ins(nop())
 # Directory scan.
 a.loadaddr('a0',PATHBUF); a.loadlabel('a1','dirfmt'); a.loadaddr('a2',ROOT); a.ins(jal(SPRINTF)); a.ins(nop()); a.loadaddr('a0',PATHBUF); a.ins(jal(DIR_OPEN)); a.ins(nop()); a.branch('beq','v0','zero','fail'); a.ins(nop()); a.ins(addu('s1','v0','zero')); a.ins(addu('s2','zero','zero')); scratch(a,'s3',ENTRY)
 a.label('scan'); a.ins(addu('a0','s1','zero')); a.ins(addu('a1','s3','zero')); a.ins(jal(DIR_NEXT)); a.ins(nop()); a.branch_bltz('v0','scan_done'); a.ins(lbu('t0',0,'s3')); a.branch('bne','t0','zero','scan'); a.ins(nop())
 candptr(a,'s4','s2'); a.ins(addiu('a1','s3',8)); a.ins(addu('a0','s4','zero')); a.ins(jal(STRCPY)); a.ins(nop()); a.ins(addiu('a0','s3',8)); a.ins(addiu('a1','zero',46)); a.ins(jal(STRRCHR)); a.ins(nop()); a.branch('beq','v0','zero','scan'); a.ins(nop()); a.ins(addiu('s5','v0',1)); a.ins(addu('a0','s5','zero')); a.ins(jal(UPPER_EXT)); a.ins(nop()); a.ins(addu('a0','s5','zero')); a.ins(jal(EXT_CLASSIFY)); a.ins(nop())
 a.ins(addiu('t0','zero',cfg['wrapper'])); a.branch('beq','v0','t0','ext_ok'); a.ins(nop()); lo,hi=cfg['native']; a.ins(addiu('t0','v0',-lo)); a.ins(sltiu('t1','t0',hi-lo+1)); a.branch('beq','t1','zero','scan'); a.ins(nop()); a.label('ext_ok')
 scratch(a,'s5',CAT0); a.ins(lw('s6',0,'s5')); a.ins(sll('t0','s6',2)); a.ins(addiu('t0','t0',4)); a.ins(addu('s7','s5','t0')); a.ins(sw('zero',84,'sp'))
 a.label('existing'); a.ins(lw('t0',84,'sp')); a.branch('beq','t0','s6','missing'); a.ins(nop()); a.ins(sll('t1','t0',2)); a.ins(addiu('t1','t1',4)); a.ins(addu('t1','s5','t1')); a.ins(lw('t2',0,'t1')); a.ins(addu('t2','s7','t2')); a.ins(addu('a0','s4','zero')); a.ins(addu('a1','t2','zero')); a.ins(jal(STRCMP)); a.ins(nop()); a.branch('beq','v0','zero','scan'); a.ins(nop()); a.ins(lw('t0',84,'sp')); a.ins(addiu('t0','t0',1)); a.ins(sw('t0',84,'sp')); a.branch('beq','zero','zero','existing'); a.ins(nop())
 a.label('missing'); a.ins(addiu('t0','zero',MAX_CANDS)); a.branch('beq','s2','t0','scan_overflow'); a.ins(nop()); a.ins(addiu('s2','s2',1)); a.branch('beq','zero','zero','scan'); a.ins(nop())
 a.label('scan_overflow'); a.ins(addu('a0','s1','zero')); a.ins(jal(DIR_CLOSE)); a.ins(nop()); a.branch('beq','zero','zero','fail'); a.ins(nop())
 a.label('scan_done'); a.ins(addu('a0','s1','zero')); a.ins(jal(DIR_CLOSE)); a.ins(nop()); a.ins(lw('t0',64,'sp')); a.ins(sw('t0',-3236,'gp')); a.loadlabel('t0','cand_count'); a.ins(sw('s2',0,'t0')); a.branch('beq','s2','zero','nochange'); a.ins(nop())
 # Build outputs. build_slot is emitted later but label references are valid.
 for so,ss,do,k,os in [(CAT0,72,OUT0,0,88),(CAT1,76,OUT1,1,92),(CAT2,80,OUT2,1,96)]:
  scratch(a,'a0',so); a.ins(lw('a1',ss,'sp')); scratch(a,'a2',do); a.ins(addiu('a3','zero',k)); a.loadlabel('t9','build_slot'); a.ins(jalr('ra','t9')); a.ins(nop()); a.branch('beq','v0','zero','fail'); a.ins(nop()); a.ins(sw('v0',os,'sp'))
 # Write outputs.
 for oo,ni,os in [(OUT0,0,88),(OUT1,1,92),(OUT2,2,96)]:
  a.loadaddr('a0',PATHBUF); a.loadaddr('a1',PATHFMT); a.loadaddr('a2',ROOT); a.loadaddr('t0',cfg['names']); a.ins(lw('a3',ni*4,'t0')); a.ins(jal(SPRINTF)); a.ins(nop()); a.loadaddr('a0',PATHBUF); a.loadaddr('a1',MODE_WB); a.ins(jal(FOPEN)); a.ins(nop()); a.branch('beq','v0','zero','fail'); a.ins(nop()); a.ins(addu('s1','v0','zero')); scratch(a,'a0',oo); a.ins(addiu('a1','zero',1)); a.ins(lw('a2',os,'sp')); a.ins(addu('a3','s1','zero')); a.ins(jal(FWRITE)); a.ins(nop()); a.ins(addu('s2','v0','zero')); a.ins(addu('a0','s1','zero')); a.ins(jal(FCLOSE)); a.ins(nop()); a.ins(lw('t0',os,'sp')); a.branch('bne','s2','t0','fail'); a.ins(nop())
 # Preserve exact Test08 post-write call even though later archaeology corrected its semantic label.
 a.ins(jal(TEST08_POST_WRITE_WRAP)); a.ins(nop()); a.loadaddr('t0',cfg['count']); a.ins(sw('zero',0,'t0')); a.ins(addiu('v0','zero',1)); a.branch('beq','zero','zero','ret'); a.ins(nop())
 a.label('nochange'); a.ins(addu('v0','zero','zero')); a.branch('beq','zero','zero','ret'); a.ins(nop())
 a.label('fail'); a.ins(lw('t0',64,'sp')); a.ins(sw('t0',-3236,'gp')); a.ins(addiu('v0','zero',-1))
 a.label('ret')
 for i,r in reversed(list(enumerate(saved))): a.ins(lw(r,16+i*4,'sp'))
 a.ins(addiu('sp','sp',F)); a.ins(jr('ra')); a.ins(nop())
 build_slot(a)
 while a.pc%4: a.data(b'\0')
 a.label('cand_base'); a.data(struct.pack('<I',0)); a.label('cand_count'); a.data(struct.pack('<I',0)); a.label('dirfmt'); a.data(b'%s/'+cfg['folder']+b'\0')
 blob=a.emit(); assert len(blob)<=OUT_SIZE,(system,len(blob)); out=blob+b'\0'*(OUT_SIZE-len(blob))
 if EXPECTED_SHA[system] is not None: assert sha(out)==EXPECTED_SHA[system]
 return out,len(blob)

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--outdir',type=Path,required=True); args=ap.parse_args(); args.outdir.mkdir(parents=True,exist_ok=True)
 for s in SYSTEMS:
  b,used=build(s); p=args.outdir/(s+'-catalog-saf.xgc'); p.write_bytes(b); print(s,'used',used,'size',len(b),'sha256',sha(b))
if __name__=='__main__': main()
