#!/usr/bin/env python3
"""Build XGO Game-List Test07: real SFC discovery + stable-merge Refresh.

Input is the exact hardware-confirmed Test06b golden ZIP. The proven Test06b
User Menu/UI/status resources are carried forward byte-for-byte. The firmware
cave is replaced with a real /SFC directory scanner + synchronized stable
append, and Resources/refresh.bin is deliberately omitted from the result.

Test07 is intentionally SFC-only and non-transactional. Use only on the
project's disposable clone until the scanner is hardware-confirmed and the
backup/transaction-marker layer is added.
"""
from __future__ import annotations
import argparse, hashlib, struct, zipfile
from pathlib import Path

TEST06B_ZIP_SHA = "2d859b3ca3f0644a461c197fcfe0b58f2650c26bc6a7c8d28a189da196aa1042"
TEST06B_FW_SHA = "5d15cbe1cef380b3517cbd64727526e1b837df5160ba5275ccde6fec01324f4e"
TEST06B_BLOB_SHA = "31590cfb05e4b02536ae288218108b066f9bf0b3d836117f2fb873d830b591bc"
TEST06B_BLOB_LEN = 1370
ORIGINAL = {
    "urefs.tax": ("ba65a0e993772dc7654449f10402be7536f7d8c7fca768c2db0174fc4b863dc0", 26993),
    "adsnt.nec": ("ffc96b0a4efc8177766ef7dafeb519a761bdfff2552d3cb8dbab2be465a7231c", 21082),
    "xvb6c.bvs": ("0a83d27343dd894802d64c8fbc68d8d9a6181d70446a443b9e9209e69a11bb24", 10290),
}
WRAPPER_SHA = "f600c45d37a77d9af80ecb1ad136e1dbcfbb7e22fd9afc91531f82cfd2fb03b1"

BASE=0x80000000
POLY=0x04C11DB7
CAVE=0x807DAB98
CAVE_LIMIT=0x807DBBA0
DISPATCH=0x80359EA8
MENU_REDRAW=0x80359ABC
STOCK_TV=0x80359EB0
STOCK_OTHER=0x80356BFC
POST_TV_HOOK=0x80359BA8
POST_TV_PAL_A_HOOK=0x8035ACB8
POST_TV_PAL_B_HOOK=0x8035ACF0
POST_TV_ORIGINAL=0x80356C04

SPRINTF=0x802946D8
MEMCPY=0x8029496C
STRCPY=0x80294DAC
STRCMP=0x80294DEC
STRLEN=0x80294E30
STRRCHR=0x801B0E38
UPPER_EXT=0x803526FC
EXT_CLASSIFY=0x80360A08
FOPEN=0x802B3524
FREAD=0x802B3698
FWRITE=0x802B42AC
FCLOSE=0x802B2F40
DIR_OPEN=0x807D40C4
DIR_NEXT=0x807D4124
DIR_CLOSE=0x807D41F4
FS_SYNC_WRAP=0x807D40A8
PATHBUF=0x8109F65C
ROOT=0x8109F25C
PATHFMT=0x809A33DC
MODE_RB=0x809A6687
MODE_WB=0x809A3404
SFC_NAMES=0x80A3C344
COUNT_SFC=0x80D28954
TEXT_DRAW=0x803528A4
OS_GET_TICK=0x8030FEC8
STATUS_MS=3000

# Scratch layout, based on the same stock arena already used by Test06b.
CAT0=0x00000
CAT1=0x10000
CAT2=0x20000
OUT0=0x30000
OUT1=0x40000
OUT2=0x50000
ENTRY=0x60000
CANDS=0x61000
CAND_REC=0x240              # 576 bytes, >= stock 0x226-byte filename
MAX_CANDS=64

