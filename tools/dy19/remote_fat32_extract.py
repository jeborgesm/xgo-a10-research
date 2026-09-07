#!/usr/bin/env python3
import argparse, os, struct, json, requests
from functools import lru_cache

class RemoteImage:
    def __init__(self,url):
        self.url=url
        self.s=requests.Session()
    @lru_cache(maxsize=2048)
    def read(self,offset,length):
        r=self.s.get(self.url,headers={"Range":f"bytes={offset}-{offset+length-1}"},timeout=60)
        if r.status_code != 206:
            raise RuntimeError(f"HTTP {r.status_code} for range {offset}+{length}")
        if len(r.content)!=length:
            raise RuntimeError(f"short read {len(r.content)} != {length} at {offset}")
        return r.content

class FAT32:
    def __init__(self,img):
        self.img=img
        mbr=img.read(0,512)
        if mbr[510:512]!=b'\x55\xaa': raise RuntimeError("bad MBR signature")
        e=mbr[446:462]
        self.ptype=e[4]
        self.pstart=struct.unpack_from("<I",e,8)[0]
        self.psectors=struct.unpack_from("<I",e,12)[0]
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
        print(json.dumps({"partition_type":hex(self.ptype),"partition_start_sector":self.pstart,
          "partition_sectors":self.psectors,"bytes_per_sector":self.bps,"sectors_per_cluster":self.spc,
          "reserved":self.res,"num_fats":self.nfat,"fat_size_sectors":self.fatsz,
          "root_cluster":self.root,"cluster_size":self.cluster_size},indent=2))
    def cloff(self,c): return self.data_off+(c-2)*self.cluster_size
    @lru_cache(maxsize=512)
    def fat_block(self,block):
        # 32 KiB cache block = 8192 FAT32 entries.
        return self.img.read(self.fat_off+block*32768,32768)
    def fat(self,c):
        off=c*4
        block=off//32768
        inner=off%32768
        raw=self.fat_block(block)[inner:inner+4]
        return struct.unpack("<I",raw)[0] & 0x0fffffff
    def chain(self,c):
        seen=set()
        while 2<=c<0x0ffffff8:
            if c in seen: raise RuntimeError("FAT loop")
            seen.add(c); yield c; c=self.fat(c)
    def read_clusters(self,clusters,size=None):
        out=[]
        clusters=list(clusters)
        i=0
        remaining=size
        while i<len(clusters):
            j=i+1
            while j<len(clusters) and clusters[j]==clusters[j-1]+1:
                j+=1
            count=j-i
            blob=self.img.read(self.cloff(clusters[i]),count*self.cluster_size)
            if remaining is not None:
                blob=blob[:remaining]
                remaining-=len(blob)
            out.append(blob)
            if remaining is not None and remaining<=0: break
            i=j
        return b''.join(out)
    def read_chain(self,c,size=None):
        return self.read_clusters(self.chain(c),size)
    @staticmethod
    def lfn_piece(e):
        raw=e[1:11]+e[14:26]+e[28:32]
        return raw.decode("utf-16le","ignore").rstrip("\x00\uffff")
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
            # LFN entries appear in reverse sequence before the short entry.
            name=''.join(piece for _,piece in sorted(lfn,key=lambda x:x[0])) if lfn else short
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
    for p in ["","BIOS","Resources"]:
        es=fs.listdir(p)
        print(f"\n## {p or '/'} ({len(es)} entries)")
        for e in es: print(json.dumps(e,ensure_ascii=False))
    targets=["BIOS/bisrv.asd"]
    # Preserve all small BIOS files and Resources metadata/configuration files.
    for d in ["BIOS","Resources"]:
        for e in fs.listdir(d):
            if e["dir"]: continue
            p=d+"/"+e["name"]
            if p.lower()=="bios/bisrv.asd" or e["size"]<=2*1024*1024:
                dest=os.path.join(args.out,p.replace("/","__"))
                try:
                    info=fs.extract(p,dest)
                    print("EXTRACTED",p,dest,info["size"])
                except Exception as ex:
                    print("FAILED",p,repr(ex))
    # Try conventional folder-name metadata if not already covered.
    for p in ["Resources/Foldername.ini"]:
        try:
            dest=os.path.join(args.out,p.replace("/","__"))
            if not os.path.exists(dest):
                info=fs.extract(p,dest); print("EXTRACTED",p,dest,info["size"])
        except Exception as ex: print("OPTIONAL",p,repr(ex))
if __name__=="__main__": main()
