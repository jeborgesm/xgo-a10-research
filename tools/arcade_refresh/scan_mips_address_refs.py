#!/usr/bin/env python3
"""Find candidate MIPS32 references to known runtime addresses in a raw helper.

This is an audit tool: it reports LUI + ADDIU/ORI address constructions and
absolute words. It does not patch anything.
"""
from __future__ import annotations
import struct,sys,pathlib

def sx16(x): return x-0x10000 if x&0x8000 else x

def scan(buf:bytes, targets:dict[str,int]):
    words=[struct.unpack_from("<I",buf,i)[0] for i in range(0,len(buf)-3,4)]
    for i,w in enumerate(words):
        op=w>>26
        if op!=0x0f: continue
        rt=(w>>16)&31; hi=w&0xffff
        # Search a small forward window because compilers may schedule an
        # independent instruction between high/low halves.
        for j in range(i+1,min(i+6,len(words))):
            q=words[j]; qop=q>>26
            rs=(q>>21)&31; qrt=(q>>16)&31; imm=q&0xffff
            if rs!=rt or qrt!=rt or qop not in (0x09,0x0d): continue
            if qop==0x09: addr=((hi<<16)+sx16(imm))&0xffffffff
            else: addr=((hi<<16)|imm)&0xffffffff
            for name,target in targets.items():
                if addr==target:
                    yield name,i*4,j*4,"addiu" if qop==0x09 else "ori",w,q

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: scan_mips_address_refs.py FILE")
    b=pathlib.Path(sys.argv[1]).read_bytes()
    targets={
      "slot0":0x870009E4,
      "slot1":0x87000A02,
      "slot2":0x87000A20,
      "root":0x87000A3E,
      "gba_count_cache":0x80D28974,
    }
    hits=list(scan(b,targets))
    for h in hits:
        name,a,b2,kind,w,q=h
        print(f"{name}: hi@+0x{a:04X} lo@+0x{b2:04X} {kind} words {w:08X} {q:08X}")
    missing=set(targets)-{h[0] for h in hits}
    if missing:
        print("UNRESOLVED:",", ".join(sorted(missing)))
        raise SystemExit(2)

if __name__=="__main__": main()