R={'zero':0,'at':1,'v0':2,'v1':3,'a0':4,'a1':5,'a2':6,'a3':7,'t0':8,'t1':9,'t2':10,'t3':11,'t4':12,'t5':13,'t6':14,'t7':15,'s0':16,'s1':17,'s2':18,'s3':19,'s4':20,'s5':21,'s6':22,'s7':23,'t8':24,'t9':25,'k0':26,'k1':27,'gp':28,'sp':29,'fp':30,'ra':31}
def sha(b): return hashlib.sha256(b).hexdigest()
def rtype(rs,rt,rd,sh,fn): return (R[rs]<<21)|(R[rt]<<16)|(R[rd]<<11)|(sh<<6)|fn
def iop(op,rs,rt,imm): return (op<<26)|(R[rs]<<21)|(R[rt]<<16)|(imm&0xffff)
def jop(op,addr): return (op<<26)|((addr>>2)&0x03ffffff)
def addiu(rt,rs,imm): return iop(9,rs,rt,imm)
def lui(rt,imm): return iop(15,'zero',rt,imm)
def ori(rt,rs,imm): return iop(13,rs,rt,imm)
def lw(rt,off,rs): return iop(35,rs,rt,off)
def sw(rt,off,rs): return iop(43,rs,rt,off)
def lbu(rt,off,rs): return iop(36,rs,rt,off)
def sb(rt,off,rs): return iop(40,rs,rt,off)
def beq(rs,rt,off): return iop(4,rs,rt,off)
def bne(rs,rt,off): return iop(5,rs,rt,off)
def sltiu(rt,rs,imm): return iop(11,rs,rt,imm)
def addu(rd,rs,rt): return rtype(rs,rt,rd,0,0x21)
def subu(rd,rs,rt): return rtype(rs,rt,rd,0,0x23)
def sltu(rd,rs,rt): return rtype(rs,rt,rd,0,0x2b)
def mfhi(rd): return rtype('zero','zero',rd,0,0x10)
def mflo(rd): return rtype('zero','zero',rd,0,0x12)
def mthi(rs): return rtype(rs,'zero','zero',0,0x11)
def mtlo(rs): return rtype(rs,'zero','zero',0,0x13)
def jal(addr): return jop(3,addr)
def jalr(rd,rs): return rtype(rs,'zero',rd,0,9)
def jr(rs): return rtype(rs,'zero','zero',0,8)
def sll(rd,rt,sh): return rtype('zero',rt,rd,sh,0)
def j(addr): return jop(2,addr)
def nop(): return 0
def bltz(rs,off): return (1<<26)|(R[rs]<<21)|(0<<16)|(off&0xffff)

def split_addr(addr):
    lo=addr&0xffff; hi=(addr>>16)&0xffff
    if lo&0x8000: hi=(hi+1)&0xffff
    return hi,(lo-0x10000 if lo&0x8000 else lo)

class Asm:
    def __init__(self,base): self.base=base; self.items=[]; self.labels={}
    def size(self): return sum(8 if t=='la' else 4 if t in ('i','b','bltz') else len(v) for t,v in self.items)
    @property
    def pc(self): return self.base+self.size()
    def label(self,n): self.labels[n]=self.pc
    def ins(self,w): self.items.append(('i',w))
    def branch(self,k,rs,rt,label): self.items.append(('b',(k,rs,rt,label)))
    def branch_bltz(self,rs,label): self.items.append(('bltz',(rs,label)))
    def loadaddr(self,r,addr):
        hi,lo=split_addr(addr); self.ins(lui(r,hi)); self.ins(addiu(r,r,lo))
    def loadlabel(self,r,label): self.items.append(('la',(r,label)))
    def data(self,b): self.items.append(('d',bytes(b)))
    def emit(self):
        out=bytearray(); pc=self.base
        for typ,val in self.items:
            if typ=='i': out += struct.pack('<I',val); pc+=4
            elif typ=='b':
                kind,rs,rt,label=val; d=self.labels[label]-(pc+4); assert d%4==0
                off=d//4; assert -32768<=off<=32767
                out += struct.pack('<I',beq(rs,rt,off) if kind=='beq' else bne(rs,rt,off)); pc+=4
            elif typ=='bltz':
                rs,label=val; d=self.labels[label]-(pc+4); assert d%4==0
                off=d//4; assert -32768<=off<=32767
                out += struct.pack('<I',bltz(rs,off)); pc+=4
            elif typ=='la':
                reg,label=val; hi,lo=split_addr(self.labels[label])
                out += struct.pack('<II',lui(reg,hi),addiu(reg,reg,lo)); pc+=8
            else: out += val; pc+=len(val)
        return bytes(out)

def scratch_addr(a, reg, off, tmp='t9'):
    high=off & ~0xffff; low=off-high
    if high:
        a.ins(lui(tmp,high>>16)); a.ins(addu(reg,'s0',tmp))
    else:
        a.ins(addu(reg,'s0','zero'))
    if low: a.ins(addiu(reg,reg,low))

def candidate_ptr(a, dst, index_reg):
    # Outer scanner: CANDS + i*0x240 from refresh scratch base s0.
    scratch_addr(a,'t8',CANDS,'t7')
    a.ins(sll('t6',index_reg,9)); a.ins(sll('t5',index_reg,6)); a.ins(addu('t6','t6','t5'))
    a.ins(addu(dst,'t8','t6'))

