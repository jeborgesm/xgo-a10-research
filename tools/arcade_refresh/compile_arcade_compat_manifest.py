#!/usr/bin/env python3
"""Compile verbose XGO Arcade compatibility JSON into a compact binary manifest.

Format XACM v1 is intentionally simple and deterministic:
 header: magic[4], version u16, family_count u16, driver_count u32,
         rom_count u32, string_bytes u32, firmware_sha256[32]
 family table: 4 x {name_off u32, first_driver u32, driver_count u32}
 driver table: {name_off,parent_off,board_off,first_rom u32; rom_count u16;
                family u8; reserved u8} = 20 bytes
 ROM table: {name_off,size,crc,type u32} = 16 bytes
 strings: NUL-terminated ASCII, deduplicated. Offset 0 means NULL.
"""
import argparse,hashlib,json,struct
MAGIC=b"XACM"; VERSION=1
FAMILIES=("CPS1","CPS2","IGS","NEOGEO")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("json_manifest"); ap.add_argument("output")
    a=ap.parse_args()
    m=json.load(open(a.json_manifest,encoding="utf-8"))
    fw=bytes.fromhex(m["firmware_sha256"])
    if len(fw)!=32: raise SystemExit("bad firmware SHA")

    drivers=sorted(m["drivers"],key=lambda d:(FAMILIES.index(d["family"]),d["name"]))
    expected={"CPS1":154,"CPS2":232,"IGS":34,"NEOGEO":258}
    got={f:sum(d["family"]==f for d in drivers) for f in FAMILIES}
    if got!=expected: raise SystemExit(f"population mismatch {got}")

    pool=bytearray(b"\0"); offsets={"":0}
    def soff(s):
        if not s:return 0
        if s in offsets:return offsets[s]
        try: raw=s.encode("ascii")+b"\0"
        except UnicodeEncodeError: raise SystemExit(f"non-ASCII manifest string {s!r}")
        offsets[s]=len(pool); pool.extend(raw); return offsets[s]

    family_rows=[]; driver_rows=[]; rom_rows=[]
    pos=0
    for fi,f in enumerate(FAMILIES):
        ds=[d for d in drivers if d["family"]==f]
        family_rows.append((soff(f),pos,len(ds)))
        for d in ds:
            first=len(rom_rows)
            for r in d["roms"]:
                rom_rows.append((soff(r["name"]),r["size"],r["crc"],r["type"]))
            driver_rows.append((soff(d["name"]),soff(d.get("parent")),
                                soff(d.get("board")),first,len(d["roms"]),fi,0))
            pos+=1

    head=struct.pack("<4sHHIII32s",MAGIC,VERSION,len(FAMILIES),
                     len(driver_rows),len(rom_rows),len(pool),fw)
    fam=b"".join(struct.pack("<III",*x) for x in family_rows)
    drv=b"".join(struct.pack("<IIIIHBB",*x) for x in driver_rows)
    rom=b"".join(struct.pack("<IIII",*x) for x in rom_rows)
    raw=head+fam+drv+rom+pool
    open(a.output,"wb").write(raw)
    print(f"drivers={len(driver_rows)} roms={len(rom_rows)} strings={len(pool)}")
    print(f"bytes={len(raw)} sha256={hashlib.sha256(raw).hexdigest()}")

if __name__=="__main__":main()
