#!/usr/bin/env python3
"""Validate one imported Arcade ZIP against an XGO generated manifest."""
import argparse,json,zipfile

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("manifest"); ap.add_argument("family")
    ap.add_argument("stem"); ap.add_argument("zip")
    a=ap.parse_args()
    m=json.load(open(a.manifest,encoding="utf-8"))
    d=next((x for x in m["drivers"] if x["family"]==a.family and x["name"]==a.stem),None)
    if d is None:
        print("UNSUPPORTED: no compiled XGO driver for family+stem"); raise SystemExit(2)
    with zipfile.ZipFile(a.zip) as z:
        ents=[(x.filename.rsplit("/",1)[-1].lower(),x.file_size,x.CRC)
              for x in z.infolist() if not x.is_dir()]
    missing=[]; size_bad=[]
    for r in d["roms"]:
        if not r["type"] or not r["size"] or not r["crc"] or r["optional"]: continue
        bycrc=next((e for e in ents if e[2]==r["crc"]),None)
        if bycrc:
            if bycrc[1]!=r["size"]: size_bad.append((r["name"],bycrc[1],r["size"]))
            continue
        # Mirrors stock wrong-CRC filename fallback.
        if any(e[0]==r["name"].lower() for e in ents): continue
        missing.append(r["name"])
    if missing or size_bad:
        print(f"INCOMPATIBLE missing={len(missing)} size_bad={len(size_bad)}")
        for x in missing: print(" missing",x)
        for x in size_bad: print(" size",x)
        raise SystemExit(1)
    print("COMPATIBLE")

if __name__=="__main__":
    main()