def candidate_ptr_shared(a, dst, index_reg):
    # build_slot has repurposed s0 for its source catalog; use saved candidate base.
    a.loadlabel('t8','cand_base'); a.ins(lw('t8',0,'t8'))
    a.ins(sll('t6',index_reg,9)); a.ins(sll('t5',index_reg,6)); a.ins(addu('t6','t6','t5'))
    a.ins(addu(dst,'t8','t6'))

def build_blob():
    a=Asm(CAVE)
    # Rows 0/1 are handled by stock code before this Test06b dispatch hook.
    a.ins(addiu('t0','zero',2)); a.branch('beq','v1','t0','row2'); a.ins(nop())
    a.ins(addiu('t0','zero',3)); a.branch('beq','v1','t0','refresh'); a.ins(nop())
    a.ins(j(STOCK_OTHER)); a.ins(nop())
    a.label('row2'); a.ins(j(STOCK_TV)); a.ins(nop())

    # build_slot(a0=src, a1=src_size, a2=dst, a3=0 full filename / 1 basename)
    # Returns final byte size in v0, or zero on structural/size failure.
    a.label('build_slot')
    BSF=112
    a.ins(addiu('sp','sp',-BSF))
    saved=['s0','s1','s2','s3','s4','s5','s6','s7','ra']
    for i,r in enumerate(saved): a.ins(sw(r,16+i*4,'sp'))
    a.ins(addu('s0','a0','zero')); a.ins(addu('s1','a1','zero')); a.ins(addu('s2','a2','zero')); a.ins(addu('s3','a3','zero'))
    a.ins(lw('s4',0,'s0')); a.ins(sll('s5','s4',2)); a.ins(addiu('s5','s5',4))
    a.ins(sltu('t0','s1','s5')); a.branch('bne','t0','zero','bs_fail'); a.ins(nop())
    a.ins(subu('s6','s1','s5'))
    a.loadlabel('t0','cand_count'); a.ins(lw('s7',0,'t0'))
    a.ins(addu('t0','s4','s7')); a.ins(sw('t0',0,'s2'))
    # Preserve source size and old blob length across libc calls.
    a.ins(sw('s1',60,'sp')); a.ins(sw('s6',64,'sp'))

    # Copy old offset table byte-for-byte.
    a.ins(addiu('a0','s2',4)); a.ins(addiu('a1','s0',4)); a.ins(sll('a2','s4',2)); a.ins(jal(MEMCPY)); a.ins(nop())

    # Append M new offsets, relative to the future string blob.
    a.ins(sw('zero',68,'sp')); a.ins(lw('t0',64,'sp')); a.ins(sw('t0',72,'sp'))
    a.label('bs_off_loop')
    a.ins(lw('t0',68,'sp')); a.branch('beq','t0','s7','bs_offsets_done'); a.ins(nop())
    a.ins(sll('t1','s4',2)); a.ins(sll('t2','t0',2)); a.ins(addu('t1','t1','t2')); a.ins(addiu('t1','t1',4)); a.ins(addu('t1','s2','t1'))
    a.ins(lw('t2',72,'sp')); a.ins(sw('t2',0,'t1'))
    candidate_ptr_shared(a,'t4','t0'); a.ins(sw('t4',76,'sp'))
    a.branch('beq','s3','zero','bs_off_full_len'); a.ins(nop())
    a.ins(addu('a0','t4','zero')); a.ins(addiu('a1','zero',46)); a.ins(jal(STRRCHR)); a.ins(nop())
    a.ins(lw('t4',76,'sp')); a.branch('beq','v0','zero','bs_off_full_len_reload'); a.ins(nop())
    a.ins(subu('t3','v0','t4')); a.branch('beq','zero','zero','bs_off_len_ready'); a.ins(nop())
    a.label('bs_off_full_len_reload'); a.ins(lw('t4',76,'sp'))
    a.label('bs_off_full_len')
    a.ins(addu('a0','t4','zero')); a.ins(jal(STRLEN)); a.ins(nop()); a.ins(addu('t3','v0','zero'))
    a.label('bs_off_len_ready')
    a.ins(lw('t2',72,'sp')); a.ins(addiu('t3','t3',1)); a.ins(addu('t2','t2','t3')); a.ins(sw('t2',72,'sp'))
    a.ins(lw('t0',68,'sp')); a.ins(addiu('t0','t0',1)); a.ins(sw('t0',68,'sp'))
    a.branch('beq','zero','zero','bs_off_loop'); a.ins(nop())

    a.label('bs_offsets_done')
    # Compute source/destination blob starts and copy old blob exactly.
    a.ins(addu('t0','s4','s7')); a.ins(sll('t0','t0',2)); a.ins(addiu('t0','t0',4)); a.ins(addu('t1','s2','t0')); a.ins(sw('t1',80,'sp'))
    a.ins(addu('t2','s0','s5')); a.ins(lw('t3',64,'sp'))
    a.ins(addu('a0','t1','zero')); a.ins(addu('a1','t2','zero')); a.ins(addu('a2','t3','zero')); a.ins(jal(MEMCPY)); a.ins(nop())
    a.ins(lw('t1',80,'sp')); a.ins(lw('t3',64,'sp')); a.ins(addu('t1','t1','t3')); a.ins(sw('t1',84,'sp'))
    a.ins(sw('zero',68,'sp'))

    # Append candidate strings.
    a.label('bs_str_loop')
    a.ins(lw('t0',68,'sp')); a.branch('beq','t0','s7','bs_done'); a.ins(nop())
    candidate_ptr_shared(a,'t4','t0'); a.ins(sw('t4',76,'sp'))
    a.branch('beq','s3','zero','bs_str_full_len'); a.ins(nop())
    a.ins(addu('a0','t4','zero')); a.ins(addiu('a1','zero',46)); a.ins(jal(STRRCHR)); a.ins(nop())
    a.ins(lw('t4',76,'sp')); a.branch('beq','v0','zero','bs_str_full_len_reload'); a.ins(nop())
    a.ins(subu('t3','v0','t4')); a.branch('beq','zero','zero','bs_str_len_ready'); a.ins(nop())
    a.label('bs_str_full_len_reload'); a.ins(lw('t4',76,'sp'))
    a.label('bs_str_full_len')
    a.ins(addu('a0','t4','zero')); a.ins(jal(STRLEN)); a.ins(nop()); a.ins(addu('t3','v0','zero'))
    a.label('bs_str_len_ready')
    a.ins(sw('t3',88,'sp')); a.ins(lw('t1',84,'sp')); a.ins(lw('t4',76,'sp'))
    a.ins(addu('a0','t1','zero')); a.ins(addu('a1','t4','zero')); a.ins(addu('a2','t3','zero')); a.ins(jal(MEMCPY)); a.ins(nop())
    a.ins(lw('t1',84,'sp')); a.ins(lw('t3',88,'sp')); a.ins(addu('t1','t1','t3')); a.ins(sb('zero',0,'t1')); a.ins(addiu('t1','t1',1)); a.ins(sw('t1',84,'sp'))
    a.ins(lw('t0',68,'sp')); a.ins(addiu('t0','t0',1)); a.ins(sw('t0',68,'sp'))
    a.branch('beq','zero','zero','bs_str_loop'); a.ins(nop())

    a.label('bs_done')
    a.ins(lw('t0',84,'sp')); a.ins(subu('v0','t0','s2'))
    a.ins(lui('t1',1)); a.ins(sltu('t2','v0','t1')); a.branch('bne','t2','zero','bs_return'); a.ins(nop())
    a.label('bs_fail'); a.ins(addu('v0','zero','zero'))
    a.label('bs_return')
    for i,r in reversed(list(enumerate(saved))): a.ins(lw(r,16+i*4,'sp'))
    a.ins(addiu('sp','sp',BSF)); a.ins(jr('ra')); a.ins(nop())

    # Real Refresh action.
    a.label('refresh')
    FRAME=192
    save_regs=['v0','v1','a0','a1','a2','a3','t0','t1','t2','t3','t4','t5','t6','t7','s0','s1','s2','s3','s4','s5','s6','s7','t8','t9','gp','fp','ra']
    a.ins(addiu('sp','sp',-FRAME))
    for idx,reg in enumerate(save_regs): a.ins(sw(reg,16+idx*4,'sp'))
    a.ins(mfhi('t0')); a.ins(sw('t0',124,'sp')); a.ins(mflo('t0')); a.ins(sw('t0',128,'sp'))
    a.ins(lw('t0',-3236,'gp')); a.ins(sw('t0',132,'sp'))  # preserve classifier system-mask global

    # Same proven scratch arena as Test06b.
    a.ins(lw('s0',-3228,'gp')); a.ins(lui('t0',0x0210)); a.ins(addu('s0','s0','t0'))
    scratch_addr(a,'t0',CANDS); a.loadlabel('t1','cand_base'); a.ins(sw('t0',0,'t1'))

    # Read synchronized SFC triplet dynamically (up to 65535 bytes each).
    cat_specs=[(CAT0,0,140),(CAT1,1,144),(CAT2,2,148)]
    for off,name_i,size_sp in cat_specs:
        a.loadaddr('a0',PATHBUF); a.loadaddr('a1',PATHFMT); a.loadaddr('a2',ROOT); a.loadaddr('t0',SFC_NAMES); a.ins(lw('a3',name_i*4,'t0')); a.ins(jal(SPRINTF)); a.ins(nop())
        a.loadaddr('a0',PATHBUF); a.loadaddr('a1',MODE_RB); a.ins(jal(FOPEN)); a.ins(nop()); a.branch('beq','v0','zero','fail'); a.ins(nop()); a.ins(addu('s1','v0','zero'))
        scratch_addr(a,'a0',off); a.ins(addiu('a1','zero',1)); a.ins(ori('a2','zero',0xffff)); a.ins(addu('a3','s1','zero')); a.ins(jal(FREAD)); a.ins(nop()); a.ins(addu('s2','v0','zero'))
        a.ins(addu('a0','s1','zero')); a.ins(jal(FCLOSE)); a.ins(nop()); a.ins(sw('s2',size_sp,'sp'))
        a.branch('beq','s2','zero','fail'); a.ins(nop())

    # Triplet must already be synchronized before mutation.
    scratch_addr(a,'t0',CAT0); scratch_addr(a,'t1',CAT1); scratch_addr(a,'t2',CAT2)
    a.ins(lw('t3',0,'t0')); a.ins(lw('t4',0,'t1')); a.ins(lw('t5',0,'t2'))
    a.branch('bne','t3','t4','fail'); a.ins(nop()); a.branch('bne','t3','t5','fail'); a.ins(nop()); a.branch('beq','t3','zero','fail'); a.ins(nop())

    # Open the real /SFC directory through the stock frontend wrapper.
    a.loadaddr('a0',PATHBUF); a.loadlabel('a1','sfc_pathfmt'); a.loadaddr('a2',ROOT); a.ins(jal(SPRINTF)); a.ins(nop())
    a.loadaddr('a0',PATHBUF); a.ins(jal(DIR_OPEN)); a.ins(nop()); a.branch('beq','v0','zero','fail'); a.ins(nop()); a.ins(addu('s1','v0','zero'))
    a.ins(addu('s2','zero','zero')); scratch_addr(a,'s3',ENTRY)

    a.label('scan_loop')
    a.ins(addu('a0','s1','zero')); a.ins(addu('a1','s3','zero')); a.ins(jal(DIR_NEXT)); a.ins(nop()); a.branch_bltz('v0','scan_done')
    a.ins(lbu('t0',0,'s3')); a.branch('bne','t0','zero','scan_loop'); a.ins(nop())

    # Copy the original filename before stock uppercase/classification mutates the extension.
    candidate_ptr(a,'s4','s2'); a.ins(addiu('a1','s3',8)); a.ins(addu('a0','s4','zero')); a.ins(jal(STRCPY)); a.ins(nop())
    a.ins(addiu('a0','s3',8)); a.ins(addiu('a1','zero',46)); a.ins(jal(STRRCHR)); a.ins(nop()); a.branch('beq','v0','zero','scan_loop'); a.ins(nop())
    a.ins(addiu('s5','v0',1)); a.ins(addu('a0','s5','zero')); a.ins(jal(UPPER_EXT)); a.ins(nop()); a.ins(addu('a0','s5','zero')); a.ins(jal(EXT_CLASSIFY)); a.ins(nop())

    # Accept ZSF (classifier return 4) or native SFC-family returns 8..15.
    a.ins(addiu('t0','zero',4)); a.branch('beq','v0','t0','scan_ext_ok'); a.ins(nop())
    a.ins(addiu('t0','v0',-8)); a.ins(sltiu('t1','t0',8)); a.branch('beq','t1','zero','scan_loop'); a.ins(nop())
    a.label('scan_ext_ok')

    # Stable merge lookup: compare original filename against every slot-0 entry.
    scratch_addr(a,'s5',CAT0); a.ins(lw('s6',0,'s5')); a.ins(sll('t0','s6',2)); a.ins(addiu('t0','t0',4)); a.ins(addu('s7','s5','t0'))
    a.ins(sw('zero',152,'sp'))
    a.label('existing_loop')
    a.ins(lw('t0',152,'sp')); a.branch('beq','t0','s6','not_existing'); a.ins(nop())
    a.ins(sll('t1','t0',2)); a.ins(addiu('t1','t1',4)); a.ins(addu('t1','s5','t1')); a.ins(lw('t2',0,'t1')); a.ins(addu('t2','s7','t2'))
    a.ins(addu('a0','s4','zero')); a.ins(addu('a1','t2','zero')); a.ins(jal(STRCMP)); a.ins(nop()); a.branch('beq','v0','zero','scan_loop'); a.ins(nop())
    a.ins(lw('t0',152,'sp')); a.ins(addiu('t0','t0',1)); a.ins(sw('t0',152,"sp")); a.branch('beq','zero','zero','existing_loop'); a.ins(nop())

    a.label('not_existing')
    a.ins(addiu('t0','zero',MAX_CANDS)); a.branch('beq','s2','t0','scan_overflow'); a.ins(nop())
    a.ins(addiu('s2','s2',1)); a.branch('beq','zero','zero','scan_loop'); a.ins(nop())

    a.label('scan_overflow')
    a.ins(addu('a0','s1','zero')); a.ins(jal(DIR_CLOSE)); a.ins(nop()); a.branch('beq','zero','zero','fail'); a.ins(nop())

    a.label('scan_done')
    a.ins(addu('a0','s1','zero')); a.ins(jal(DIR_CLOSE)); a.ins(nop())
    # Undo the extension classifier's global OR side effect before any menu/game state resumes.
    a.ins(lw('t0',132,'sp')); a.ins(sw('t0',-3236,'gp'))
    a.loadlabel('t0','cand_count'); a.ins(sw('s2',0,'t0')); a.branch('beq','s2','zero','nochange'); a.ins(nop())

    # Build all three complete outputs in RAM before touching canonical files.
    build_specs=[(CAT0,140,OUT0,0,156),(CAT1,144,OUT1,1,160),(CAT2,148,OUT2,1,164)]
    for src_off,size_sp,dst_off,kind,out_size_sp in build_specs:
        scratch_addr(a,'a0',src_off); a.ins(lw('a1',size_sp,'sp')); scratch_addr(a,'a2',dst_off); a.ins(addiu('a3','zero',kind)); a.loadlabel('t9','build_slot'); a.ins(jalr('ra','t9')); a.ins(nop())
        a.branch('beq','v0','zero','fail'); a.ins(nop()); a.ins(sw('v0',out_size_sp,'sp'))

    # Write synchronized triplet. Still deliberately non-transactional in Test07.
    write_specs=[(OUT0,0,156),(OUT1,1,160),(OUT2,2,164)]
    for out_off,name_i,size_sp in write_specs:
        a.loadaddr('a0',PATHBUF); a.loadaddr('a1',PATHFMT); a.loadaddr('a2',ROOT); a.loadaddr('t0',SFC_NAMES); a.ins(lw('a3',name_i*4,'t0')); a.ins(jal(SPRINTF)); a.ins(nop())
        a.loadaddr('a0',PATHBUF); a.loadaddr('a1',MODE_WB); a.ins(jal(FOPEN)); a.ins(nop()); a.branch('beq','v0','zero','fail'); a.ins(nop()); a.ins(addu('s1','v0','zero'))
        scratch_addr(a,'a0',out_off); a.ins(addiu('a1','zero',1)); a.ins(lw('a2',size_sp,'sp')); a.ins(addu('a3','s1','zero')); a.ins(jal(FWRITE)); a.ins(nop()); a.ins(addu('s2','v0','zero'))
        a.ins(addu('a0','s1','zero')); a.ins(jal(FCLOSE)); a.ins(nop()); a.ins(lw('t0',size_sp,'sp')); a.branch('bne','s2','t0','fail'); a.ins(nop())

    a.ins(jal(FS_SYNC_WRAP)); a.ins(nop()); a.loadaddr('t0',COUNT_SFC); a.ins(sw('zero',0,'t0'))
    a.loadlabel('t0','status'); a.ins(addiu('t1','zero',1)); a.ins(sw('t1',0,'t0')); a.ins(jal(OS_GET_TICK)); a.ins(nop()); a.loadlabel('t0','status_tick'); a.ins(sw('v0',0,'t0'))
    a.branch('beq','zero','zero','restore'); a.ins(nop())

    a.label('nochange')
    a.loadlabel('t0','status'); a.ins(addiu('t1','zero',2)); a.ins(sw('t1',0,'t0')); a.ins(jal(OS_GET_TICK)); a.ins(nop()); a.loadlabel('t0','status_tick'); a.ins(sw('v0',0,'t0'))
    a.branch('beq','zero','zero','restore'); a.ins(nop())

    a.label('fail')
    # Always restore classifier global even when failure occurred before/within scan.
    a.ins(lw('t0',132,"sp")); a.ins(sw('t0',-3236,'gp'))
    a.loadlabel('t0','status'); a.ins(addiu('t1','zero',3)); a.ins(sw('t1',0,'t0')); a.ins(jal(OS_GET_TICK)); a.ins(nop()); a.loadlabel('t0','status_tick'); a.ins(sw('v0',0,'t0'))

    a.label('restore')
    a.ins(lw('t0',124,'sp')); a.ins(mthi('t0')); a.ins(lw('t0',128,'sp')); a.ins(mtlo('t0'))
    for idx,reg in reversed(list(enumerate(save_regs))):
        if reg!='t0': a.ins(lw(reg,16+idx*4,'sp'))
    a.ins(lw('t0',16+save_regs.index('t0')*4,'sp')); a.ins(addiu('sp','sp',FRAME))
    a.ins(addiu('fp','zero',1)); a.ins(addiu('s2','zero',1)); a.ins(j(MENU_REDRAW)); a.ins(nop())

    # Preserve Test06b's stock-font timed status renderer.
    a.label('status_draw')
    status_save=['v0','v1','a0','a1','a2','a3','t0','t1','t2','t3','t4','t5','t6','t7','t8','t9','ra','fp']
    STATUS_FRAME=112
    a.ins(addiu('sp','sp',-STATUS_FRAME))
    for idx,reg in enumerate(status_save): a.ins(sw(reg,16+idx*4,'sp'))
    a.loadlabel('t0','status'); a.ins(lw('t0',0,'t0')); a.branch('beq','t0','zero','status_done'); a.ins(nop())
    a.ins(jal(OS_GET_TICK)); a.ins(nop()); a.loadlabel('t1','status_tick'); a.ins(lw('t1',0,'t1')); a.ins(subu('t2','v0','t1')); a.ins(sltiu('t1','t2',STATUS_MS)); a.branch('bne','t1','zero','status_live'); a.ins(nop())
    a.loadlabel('t1','status'); a.ins(sw('zero',0,'t1')); a.branch('beq','zero','zero','status_done'); a.ins(nop())
    a.label('status_live')
    a.loadlabel('t0','status'); a.ins(lw('t0',0,'t0')); a.ins(addiu('t1','zero',1)); a.branch('beq','t0','t1','status_updated'); a.ins(nop()); a.ins(addiu('t1','zero',2)); a.branch('beq','t0','t1','status_none'); a.ins(nop())
    a.loadlabel('t3','msg_fail'); a.branch('beq','zero','zero','status_call'); a.ins(nop())
    a.label('status_updated'); a.loadlabel('t3','msg_updated'); a.branch('beq','zero','zero','status_call'); a.ins(nop())
    a.label('status_none'); a.loadlabel('t3','msg_none')
    a.label('status_call')
    a.ins(lw('a0',-5136,'gp')); a.ins(addiu('a1','zero',245)); a.ins(addiu('a2','zero',205)); a.ins(addiu('a3','zero',0)); a.ins(sw('s5',16,'sp')); a.ins(lw('t0',-30380,'gp')); a.ins(sw('t0',20,'sp')); a.ins(sw('t3',24,'sp')); a.ins(jal(TEXT_DRAW)); a.ins(addiu('fp','zero',0))
    a.label('status_done')
    for idx,reg in reversed(list(enumerate(status_save))): a.ins(lw(reg,16+idx*4,'sp'))
    a.ins(addiu('sp','sp',STATUS_FRAME)); a.ins(j(POST_TV_ORIGINAL)); a.ins(nop())

    while a.pc%4: a.data(b'\0')
    a.label('cand_base'); a.data(struct.pack('<I',0)); a.label('cand_count'); a.data(struct.pack('<I',0))
    a.label('status'); a.data(struct.pack('<I',0)); a.label('status_tick'); a.data(struct.pack('<I',0))
    a.label('sfc_pathfmt'); a.data(b'%s/SFC\0')
    a.label('msg_updated'); a.data(b'Games Updated\0'); a.label('msg_none'); a.data(b'No New Games\0'); a.label('msg_fail'); a.data(b'Refresh Failed\0')
    blob=a.emit(); assert CAVE+len(blob)<=CAVE_LIMIT, (len(blob),hex(CAVE_LIMIT-CAVE))
    return blob,a.labels['status_draw']

