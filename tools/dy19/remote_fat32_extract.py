#!/usr/bin/env python3
import argparse, os, struct, sys, json, requests
from functools import lru_cache

class RemoteImage:
    def __init__(self,url):
        self.url=url
        self.s=requests.Session()
    @lru_cache(maxsize=4096)
    def read(self,offset,length):
        r=self.s.get(self.url,headers={"Range":f"bytes={offset}-{offset+length-1}"},timeout=60)
        if r.status_code not in (200,206):
            raise RuntimeError(f"HTTP {r.status_code} for range {offset}+{length}")
        data=r.content
        if r.status_code==200 and len(data)>length:
            data=data[offset:offset+length]
        if len(data)!=length:
            raise RuntimeError(f"short read {len(data)} != {length} at {offset}")
        return data

class FAT32:
    def __init__(self,img):
        self.img=img
        mbr=img.read(0,512)
        if mbr[510:512]!=b'\x55\xaa': raise RuntimeError("bad MBR signature")
        parts=[]
        for i in range(4):
            e=mbr[446+i*16:462+i*16]
            ptype=e[4]; start=struct.unpack_from("<I",e,8)[0]; sectors=struct.unpack_from("<I",e,12)[0]
            if ptype and sectors: parts.append((ptype,start,sectors))
        if not parts: raise RuntimeError("no MBR partitions")
        ptype,self.pstart,self.psectors=parts[0]
        self.base=self.pstart*512
        b=img.read(self.base,512)
        self.bps=struct.unpack_from("<H",b,11)[0]
        self.spc=b[13]
        self.res=struct.unpack_from("<H",b,14)[0]
        self.nfat=b[16]
        self.fatsz=struct.unpack_from("<I",b,36)[0]
        self.root=struct.unpack_from("<I",b,44)[0]
        self.fat_off=self.base+self.res*self.bps
        self.data_off=self.base+(self.res+self.nfat*self.fatsz)*self.bps
        self.cluster_size=self.bps*self.spc
        print(json.dumps({"partition_type":hex(ptype),"partition_start_sector":self.pstart,
          "partition_sectors":self.psectors,"bytes_per_sector":self.bps,"sectors_per_cluster":self.spc,
          "reserved":self.res,"num_fats":self.nfat,"fat_size_sectors":self.fatsz,
          "root_cluster":self.root,"cluster_size":self.cluster_size},indent=2))
    def cloff(self,c): return self.data_off+(c-2)*self.cluster_size
    @lru_cache(maxsize=8192)
    def fat(self,c):
        raw=self.img.read(self.fat_off+c*4,4)
        return struct.unpack("<I",raw)[0] & 0x0fffffff
    def chain(self,c):
        seen=set()
        while 2<=c<0x0ffffff8:
            if c in seen: raise RuntimeError("FAT loop")
            seen.add(c); yield c; c=self.fat(c)
    def read_chain(self,c,size=None):
        chunks=[]
        remain=size
        for cl in self.chain(c):
            d=self.img.read(self.cloff(cl),self.cluster_size)
            if remain is not None:
                d=d[:remain]; remain-=len(d)
            chunks.append(d)
            if remain is not None and remain<=0: break
        return b''.join(chunks)
    @staticmethod
    def lfn_piece(e):
        raw=e[1:11]+e[14:26]+e[28:32]
        try: return raw.decode("utf-16le").rstrip("\x00\uffff")
        except: return ""
    def entries(self,c):
        data=self.read_chain(c)
        lfn=[]
        out=[]
        for off in range(0,len(data),32):
            e=data[off:off+32]
            if len(e)<32 or e[0]==0x00: break
            if e[0]==0xe5: lfn=[]; continue
            attr=e[11]
            if attr==0x0f:
                lfn.append((e[0]&0x1f,self.lfn_piece(e))); continue
            if attr & 0x08: lfn=[]; continue
            short=(e[0:8].decode("ascii","replace").rstrip()+"."+e[8:11].decode("ascii","replace").rstrip()).rstrip(".")
            name=''.join(x[1] for x in sorted(lfn,reverse=True)) if lfn else short
            lfn=[]
            hi=struct.unpack_from("<H",e,20)[0]; lo=struct.unpack_from("<H",e,26)[0]
            cl=(hi<<16)|lo; size=struct.unpack_from("<I",e,28)[0]
            out.append({"name":name,"short":short,"attr":attr,"cluster":cl,"size":size,"dir":bool(attr&0x10)})
        return out
    def find(self,path):
        parts=[p for p in path.replace("\\","/").split("/") if p]
        cur={"name":"/","cluster":self.root,"dir":True}
        for part in parts:
            matches=[e for e in self.entries(cur["cluster"]) if e["name"].lower()==part.lower() or e["short"].lower()==part.lower()]
            if not matches: raise FileNotFoundError(path)
            cur=matches[0]
        return cur
    def listdir(self,path=""):
        e=self.find(path) if path else {"cluster":self.root}
        return self.entries(e["cluster"])
    def extract(self,path,out):
        e=self.find(path)
        if e["dir"]: raise IsADirectoryError(path)
        data=self.read_chain(e["cluster"],e["size"])
        os.makedirs(os.path.dirname(out) or ".",exist_ok=True)
        open(out,"wb").write(data)
        return e

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("url"); ap.add_argument("--out",default="out")
    args=ap.parse_args()
    fs=FAT32(RemoteImage(args.url))
    for p in ["","bios","Resources","FC","SFC","ARCADE"]:
        try:
            es=fs.listdir(p)
            print(f"\n## {p or '/'} ({len(es)} entries)")
            for e in es[:500]: print(json.dumps(e,ensure_ascii=False))
        except Exception as ex: print(f"LIST {p}: {ex}")
    targets=["bios/bisrv.asd","Resources/Foldername.ini"]
    for p in targets:
        try:
            dest=os.path.join(args.out,p.replace("/","__"))
            e=fs.extract(p,dest); print("EXTRACTED",p,dest,e["size"])
        except Exception as ex: print("EXTRACT",p,ex)
    # Extract small root/bios/resources metadata files only (<= 2 MiB), avoiding ROM/media payloads.
    for d in ["","bios","Resources"]:
        try:
            for e in fs.listdir(d):
                if e["dir"] or e["size"]>2*1024*1024: continue
                p=(d+"/"+e["name"]).strip("/")
                if p in targets: continue
                try:
                    dest=os.path.join(args.out,p.replace("/","__"))
                    fs.extract(p,dest); print("EXTRACTED",p,dest,e["size"])
                except Exception as ex: print("SKIP",p,ex)
        except Exception as ex: print("SCAN",d,ex)
if __name__=="__main__": main()
