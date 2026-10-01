#!/usr/bin/env python3
"""Validate one Arcade import using XACM v1 plus the bounded metadata-only
central-directory parser. This mirrors the intended on-device substrate: no
JSON, zipfile module, or decompression."""
import argparse,struct
FAMILIES=("CPS1","CPS2","IGS","NEOGEO")
EOCD=0x06054B50; CEN=0x02014B50; MAX_TAIL=65557
class FormatError(Exception): pass

def zip_entries(path):
    with open(path,"rb") as f:
        f.seek(0,2); size=f.tell(); n=min(size,MAX_TAIL)
        f.seek(size-n); tail=f.read(n); p=tail.rfind(struct.pack("<I",EOCD))
        if p<0 or p+22>len(tail): raise FormatError("EOCD missing/truncated")
        disk,cd_disk,n_disk,n_total,cd_size,cd_off,comment=struct.unpack_from("<HHHHIIH",tail,p+4)
        if p+22+comment!=len(tail): raise FormatError("EOCD/comment does not terminate archive")
        if disk or cd_disk or n_disk!=n_total: raise FormatError("multidisk ZIP unsupported")
        if n_total==0xffff or cd_size==0xffffffff or cd_off==0xffffffff: raise FormatError("ZIP64 unsupported")
        if cd_off+cd_size>size: raise FormatError("central directory outside file")
        f.seek(cd_off); remaining=cd_size; out=[]
        for _ in range(n_total):
            h=f.read(46); remaining-=46
            if len(h)!=46 or remaining<0 or struct.unpack_from("<I",h)[0]!=CEN: raise FormatError("bad central entry")
            flags=struct.unpack_from("<H",h,8)[0]; crc=struct.unpack_from("<I",h,16)[0]
            csize,usize=struct.unpack_from("<II",h,20); nlen,xlen,clen=struct.unpack_from("<HHH",h,28)
            disk_start=struct.unpack_from("<H",h,34)[0]; local_off=struct.unpack_from("<I",h,42)[0]
            if 0xffffffff in (csize,usize,local_off) or disk_start==0xffff: raise FormatError("ZIP64 entry unsupported")
            if disk_start: raise FormatError("multidisk entry unsupported")
            need=nlen+xlen+clen
            if need>remaining: raise FormatError("central entry exceeds directory")
            name=f.read(nlen); f.seek(xlen+clen,1); remaining-=need
            if flags&1: raise FormatError("encrypted entry unsupported")
            out.append((name.decode("utf-8" if flags&0x800 else "cp437"),usize,crc))
        if remaining: raise FormatError("central directory size/count mismatch")
        return out

def load_xacm(path):
    b=open(path,"rb").read()
    if len(b)<52: raise FormatError("short XACM")
    magic,ver,nfam,ndrv,nrom,nstr,fw=struct.unpack_from("<4sHHIII32s",b,0)
    if magic!=b"XACM" or ver!=1 or nfam!=len(FAMILIES): raise FormatError("unsupported XACM")
    off=52; need=off+nfam*12+ndrv*20+nrom*16+nstr
    if need!=len(b): raise FormatError("XACM size/count mismatch")
    fam=[struct.unpack_from("<III",b,off+i*12) for i in range(nfam)]; off+=nfam*12
    drv=[struct.unpack_from("<IIIIHBB",b,off+i*20) for i in range(ndrv)]; off+=ndrv*20
    rom=[struct.unpack_from("<IIII",b,off+i*16) for i in range(nrom)]; off+=nrom*16
    pool=b[off:]
    def s(o):
        if not o:return None
        if o>=len(pool):raise FormatError("string offset outside pool")
        e=pool.find(b"\0",o)
        if e<0:raise FormatError("unterminated manifest string")
        return pool[o:e].decode("ascii")
    return fw,fam,drv,rom,s

def validate(xacm,family,stem,zpath):
    fw,fam,drv,rom,s=load_xacm(xacm); fi=FAMILIES.index(family)
    _,first,count=fam[fi]
    if first+count>len(drv): raise FormatError("family range outside driver table")
    d=next((r for r in drv[first:first+count] if s(r[0])==stem),None)
    if d is None:return "UNSUPPORTED",[],[]
    ents=[(n.rsplit("/",1)[-1].lower(),sz,crc) for n,sz,crc in zip_entries(zpath) if not n.endswith("/")]
    missing=[]; size_bad=[]; _,_,_,first_rom,rom_count,dfi,res=d
    if dfi!=fi or res or first_rom+rom_count>len(rom):raise FormatError("bad driver record")
    for no,size,crc,typ in rom[first_rom:first_rom+rom_count]:
        name=s(no) or ""
        if not typ or not size or not crc or typ&(1<<27):continue
        hit=next((e for e in ents if e[2]==crc),None)
        if hit:
            if hit[1]!=size:size_bad.append((name,hit[1],size))
            continue
        if any(e[0]==name.lower() for e in ents):continue
        missing.append(name)
    return ("COMPATIBLE" if not missing and not size_bad else "INCOMPATIBLE"),missing,size_bad

def main():
    ap=argparse.ArgumentParser();ap.add_argument("xacm");ap.add_argument("family",choices=FAMILIES);ap.add_argument("stem");ap.add_argument("zip");a=ap.parse_args()
    try: status,missing,size_bad=validate(a.xacm,a.family,a.stem,a.zip)
    except FormatError as e: print("VALIDATOR_ERROR:",e);raise SystemExit(3)
    print(status)
    for x in missing:print(" missing",x)
    for x in size_bad:print(" size",*x)
    raise SystemExit({"COMPATIBLE":0,"INCOMPATIBLE":1,"UNSUPPORTED":2}[status])
if __name__=="__main__":main()