def crc32_mpeg2(data):
    crc=0xffffffff
    for byte in data:
        crc ^= byte<<24
        for _ in range(8): crc=(((crc<<1)^POLY) if crc&0x80000000 else crc<<1)&0xffffffff
    return crc

def zi(name):
    z=zipfile.ZipInfo(name,(2026,9,7,18,55,0)); z.compress_type=zipfile.ZIP_DEFLATED
    z.create_system=3; z.external_attr=0o600<<16; return z

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--test06b-zip',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); args=ap.parse_args()
    raw=args.test06b_zip.read_bytes(); assert sha(raw)==TEST06B_ZIP_SHA
    with zipfile.ZipFile(args.test06b_zip) as z:
        members={n:z.read(n) for n in z.namelist()}
    assert 'Resources/refresh.bin' in members
    assert sha(members['SFC/XGO Import Test.zsf'])==WRAPPER_SHA
    for n,(h,s) in ORIGINAL.items(): assert (sha(members['Resources/'+n]),len(members['Resources/'+n]))==(h,s)
    fw=bytearray(members['bios/bisrv.asd']); assert sha(fw)==TEST06B_FW_SHA
    old=bytes(fw[CAVE-BASE:CAVE-BASE+TEST06B_BLOB_LEN]); assert sha(old)==TEST06B_BLOB_SHA

    blob,status_draw=build_blob()
    fw[CAVE-BASE:CAVE_LIMIT-BASE]=b'\0'*(CAVE_LIMIT-CAVE)
    fw[CAVE-BASE:CAVE-BASE+len(blob)]=blob
    def put(addr,w): struct.pack_into('<I',fw,addr-BASE,w)
    # Dispatch was already Test06b's jump to CAVE; rewrite explicitly and repoint status hooks.
    put(DISPATCH,j(CAVE)); put(POST_TV_HOOK,j(status_draw)); put(POST_TV_PAL_A_HOOK,j(status_draw)); put(POST_TV_PAL_B_HOOK,j(status_draw))
    crc=crc32_mpeg2(fw[0x200:]); struct.pack_into('<I',fw,0x18c,crc)

    readme=f"""XGO GAME-LIST TEST07 — REAL SFC DISCOVERY + STABLE MERGE

PROTECTED INPUT
---------------
Golden Test06b explicit Refresh UI/timed status
ZIP SHA-256      {TEST06B_ZIP_SHA}
firmware SHA-256 {TEST06B_FW_SHA}

WHAT CHANGED
------------
Test07 removes Resources/refresh.bin entirely. Pressing Refresh now:
1. reads the current SFC filename/title/search triplet;
2. scans the real /SFC directory through the stock directory wrappers;
3. accepts ZSF and stock native SFC-family extensions;
4. compares discovered filenames against slot 0;
5. keeps every existing entry/index/order unchanged;
6. appends only missing physical filenames;
7. appends basename fallbacks to slots 1 and 2;
8. builds all three complete outputs in RAM before any canonical write;
9. rewrites the synchronized triplet, fs_syncs, and invalidates only SFC count;
10. reuses the golden Test06b Games Updated / No New Games / Refresh Failed timed status.

The extension classifier's global system-mask side effect is saved/restored.
The golden Test06b UI resources are otherwise carried forward unchanged.

SAFETY BOUNDARY
---------------
This is the first REAL scanner candidate but is still intentionally non-transactional.
Use ONLY on the disposable clone. A power loss or write failure during the canonical
triplet rewrite can still leave the SFC catalogs inconsistent. Transaction-marker
recovery is the next safety layer after discovery/stable-merge hardware proof.

EXPECTED DISPOSABLE-CLONE TEST
------------------------------
Initial state: 929 SFC entries; SFC/XGO Import Test.zsf physically present but absent
from the catalogs.

First Refresh:
- must discover the physical wrapper itself (no refresh.bin exists);
- status: Games Updated;
- SFC becomes 930;
- XGO Import Test appears last and launches normally.

Second Refresh:
- status: No New Games;
- no catalog rewrite expected.

Regression checks:
- existing Favorites/save remain valid;
- Search and Chinese-mode list access remain aligned;
- User Games/Language/TV System unchanged;
- timed status still expires after about three seconds;
- audio OSD / SNES / CPS1 protected behavior unchanged.

Firmware cave: 0x{CAVE:08x}..0x{CAVE_LIMIT:08x}
scanner/status blob bytes: {len(blob)}
scanner/status blob SHA-256: {sha(blob)}
LCFG CRC-32/MPEG-2: 0x{crc:08x}
Candidate firmware SHA-256: {sha(fw)}
""".encode()

    order=[n for n in members if n!='Resources/refresh.bin']
    with zipfile.ZipFile(args.output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for n in order:
            if n=='README-HARDWARE-TEST.txt': z.writestr(zi(n),readme)
            elif n=='bios/bisrv.asd': z.writestr(zi(n),bytes(fw))
            else: z.writestr(zi(n),members[n])
    print('scanner',len(blob),sha(blob)); print('firmware',sha(fw)); print('zip',args.output.stat().st_size,sha(args.output.read_bytes()))

if __name__=='__main__': main()
