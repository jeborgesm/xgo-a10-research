#!/usr/bin/env python3
"""Audit XACM v1 compact manifest against its source JSON."""
import argparse,json,struct,hashlib
FAMILIES=("CPS1","CPS2","IGS","NEOGEO")
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("json"); ap.add_argument("xacm"); a=ap.parse_args()
    j=json.load(open(a.json,encoding="utf-8")); b=open(a.xacm,"rb").read()
    magic,ver,nfam,ndrv,nrom,nstr,fw=struct.unpack_from("<4sHHIII32s",b,0)
    assert magic==b"XACM" and ver==1 and nfam==4
    assert fw.hex()==j["firmware_sha256"]
    off=52; fam=[struct.unpack_from("<III",b,off+i*12) for i in range(nfam)]; off+=nfam*12
    drv=[struct.unpack_from("<IIIIHBB",b,off+i*20) for i in range(ndrv)]; off+=ndrv*20
    rom=[struct.unpack_from("<IIII",b,off+i*16) for i in range(nrom)]; off+=nrom*16
    pool=b[off:]
    assert len(pool)==nstr
    def s(o):
        if not o:return None
        e=pool.index(0,o); return pool[o:e].decode("ascii")
    for i,(no,first,count) in enumerate(fam):
        assert s(no)==FAMILIES[i] and first+count<=ndrv
    src=sorted(j["drivers"],key=lambda d:(FAMILIES.index(d["family"]),d["name"]))
    assert len(src)==ndrv
    for d,row in zip(src,drv):
        no,po,bo,first,count,fi,res=row
        assert res==0 and FAMILIES[fi]==d["family"]
        assert (s(no),s(po),s(bo))==(d["name"],d.get("parent"),d.get("board"))
        assert count==len(d["roms"]) and first+count<=nrom
        for rr,x in zip(rom[first:first+count],d["roms"]):
            rn,size,crc,typ=rr
            assert (s(rn),size,crc,typ)==(x["name"],x["size"],x["crc"],x["type"])
    print(f"PASS drivers={ndrv} roms={nrom} bytes={len(b)} sha256={hashlib.sha256(b).hexdigest()}")
if __name__=="__main__":main()
