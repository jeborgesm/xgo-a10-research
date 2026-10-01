#!/usr/bin/env python3
"""Bounded metadata-only ZIP central-directory reader for Arcade validator tests.

Reference implementation for the external-helper parser. It intentionally does
not decompress file data.
"""
import argparse,struct

EOCD=0x06054B50
CEN=0x02014B50
MAX_TAIL=65557

class ZipFormatError(Exception): pass

def entries(path):
    with open(path,"rb") as f:
        f.seek(0,2); size=f.tell()
        n=min(size,MAX_TAIL); f.seek(size-n); tail=f.read(n)
        sig=struct.pack("<I",EOCD); p=tail.rfind(sig)
        if p<0 or p+22>len(tail): raise ZipFormatError("EOCD missing/truncated")
        disk,cd_disk,n_disk,n_total,cd_size,cd_off,comment=struct.unpack_from("<HHHHIIH",tail,p+4)
        if p+22+comment != len(tail): raise ZipFormatError("EOCD/comment does not terminate archive")
        if disk or cd_disk or n_disk!=n_total: raise ZipFormatError("multidisk ZIP unsupported")
        if n_total==0xffff or cd_size==0xffffffff or cd_off==0xffffffff:
            raise ZipFormatError("ZIP64 unsupported")
        if cd_off+cd_size>size: raise ZipFormatError("central directory outside file")
        f.seek(cd_off); remaining=cd_size
        out=[]
        for _ in range(n_total):
            h=f.read(46); remaining-=46
            if len(h)!=46 or remaining<0 or struct.unpack_from("<I",h)[0]!=CEN:
                raise ZipFormatError("bad central entry")
            flags=struct.unpack_from("<H",h,8)[0]
            crc=struct.unpack_from("<I",h,16)[0]
            csize,usize=struct.unpack_from("<II",h,20)
            nlen,xlen,clen=struct.unpack_from("<HHH",h,28)
            disk_start=struct.unpack_from("<H",h,34)[0]
            local_off=struct.unpack_from("<I",h,42)[0]
            if 0xffffffff in (csize,usize,local_off) or disk_start==0xffff:
                raise ZipFormatError("ZIP64 entry unsupported")
            if disk_start: raise ZipFormatError("multidisk entry unsupported")
            need=nlen+xlen+clen
            if need>remaining: raise ZipFormatError("central entry exceeds directory")
            name=f.read(nlen); f.seek(xlen+clen,1); remaining-=need
            if flags & 1: raise ZipFormatError("encrypted entry unsupported")
            try: s=name.decode("utf-8" if flags&0x800 else "cp437")
            except UnicodeDecodeError: raise ZipFormatError("invalid filename encoding")
            out.append((s,usize,crc))
        if remaining!=0: raise ZipFormatError("central directory size/count mismatch")
        return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("zip"); a=ap.parse_args()
    es=entries(a.zip)
    print(f"entries={len(es)}")
    for name,size,crc in es: print(f"{crc:08x} {size:10d} {name}")

if __name__=="__main__": main()
